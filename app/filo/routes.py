from app.filo import filo_bp
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from sqlalchemy.orm import joinedload, subqueryload
from sqlalchemy import or_, and_
from datetime import datetime, date, timedelta
from flask_login import current_user

# Servisler ve Doğrulama
from app.services.filo_services import EkipmanService, BakimService
from app.services.ekipman_rapor_services import EkipmanRaporuService
from app.services.base import ValidationError

# Modeller
from app.filo.models import Ekipman, BakimKaydi
from app.kiralama.models import Kiralama, KiralamaKalemi
from app.subeler.models import Sube

# Formlar
from app.filo.forms import EkipmanForm 
import locale

# Türkçe yerel ayarlarını dene
try:
    locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
except:
    pass

# --- GÜVENLİK YARDIMCISI ---
def get_actor_id():
    """Kullanıcı giriş sistemi aktifse işlemi yapanın ID'sini alır."""
    if hasattr(current_app, 'login_manager'):
        try:
            if current_user.is_authenticated:
                return current_user.id
        except Exception:
            pass
    return None

# -------------------------------------------------------------------------
# 1. Makine Parkı Listeleme (Sadece Aktifler)
# -------------------------------------------------------------------------
@filo_bp.route('/')
@filo_bp.route('/index')
def index():
    try:
        page = request.args.get('page', 1, type=int)
        q = request.args.get('q', '', type=str)
        
        # SADECE AKTİF VE BİZİM OLANLAR
        base_query = Ekipman.query.filter(
            and_(
                Ekipman.firma_tedarikci_id.is_(None),
                Ekipman.is_active == True 
            )
        ).options(
            joinedload(Ekipman.sube),
            subqueryload(Ekipman.kiralama_kalemleri).options(
                joinedload(KiralamaKalemi.kiralama).joinedload(Kiralama.firma_musteri)
            )
        )
        
        if q:
            search_term = f'%{q}%'
            base_query = base_query.filter(
                or_(
                    Ekipman.kod.ilike(search_term),
                    Ekipman.tipi.ilike(search_term),
                    Ekipman.seri_no.ilike(search_term),
                    Ekipman.marka.ilike
                    
                )
            )
        
        pagination = base_query.order_by(Ekipman.kod).paginate(
            page=page, per_page=25, error_out=False
        )
        ekipmanlar = pagination.items
        
        for ekipman in ekipmanlar:
            ekipman.aktif_kiralama_bilgisi = None 
            if ekipman.calisma_durumu == 'kirada':
                aktif_kalemler = [k for k in ekipman.kiralama_kalemleri if not k.sonlandirildi]
                if aktif_kalemler:
                    ekipman.aktif_kiralama_bilgisi = max(aktif_kalemler, key=lambda k: k.id)
        
        subeler = Sube.query.all()
    
    except Exception as e:
        flash(f"Hata: {str(e)}", "danger")
        ekipmanlar = []
        pagination = None
        subeler = []

    return render_template('filo/index.html', ekipmanlar=ekipmanlar, pagination=pagination, q=q, subeler=subeler)

# -------------------------------------------------------------------------
# 2. Yeni Makine Ekleme
# -------------------------------------------------------------------------
@filo_bp.route('/ekle', methods=['GET', 'POST'])
def ekle():
    form = EkipmanForm()
    form.sube_id.choices = [(s.id, s.isim) for s in Sube.query.all()]
    
    try:
        son_ekipman = Ekipman.query.filter(Ekipman.firma_tedarikci_id.is_(None)).order_by(Ekipman.kod.desc()).first()
        son_kod = son_ekipman.kod if son_ekipman else 'Henüz kayıt yok'
    except:
        son_kod = '...'

    if form.validate_on_submit():
        try:
            # Kullanıcı dostu özel arşiv uyarılarını koruyoruz (Servisten önce formda yakalıyoruz)
            mevcut_makine = Ekipman.query.filter_by(kod=form.kod.data).first()
            if mevcut_makine:
                durum = "zaten listenizde" if mevcut_makine.is_active else "ARŞİVDE (Pasif Durumda)"
                flash(f"HATA: '{form.kod.data}' kodlu makine {durum} mevcut.", "warning" if not mevcut_makine.is_active else "danger")
                return render_template('filo/ekle.html', form=form, son_kod=son_kod)
            
            mevcut_seri = Ekipman.query.filter_by(seri_no=form.seri_no.data, firma_tedarikci_id=None).first()
            if mevcut_seri:
                durum = f"zaten mevcut (Kod: {mevcut_seri.kod})" if mevcut_seri.is_active else "ARŞİVDE mevcut"
                flash(f"HATA: '{form.seri_no.data}' seri numaralı bir makine {durum}!", "warning" if not mevcut_seri.is_active else "danger")
                return render_template('filo/ekle.html', form=form, son_kod=son_kod)

            # BaseForm sayesinde temiz veri aktarımı (MoneyField, giris_maliyeti'ni otomatik Decimal yapar)
            data = {k: v for k, v in form.data.items() if k in EkipmanService.updatable_fields}
            data['firma_tedarikci_id'] = None
            data['calisma_durumu'] = 'bosta'
            data['is_active'] = True
            
            yeni_ekipman = Ekipman(**data)
            EkipmanService.save(yeni_ekipman, actor_id=get_actor_id())
            
            flash('Yeni makine başarıyla eklendi!', 'success')
            return redirect(url_for('filo.index'))
            
        except ValidationError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Kayıt hatası: {str(e)}", "danger")
    
    return render_template('filo/ekipman_form.html', form=form, son_kod=son_kod,is_edit=False)
    
