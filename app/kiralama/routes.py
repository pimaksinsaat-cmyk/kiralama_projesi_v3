import traceback
import threading
from datetime import datetime, date, timedelta
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import current_user, login_required
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from app import db
from app.kiralama import kiralama_bp

# Modeller
from app.firmalar.models import Firma
from app.kiralama.models import Kiralama, KiralamaKalemi
from app.filo.models import Ekipman
from app.subeler.models import Sube
from app.araclar.models import Arac as NakliyeAraci
from app.kiralama.forms import KiralamaForm

# Servis Katmanı ve Hata Yönetimi
from app.services.kiralama_services import KiralamaService, KiralamaKalemiService
from app.services.base import ValidationError

# --- BELLEK İÇİ ÖNBELLEKLEME (IN-MEMORY CACHE) ---
_CACHE_DATA = {
    'subeler': {'data': None, 'last_update': None},
    'aktif_araclar': {'data': None, 'last_update': None}
}

# DARBOĞAZ ÖNLEME: Her veri kümesi için ayrı kilit (lock) tanımlandı.
# Böylece şube güncellenirken araç listesi etkilenmez.
_SUBE_CACHE_LOCK = threading.Lock()
_ARAC_CACHE_LOCK = threading.Lock()

_CACHE_TIMEOUT_MINUTES = 60 

def get_cached_subeler():
    """Şubeleri thread-safe ve bağımsız bir kilitle bellekten getirir."""
    now = datetime.now()
    cache = _CACHE_DATA['subeler']
    
    # 1. Hızlı Okuma
    if cache['data'] is not None and (now - cache['last_update']) < timedelta(minutes=_CACHE_TIMEOUT_MINUTES):
        return cache['data']

    # 2. Kaynağa Özel Kilit
    with _SUBE_CACHE_LOCK:
        if cache['data'] is None or (datetime.now() - cache['last_update']) > timedelta(minutes=_CACHE_TIMEOUT_MINUTES):
            try:
                cache['data'] = Sube.query.all()
                cache['last_update'] = datetime.now()
            except Exception as e:
                current_app.logger.error(f"Sube Cache Hatası: {e}")
                return cache['data'] or []
    return cache['data']

def get_cached_aktif_araclar():
    """Aktif araçları thread-safe ve bağımsız bir kilitle bellekten getirir."""
    now = datetime.now()
    cache = _CACHE_DATA['aktif_araclar']
    
    if cache['data'] is not None and (now - cache['last_update']) < timedelta(minutes=_CACHE_TIMEOUT_MINUTES):
        return cache['data']

    with _ARAC_CACHE_LOCK:
        if cache['data'] is None or (datetime.now() - cache['last_update']) > timedelta(minutes=_CACHE_TIMEOUT_MINUTES):
            try:
                cache['data'] = NakliyeAraci.query.filter_by(is_active=True).all()
                cache['last_update'] = datetime.now()
            except Exception as e:
                current_app.logger.error(f"Arac Cache Hatası: {e}")
                return cache['data'] or []
    return cache['data']

def populate_kiralama_form_choices(form, include_ids=None):
    """
    Formdaki tüm SelectField alanlarını veritabanından dinamik olarak doldurur.
    """
    if include_ids is None: include_ids = []
    
    # 1. Ana Müşteri ve Tedarikçi Listeleri (Dahili firmalar gizlendi)
    musteriler = Firma.query.filter(
        Firma.is_musteri == True, 
        Firma.is_active == True,
        Firma.firma_adi.notin_(['DAHİLİ İŞLEMLER', 'Dahili Kasa İşlemleri'])
    ).order_by(Firma.firma_adi).all()
    form.firma_musteri_id.choices = [(0, '--- Müşteri Seçiniz ---')] + [(f.id, f.firma_adi) for f in musteriler]

    tedarikciler = Firma.query.filter(
        Firma.is_tedarikci == True, 
        Firma.is_active == True,
        Firma.firma_adi.notin_(['DAHİLİ İŞLEMLER', 'Dahili Kasa İşlemleri'])
    ).order_by(Firma.firma_adi).all()
    ted_choices = [(0, '--- Tedarikçi Seçiniz ---')] + [(f.id, f.firma_adi) for f in tedarikciler]
    
    # 2. Makine Parkı (Pimaks Filosu) - Detaylandırılmış Etiketler Eklendi
    filo_query = Ekipman.query.filter(
        Ekipman.firma_tedarikci_id.is_(None),
        or_(Ekipman.calisma_durumu == 'bosta', Ekipman.id.in_(include_ids))
    ).order_by(Ekipman.kod).all()
    
    # KOD | TİP (Yükseklik m - Kapasite kg) formatı uygulandı
    pimaks_choices = [(0, '--- Seçiniz ---')] + [
        (e.id, f"{e.kod} | {e.tipi} ({e.calisma_yuksekligi}m - {e.kaldirma_kapasitesi}kg)") 
        for e in filo_query
    ]

    # 3. Nakliye Araçları (Cache destekli)
    arac_choices = [(0, '--- Araç Seçiniz ---')] + [(a.id, f"{a.plaka} - {a.arac_tipi}") for a in get_cached_aktif_araclar()]

    # 4. Kalemler Listesi Doldurma
    if not form.kalemler.entries:
        form.kalemler.append_entry()

    for entry in form.kalemler:
        f = entry.form
        f.ekipman_id.choices = pimaks_choices
        f.harici_ekipman_tedarikci_id.choices = ted_choices
        f.nakliye_tedarikci_id.choices = ted_choices
        f.nakliye_araci_id.choices = arac_choices