# -------------------------------------------------------------------------
# 3. Makine Bilgilerini Düzelt
# -------------------------------------------------------------------------
@filo_bp.route('/duzelt/<int:id>', methods=['GET', 'POST'])
def duzelt(id):
    ekipman = EkipmanService.get_by_id(id)
    if not ekipman or not ekipman.is_active or ekipman.firma_tedarikci_id is not None:
        flash("Geçerli bir makine bulunamadı.", "danger")
        return redirect(url_for('filo.index'))
        
    # obj=ekipman dendiğinde MoneyField sayesinde giris_maliyeti otomatik formatlanır!
    form = EkipmanForm(obj=ekipman)
    form.sube_id.choices = [(s.id, s.isim) for s in Sube.query.all()]

    if form.validate_on_submit():
        try:
            data = {k: v for k, v in form.data.items() if k in EkipmanService.updatable_fields}
            
            # Şube ve Durum Güncelleme Koruması
            if ekipman.calisma_durumu == 'kirada':
                # Kiradaki makinenin şubesi ve durumu formdan değiştirilemez
                data.pop('sube_id', None)
                data.pop('calisma_durumu', None)
            else:
                data['calisma_durumu'] = 'bosta'

            EkipmanService.update(id, data, actor_id=get_actor_id())
            
            flash('Makine bilgileri güncellendi!', 'success')
            return redirect(url_for('filo.index', page=request.args.get('page', 1, type=int), q=request.args.get('q', '')))
            
        except ValidationError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Hata: {str(e)}", "danger")

    return render_template('filo/ekipman_form.html', form=form, ekipman=ekipman, subeler=Sube.query.all(), is_edit=True)

# -------------------------------------------------------------------------
# 4. Şube Nakil Merkezi (Modal Hızlı Transfer)
# -------------------------------------------------------------------------
@filo_bp.route('/sube_degistir/<int:id>', methods=['POST'])
def sube_degistir(id):
    try:
        yeni_sube_id = request.form.get('yeni_sube_id', type=int)
        if not yeni_sube_id:
            flash("Uyarı: Lütfen geçerli bir şube seçin.", "warning")
            return redirect(request.referrer or url_for('filo.index'))
            
        EkipmanService.sube_transfer(id, yeni_sube_id, actor_id=get_actor_id())
        flash(f"Nakil Başarılı! Makine yeni deposuna aktarıldı.", "success")
    except ValidationError as e:
        flash(f"Hata: {str(e)}", "danger")
    except Exception as e:
        flash(f"Nakil hatası: {str(e)}", "danger")
        
    return redirect(request.referrer or url_for('filo.index'))

# -------------------------------------------------------------------------
# 5. Makine Bilgi ve Geçmişi
# -------------------------------------------------------------------------
@filo_bp.route('/bilgi/<int:id>', methods=['GET'])
def bilgi(id):
    ekipman = Ekipman.query.filter(
        Ekipman.id == id,
        Ekipman.firma_tedarikci_id.is_(None) 
    ).options(
        subqueryload(Ekipman.kiralama_kalemleri).options(
            joinedload(KiralamaKalemi.kiralama).joinedload(Kiralama.firma_musteri)
        )
    ).first_or_404()
    
    kalemler = sorted(ekipman.kiralama_kalemleri, key=lambda k: k.id, reverse=True)
    referrer = request.referrer or url_for('filo.index')
    return render_template('filo/bilgi.html', ekipman=ekipman, kalemler=kalemler, referrer=referrer)

# -------------------------------------------------------------------------
# 6. Kiralama Sonlandırma (İnce Tarih Kontrolü ve Şube Ataması)
# -------------------------------------------------------------------------
@filo_bp.route('/sonlandir', methods=['POST'])
def sonlandir():
    try:
        ekipman_id = request.form.get('ekipman_id', type=int)
        bitis_tarihi_str = request.form.get('bitis_tarihi') 
        donus_sube_id = request.form.get('donus_sube_id', type=int)
        
        if not (ekipman_id and bitis_tarihi_str and donus_sube_id):
            flash('Eksik bilgi! Lütfen tarih ve dönüş şubesini seçiniz.', 'danger')
            return redirect(url_for('filo.index'))

        EkipmanService.kiralama_sonlandir(ekipman_id, bitis_tarihi_str, donus_sube_id, actor_id=get_actor_id())
        flash(f"Kiralama sonlandırıldı. Makine depoya iade alındı.", 'success')

    except ValidationError as e:
        flash(f"Hata: {str(e)}", 'danger')
    except Exception as e:
        flash(f"Sistem Hatası: {str(e)}", 'danger')
        
    return redirect(url_for('filo.index', page=request.args.get('page', 1, type=int), q=request.args.get('q', '')))

# -------------------------------------------------------------------------
# 7. Bakım ve Servis İşlemleri
# -------------------------------------------------------------------------
@filo_bp.route('/bakimda')
def bakimda():
    try:
        page = request.args.get('page', 1, type=int)
        q = request.args.get('q', '', type=str)
        
        base_query = Ekipman.query.filter(
            Ekipman.firma_tedarikci_id.is_(None),
            Ekipman.is_active == True,
            Ekipman.calisma_durumu == 'serviste'
        )
        
        if q:
            base_query = base_query.filter(Ekipman.kod.ilike(f'%{q}%'))
            
        pagination = base_query.order_by(Ekipman.kod).paginate(page=page, per_page=25, error_out=False)
        return render_template('filo/bakimda.html', ekipmanlar=pagination.items, pagination=pagination, q=q)
    except Exception as e:
        flash(f"Hata: {str(e)}", "danger")
        return render_template('filo/bakimda.html', ekipmanlar=[], pagination=None, q='')

@filo_bp.route('/bakima_al', methods=['POST'])
def bakima_al():
    try:
        ekipman_id = request.form.get('ekipman_id', type=int)
        tarih = request.form.get('tarih')
        aciklama = request.form.get('aciklama')
        
        if not (ekipman_id and tarih):
            flash('Eksik bilgi! Lütfen tarih seçiniz.', 'danger')
            return redirect(url_for('filo.index'))

        bakim_verileri = {
            'tarih': tarih,
            'aciklama': aciklama or "Listeden servise alındı.",
            'calisma_saati': 0
        }
        
        EkipmanService.update(ekipman_id, {'calisma_durumu': 'serviste'}, actor_id=get_actor_id())
        BakimService.bakim_kaydet(ekipman_id, bakim_verileri, actor_id=get_actor_id())
        
        flash("Makine başarıyla bakıma alındı.", 'success')
    except ValidationError as e:
        flash(f"Uyarı: {str(e)}", 'warning')
    except Exception as e:
        flash(f"Hata: {str(e)}", 'danger')
        
    return redirect(url_for('filo.index'))

@filo_bp.route('/bakim_bitir/<int:id>', methods=['POST'])
def bakim_bitir(id):
    try:
        ekipman = EkipmanService.get_by_id(id)
        if ekipman and ekipman.calisma_durumu == 'serviste':
            EkipmanService.update(id, {'calisma_durumu': 'bosta'}, actor_id=get_actor_id())
            flash(f"'{ekipman.kod}' servisten çıkarıldı.", "success")
    except ValidationError as e:
        flash(str(e), "danger")
    return redirect(url_for('filo.bakimda'))

# -------------------------------------------------------------------------
# 8. Arşiv, Silme ve Harici Makineler
# -------------------------------------------------------------------------
@filo_bp.route('/sil/<int:id>', methods=['POST'])
def sil(id):
    try:
        EkipmanService.delete(id, actor_id=get_actor_id())
        flash('Makine arşive kaldırıldı.', 'success')
    except ValidationError as e:
        flash(str(e), 'danger')
    return redirect(url_for('filo.index'))

@filo_bp.route('/arsiv')
def arsiv():
    ekipmanlar = EkipmanService.find_by(is_active=False, firma_tedarikci_id=None)
    return render_template('filo/arsiv.html', ekipmanlar=ekipmanlar)

@filo_bp.route('/geri_yukle/<int:id>', methods=['POST'])
def geri_yukle(id):
    try:
        EkipmanService.update(id, {'is_active': True}, actor_id=get_actor_id())
        flash("Makine geri yüklendi.", "success")
    except ValidationError as e:
        flash(str(e), "danger")
    return redirect(url_for('filo.arsiv'))

@filo_bp.route('/harici')
def harici():
    ekipmanlar = Ekipman.query.filter(Ekipman.firma_tedarikci_id.isnot(None), Ekipman.is_active == True).all()
    return render_template('filo/harici.html', ekipmanlar=ekipmanlar)