@kiralama_bp.route('/')
@kiralama_bp.route('/index')
@login_required
def index():
    """Kiralama ana listesi ve arama."""
    try:
        page = request.args.get('page', 1, type=int)
        q = request.args.get('q', '', type=str)
        
        query = Kiralama.query.options(
            joinedload(Kiralama.firma_musteri), 
            joinedload(Kiralama.kalemler).joinedload(KiralamaKalemi.ekipman)
        )
        
        if q:
            search = f"%{q}%"
            query = query.join(Firma, Kiralama.firma_musteri_id == Firma.id)\
                         .filter(or_(Kiralama.kiralama_form_no.ilike(search), Firma.firma_adi.ilike(search)))
            
        pagination = query.order_by(Kiralama.id.desc()).paginate(page=page, per_page=20)
        
        return render_template(
            'kiralama/index.html', 
            kiralamalar=pagination.items, 
            pagination=pagination, 
            q=q, 
            kurlar=KiralamaService.get_tcmb_kurlari(),
            today=date.today(),
            subeler=get_cached_subeler(),
            nakliye_araclari=get_cached_aktif_araclar()
        )
    except Exception as e:
        current_app.logger.error(f"Kiralama Liste Yükleme Hatası: {str(e)}")
        flash(f"Liste yüklenirken bir hata oluştu.", "danger")
        return render_template('kiralama/index.html', kiralamalar=[], kurlar={}, today=date.today(), subeler=[])

@kiralama_bp.route('/ekle', methods=['GET', 'POST'])
@login_required
def ekle():
    """Yeni kiralama kaydı oluşturma."""
    form = KiralamaForm()
    
    try:
        populate_kiralama_form_choices(form)
    except Exception as e:
        current_app.logger.error(f"Seçenek doldurma hatası (Ekle): {str(e)}")
        flash("Seçenek listeleri yüklenemedi. Lütfen sistem yöneticisine başvurun.", "danger")
        return redirect(url_for('kiralama.index'))

    # --- TCMB KURU VE FORM NUMARASI OTOMATİK DOLDURMA ---
    if request.method == 'GET':
        try:
            kurlar = KiralamaService.get_tcmb_kurlari()
            form.doviz_kuru_usd.data = kurlar.get('USD', 1.0)
            if hasattr(form, 'doviz_kuru_eur'):
                form.doviz_kuru_eur.data = kurlar.get('EUR', 1.0)
                
            form.kiralama_form_no.data = KiralamaService.get_next_form_no()
        except Exception as e:
            current_app.logger.warning(f"Varsayılan değerler forma basılırken hata: {e}")
    # ----------------------------------------------------

    if form.validate_on_submit():
        try:
            actor_id = getattr(current_user, 'id', None)
            kiralama_data = {
                'kiralama_form_no': form.kiralama_form_no.data,
                'firma_musteri_id': form.firma_musteri_id.data,
                'kdv_orani': form.kdv_orani.data,
                'doviz_kuru_usd': form.doviz_kuru_usd.data,
                'doviz_kuru_eur': getattr(form, 'doviz_kuru_eur', form.doviz_kuru_usd).data
            }
            kalemler_data = [k_form.data for k_form in form.kalemler]

            KiralamaService.create_kiralama_with_relations(kiralama_data, kalemler_data, actor_id=actor_id)
            flash('Kiralama kaydı başarıyla oluşturuldu.', 'success')
            return redirect(url_for('kiralama.index'))
            
        except ValidationError as e:
            flash(f"Doğrulama Hatası: {str(e)}", "warning")
        except Exception as e:
            current_app.logger.error(f"Kiralama Kayıt Hatası: {str(e)}")
            flash(f"Sistemsel bir hata oluştu. Lütfen tekrar deneyin.", "danger")
    
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            if field == 'kalemler':
                for idx, kalem_errors in enumerate(errors):
                    for k_field, k_msg in kalem_errors.items():
                        flash(f"Satır {idx+1} - {k_field}: {k_msg}", "warning")
            else:
                flash(f"{field}: {errors}", "warning")
    subeler = Sube.query.all()
    markalar = [m[0] for m in db.session.query(Ekipman.marka).filter(Ekipman.marka.isnot(None)).distinct().all()]
    tipler = [t[0] for t in db.session.query(Ekipman.tipi).filter(Ekipman.tipi.isnot(None), Ekipman.tipi != '').distinct().all()]
    return render_template('kiralama/ekle.html', form=form,subeler=subeler, markalar=markalar, tipler=tipler, is_edit=False)