# -------------------------------------------------------------------------
# 9. Finansal Raporlama - Makine ROI ve Amorti Analizi
# -------------------------------------------------------------------------
@filo_bp.route('/finansal_rapor/<int:ekipman_id>', methods=['GET', 'POST'])
def finansal_rapor(ekipman_id):
    """
    Makinenin finansal analizini gösterir:
    - Başlangıç maliyeti
    - Kiralama gelirleri (dönem bazında)
    - Servis masrafları
    - ROI ve amorti durumu
    """
    ekipman = Ekipman.query.get_or_404(ekipman_id)
    
    # Form'dan tarih aralığı al veya varsayılan değerler kullan
    start_date = None
    end_date = date.today()
    
    if request.method == 'POST':
        start_str = request.form.get('start_date')
        end_str = request.form.get('end_date')
        
        if start_str:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
        if end_str:
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
    else:
        # Ilk ziyarette: Makinenin satın alındığı tarihten itibaren
        if ekipman.created_at:
            start_date = ekipman.created_at.date()
    
    # Finansal analiz hesapla
    ozet = EkipmanRaporuService.get_finansal_ozet(ekipman_id, start_date, end_date)
    
    # Kiralama detayları (tablo için)
    kiralama_detaylari = EkipmanRaporuService.get_kiralama_detaylari(ekipman_id, start_date, end_date)
    
    # Durum etiketi (Türkçe)
    durum_etiketleri = {
        'amorti_olmadi_zarar': 'Henüz Amorti Olmadı (Zarar)',
        'amorti_surecinde': 'Amorti Süreci İçinde',
        'amorti_oldu': 'Kendini Amorti Etti',
        'kar_asamasi': 'Kâr Aşamasında'
    }
    
    ozet['durum_etiket'] = durum_etiketleri.get(ozet['durum'], ozet['durum'])
    
    return render_template(
        'filo/finansal_rapor.html',
        ekipman=ekipman,
        ozet=ozet,
        kiralama_detaylari=kiralama_detaylari,
        start_date=start_date,
        end_date=end_date
    )


@filo_bp.route('/finansal_rapor_api/<int:ekipman_id>')
def finansal_rapor_api(ekipman_id):
    """
    Finansal rapor verilerini JSON formatında döner (grafik oluşturma için)
    """
    ekipman = Ekipman.query.get(ekipman_id)
    if not ekipman:
        return jsonify({'error': 'Makine bulunamadı'}), 404
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    ozet = EkipmanRaporuService.get_finansal_ozet(ekipman_id, start_date, end_date)
    
    return jsonify(ozet)


# -------------------------------------------------------------------------
# 10. Kiralama Geçmişi (Detaylı Tablo)
# -------------------------------------------------------------------------
@filo_bp.route('/kiralama_gecmisi/<int:ekipman_id>', methods=['GET', 'POST'])
def kiralama_gecmisi(ekipman_id):
    """
    Makinenin tüm kiralama geçmişini gösterir:
    - Her kiralama kalemi için TRY, USD, EUR cinsinden gelir
    - Döviz kuru bilgileri
    - Toplam satırlar
    """
    ekipman = Ekipman.query.get_or_404(ekipman_id)
    
    # Form'dan tarih aralığı al veya varsayılan değerler kullan
    start_date = None
    end_date = date.today()
    
    if request.method == 'POST':
        start_str = request.form.get('start_date')
        end_str = request.form.get('end_date')
        
        if start_str:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
        if end_str:
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
    else:
        # Ilk ziyarette: Makinenin satın alındığı tarihten itibaren
        if ekipman.created_at:
            start_date = ekipman.created_at.date()
    
    # Kiralama detayları al
    kiralama_detaylari = EkipmanRaporuService.get_kiralama_detaylari(ekipman_id, start_date, end_date)
    
    # Totalleri hesapla
    total_gun = sum(d['gun_sayisi'] for d in kiralama_detaylari)
    total_try = sum(d['gelir_try'] for d in kiralama_detaylari)
    total_usd = sum(d['gelir_usd'] for d in kiralama_detaylari)
    total_eur = sum(d['gelir_eur'] for d in kiralama_detaylari)
    
    # Referrer URL'ini al (form'dan veya request header'dan)
    referrer = request.form.get('referrer') or request.referrer or url_for('filo.index')
    
    return render_template(
        'filo/kiralama_gecmisi.html',
        ekipman=ekipman,
        kiralama_detaylari=kiralama_detaylari,
        total_gun=total_gun,
        total_try=total_try,
        total_usd=total_usd,
        total_eur=total_eur,
        start_date=start_date,
        end_date=end_date,
        referrer=referrer
    )