@kiralama_bp.route('/duzenle/<int:kiralama_id>', methods=['GET', 'POST'])
@login_required
def duzenle(kiralama_id):
    """Mevcut bir kiralama kaydını düzenleme."""
    kiralama = db.get_or_404(Kiralama, kiralama_id)
    form = KiralamaForm(obj=kiralama)
    
    try:
        include_ids = [k.ekipman_id for k in kiralama.kalemler if k.ekipman_id]
        populate_kiralama_form_choices(form, include_ids=include_ids)
    except Exception as e:
        current_app.logger.error(f"Seçenek doldurma hatası (Düzenle): {str(e)}")
        flash("Form seçenekleri yüklenirken hata oluştu.", "danger")
        return redirect(url_for('kiralama.index'))

    if form.validate_on_submit():
        try:
            actor_id = getattr(current_user, 'id', None)
            kiralama_data = {
                'firma_musteri_id': form.firma_musteri_id.data,
                'kdv_orani': form.kdv_orani.data,
                'doviz_kuru_usd': form.doviz_kuru_usd.data,
                'doviz_kuru_eur': getattr(form, 'doviz_kuru_eur', form.doviz_kuru_usd).data
            }
            kalemler_data = [k_form.data for k_form in form.kalemler]

            KiralamaService.update_kiralama_with_relations(kiralama.id, kiralama_data, kalemler_data, actor_id=actor_id)
            flash('Kiralama başarıyla güncellendi.', 'success')
            return redirect(url_for('kiralama.index'))
        except ValidationError as e:
            flash(f"Hata: {str(e)}", "warning")
        except Exception as e:
            current_app.logger.error(f"Kiralama Güncelleme Hatası (ID: {kiralama_id}): {str(e)}")
            flash(f"Güncelleme sırasında sistemsel bir hata oluştu.", "danger")
    subeler = Sube.query.all()
    markalar = [m[0] for m in db.session.query(Ekipman.marka).filter(Ekipman.marka.isnot(None)).distinct().all()]
    tipler = [t[0] for t in db.session.query(Ekipman.tipi).filter(Ekipman.tipi.isnot(None), Ekipman.tipi != '').distinct().all()]
    return render_template('kiralama/duzelt.html', form=form, kiralama=kiralama,markalar=markalar, subeler=subeler, tipler=tipler, is_edit=True)

@kiralama_bp.route('/sil/<int:kiralama_id>', methods=['POST'])
@login_required
def sil(kiralama_id):
    """Kiralama ve bağlı finansal kayıtları siler."""
    try:
        actor_id = getattr(current_user, 'id', None)
        KiralamaService.delete_with_relations(kiralama_id, actor_id=actor_id)
        flash('Kiralama kaydı ve bağlı tüm hareketler silindi.', 'success')
    except ValidationError as e:
        flash(str(e), "warning")
    except Exception as e:
        current_app.logger.error(f"Kiralama Silme Hatası (ID: {kiralama_id}): {str(e)}")
        flash(f'Silme işlemi başarısız oldu.', 'danger')
    return redirect(url_for('kiralama.index'))

@kiralama_bp.route('/kalem/sonlandir', methods=['POST'])
@login_required
def sonlandir_kalem():
    """Kiralama kalemini kapatır ve makineyi boşa çıkarır."""
    try:
        kalem_id = request.form.get('kalem_id', type=int)
        if not kalem_id:
            flash("İşlem yapılacak kiralama kalemi seçilmedi.", "warning")
            return redirect(url_for('kiralama.index'))

        actor_id = getattr(current_user, 'id', None)
        bitis_str = request.form.get('bitis_tarihi')
        donus_sube_id = request.form.get('donus_sube_id')
        
        KiralamaKalemiService.sonlandir(kalem_id, bitis_str, donus_sube_id, actor_id=actor_id)
        flash("Kiralama başarıyla sonlandırıldı.", "success")
    except ValidationError as e:
        flash(f"Hata: {str(e)}", "warning")
    except Exception as e:
        current_app.logger.error(f"Kalem Sonlandırma Hatası: {str(e)}")
        flash(f"İşlem sırasında bir hata oluştu.", "danger")
    return redirect(url_for('kiralama.index'))

@kiralama_bp.route('/kalem/iptal_et', methods=['POST'])
@login_required
def iptal_et_kalem():
    """Sonlandırma işlemini geri alır."""
    try:
        kalem_id = request.form.get('kalem_id', type=int)
        if not kalem_id:
            flash("Hatalı kalem seçimi.", "warning")
            return redirect(url_for('kiralama.index'))

        actor_id = getattr(current_user, 'id', None)
        KiralamaKalemiService.iptal_et_sonlandirma(kalem_id, actor_id=actor_id)
        flash("İşlem başarıyla geri alındı.", "success")
    except ValidationError as e:
        flash(f"Hata: {str(e)}", "warning")
    except Exception as e:
        current_app.logger.error(f"Sonlandırma İptal Hatası: {str(e)}")
        flash(f"İşlem geri alınamadı.", "danger")
    return redirect(url_for('kiralama.index'))
@kiralama_bp.route('/api/ekipman-filtrele')
def api_ekipman_filtrele():
    try:
        # Sadece bizim olan (Tedarikçi olmayan), aktif ve boşta olan makineler
        query = Ekipman.query.filter_by(is_active=True, firma_tedarikci_id=None, calisma_durumu='bosta')
        
        # Filtreleri yakala
        sube_id = request.args.get('sube_id', type=int)
        tip = request.args.get('tip')
        marka = request.args.get('marka')
        enerji = request.args.get('enerji')
        ortam = request.args.get('ortam')
        
        y_min = request.args.get('y_min', type=float)
        y_max = request.args.get('y_max', type=float)
        k_min = request.args.get('k_min', type=float)
        
        agirlik_max = request.args.get('agirlik_max', type=float)
        genislik_max = request.args.get('genislik_max', type=float)
        ky_max = request.args.get('ky_max', type=float)
        
        # Sorguları uygula
        if sube_id: query = query.filter(Ekipman.sube_id == sube_id)
        if tip: query = query.filter(Ekipman.tipi == tip)
        if marka: query = query.filter(Ekipman.marka == marka)
        if enerji: query = query.filter(Ekipman.yakit == enerji)
        if ortam == 'ic': query = query.filter(Ekipman.ic_mekan_uygun == True)
        
        if y_min: query = query.filter(Ekipman.calisma_yuksekligi >= y_min)
        if y_max: query = query.filter(Ekipman.calisma_yuksekligi <= y_max)
        if k_min: query = query.filter(Ekipman.kaldirma_kapasitesi >= k_min)
        if agirlik_max: query = query.filter(Ekipman.agirlik <= agirlik_max)
        if genislik_max: query = query.filter(Ekipman.genislik <= genislik_max)
        if ky_max: query = query.filter(Ekipman.kapali_yukseklik <= ky_max)
        
        ekipmanlar = query.order_by(Ekipman.kod).all()
        
        data = []
        for e in ekipmanlar:
            # Şube varsa adını, yoksa 'Şubesiz' yazar. Değişken adı temizlendi.
            gecici_sube_adi = e.sube.isim if e.sube else 'Merkez / Şubesiz'
            
            data.append({
                'id': e.id,
                'label': f"{e.kod} | {e.tipi} ({e.calisma_yuksekligi}m) - {gecici_sube_adi}"
            })
            
        return jsonify({
            'success': True,
            'count': len(data),
            'data': data
        })
    except Exception as e:
        # Gerçek hatayı ekrana basması için 'error' anahtarı eklendi
        return jsonify({'success': False, 'error': str(e)}), 500

