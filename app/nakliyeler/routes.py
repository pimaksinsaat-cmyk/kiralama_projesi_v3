from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
from app.extensions import db
from app.nakliyeler import nakliye_bp
from app.nakliyeler.models import Nakliye
from app.nakliyeler.forms import NakliyeForm
from app.services.nakliye_services import CariServis
from app.services.operation_log_service import OperationLogService
from app.firmalar.models import Firma
from app.araclar.models import Arac
from decimal import Decimal, InvalidOperation
from datetime import datetime, date, timedelta

def _actor():
    return current_user.id if current_user.is_authenticated else None

def _uname():
    return getattr(current_user, 'username', None)

# -------------------------------------------------------------------------
# YARDIMCI FONKSİYON: Decimal Hata Çözücü
# -------------------------------------------------------------------------
def to_decimal(value):
    """
    Formlardan veya veritabanından gelen karmaşık sayı formatlarını 
    güvenli bir şekilde Decimal nesnesine çevirir.
    """
    if value is None or value == '':
        return Decimal('0.00')
    if isinstance(value, Decimal):
        return value
    try:
        # Virgüllü formatı (1.250,50) Python'un anlayacağı (1250.50) formatına çevir
        clean_val = str(value).replace('.', '').replace(',', '.')
        return Decimal(clean_val)
    except (InvalidOperation, ValueError):
        return Decimal('0.00')

# ---------------------------------------------------
# 1. NAKLİYE SEFER LİSTESİ (Filtreleme)
# ---------------------------------------------------
@nakliye_bp.route('/')
def index():
    # Filtreleme parametrelerini yakala
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    if per_page not in {10, 25, 50, 100}:
        per_page = 10

    bugun = date.today()
    varsayilan_baslangic = (bugun - timedelta(days=15)).isoformat()

    baslangic = request.args.get('baslangic') or varsayilan_baslangic
    bitis = request.args.get('bitis') or bugun.isoformat()
    secili_plaka = request.args.get('plaka')
    secili_taseron_id = request.args.get('taseron_id')

    query = Nakliye.query

    # Filtreleri uygula
    if baslangic:
        try:
            baslangic_date = datetime.strptime(baslangic, '%Y-%m-%d').date()
            query = query.filter(Nakliye.tarih >= baslangic_date)
        except ValueError: pass
    if bitis:
        try:
            bitis_date = datetime.strptime(bitis, '%Y-%m-%d').date()
            query = query.filter(Nakliye.tarih <= bitis_date)
        except ValueError: pass
    if secili_plaka:
        query = query.filter(Nakliye.plaka == secili_plaka)
    if secili_taseron_id and secili_taseron_id.isdigit():
        query = query.filter(Nakliye.taseron_firma_id == int(secili_taseron_id))

    ordered_query = query.order_by(Nakliye.tarih.desc())
    pagination = ordered_query.paginate(page=page, per_page=per_page, error_out=False)
    nakliyeler = pagination.items
    filtered_all = ordered_query.all()

    # Dropdown listelerini hazırla
    plakalar = db.session.query(Nakliye.plaka).filter(Nakliye.plaka.isnot(None)).distinct().all()
    plaka_listesi = [p[0] for p in plakalar if p[0] and p[0].strip() != ""]
    taseron_listesi = Firma.query.filter_by(is_tedarikci=True, is_active=True).order_by(Firma.firma_adi).all()

    # İstatistikler
    stats = {
        'sefer_sayisi': len(filtered_all),
        'ciro': sum(n.toplam_tutar or 0 for n in filtered_all),
        'maliyet': sum(n.taseron_maliyet or 0 for n in filtered_all),
        'kar': sum(n.tahmini_kar or 0 for n in filtered_all)
    }

    return render_template('nakliyeler/index.html', 
                           nakliyeler=nakliyeler, 
                           pagination=pagination,
                           per_page=per_page,
                           stats=stats,
                           baslangic=baslangic,
                           bitis=bitis,
                           plaka_listesi=plaka_listesi,
                           taseron_listesi=taseron_listesi,
                           secili_taseron_id=secili_taseron_id,
                           secili_plaka=secili_plaka)

# ---------------------------------------------------
# 2. YENİ NAKLİYE KAYDI (Otomasyonlu)
# ---------------------------------------------------
@nakliye_bp.route('/ekle', methods=['GET', 'POST'])
def ekle():
    form = NakliyeForm()
    
    # Form seçeneklerini dinamik doldur
    firmalar = Firma.query.filter_by(is_active=True).order_by(Firma.firma_adi).all()
    form.firma_id.choices = [(f.id, f.firma_adi) for f in firmalar]
    form.taseron_firma_id.choices = [(0, '--- Öz Mal (Kendi Aracımız) ---')] + [(f.id, f.firma_adi) for f in firmalar if f.is_tedarikci]
    
    araclar = Arac.query.filter_by(is_active=True).all()
    form.arac_id.choices = [(0, '--- Dış Nakliye / Belirtilmemiş ---')] + [(a.id, a.plaka) for a in araclar]

    kiralama_id = request.args.get('kiralama_id', type=int)

    if form.validate_on_submit():
        try:
            nakliye = Nakliye()
            form.populate_obj(nakliye)
            
            # Öz mal araç seçildiyse plaka senkronize et
            if nakliye.arac_id and nakliye.arac_id > 0:
                secili_arac = Arac.query.get(nakliye.arac_id)
                if secili_arac:
                    nakliye.plaka = secili_arac.plaka

            # Decimal dönüşümleri
            nakliye.tutar = to_decimal(form.tutar.data)
            nakliye.taseron_maliyet = to_decimal(form.taseron_maliyet.data)
            if kiralama_id: nakliye.kiralama_id = kiralama_id
            
            nakliye.hesapla_ve_guncelle()

            # Veritabanına ekle
            db.session.add(nakliye)
            db.session.flush() 
            
            # --- 🚀 CARİ SERVİS OTOMASYONU ---
            CariServis.musteri_nakliye_senkronize_et(nakliye)
            CariServis.taseron_maliyet_senkronize_et(nakliye)
            
            db.session.commit()
            OperationLogService.log(
                module='nakliyeler', action='create',
                user_id=_actor(), username=_uname(),
                entity_type='Nakliye', entity_id=nakliye.id,
                description=f"Nakliye seferi eklendi (#{nakliye.id}).",
                success=True
            )
            flash('Nakliye seferi ve bağlı cari kayıtlar başarıyla oluşturuldu.', 'success')
            return redirect(url_for('nakliyeler.index'))
            
        except Exception as e:
            db.session.rollback()
            OperationLogService.log(
                module='nakliyeler', action='create',
                user_id=_actor(), username=_uname(),
                entity_type='Nakliye',
                description=f"Nakliye ekleme hatası: {str(e)}",
                success=False
            )
            flash(f'Kayıt hatası: {str(e)}', 'danger')

    return render_template('nakliyeler/ekle.html', form=form)

# ---------------------------------------------------
# 3. ARAÇ YÖNETİMİ (Lojistik Parkı)
# ---------------------------------------------------
@nakliye_bp.route('/arac/liste')
def arac_liste():
    araclar = Arac.query.all()
    return render_template('nakliyeler/arac_liste.html', araclar=araclar)

@nakliye_bp.route('/arac/ekle', methods=['GET', 'POST'])
def arac_ekle():
    from .forms import AracForm # Döngüsel importu önlemek için
    from app.utils import normalize_turkish_upper
    form = AracForm()
    if form.validate_on_submit():
        try:
            plaka_norm = normalize_turkish_upper(form.plaka.data)
            mevcut = Arac.query.filter_by(plaka=plaka_norm).first()
            if mevcut:
                flash(f"{form.plaka.data} zaten kayıtlı!", "danger")
            else:
                yeni_arac = Arac(
                    plaka=plaka_norm,
                    arac_tipi=form.arac_tipi.data,
                    marka_model=form.marka_model.data
                )
                db.session.add(yeni_arac)
                db.session.commit()
                flash('Araç eklendi.', 'success')
                return redirect(url_for('nakliyeler.arac_liste'))
        except Exception as e:
            db.session.rollback()
            flash(f'Hata: {str(e)}', 'danger')
    return render_template('nakliyeler/arac_ekle.html', form=form)

# ---------------------------------------------------
# 4. DÜZENLEME (Otomasyonlu & Kilitli)
# ---------------------------------------------------
@nakliye_bp.route('/duzenle/<int:id>', methods=['GET', 'POST'])
def duzenle(id):
    nakliye = Nakliye.query.get_or_404(id)
    
    if nakliye.kiralama_id:
        flash('Bu kayıt kiralama modülüne bağlıdır.', 'warning')
        return redirect(url_for('nakliyeler.index'))

    form = NakliyeForm(obj=nakliye)
    
    # Seçenekleri doldur
    firmalar = Firma.query.filter_by(is_active=True).all()
    form.firma_id.choices = [(f.id, f.firma_adi) for f in firmalar]
    form.taseron_firma_id.choices = [(0, '--- Öz Mal ---')] + [(f.id, f.firma_adi) for f in firmalar if f.is_tedarikci]
    
    araclar = Arac.query.filter_by(is_active=True).all()
    form.arac_id.choices = [(0, '--- Dış Nakliye / Belirtilmemiş ---')] + [(a.id, a.plaka) for a in araclar]

    if form.validate_on_submit():
        try:
            form.populate_obj(nakliye)
            
            if nakliye.nakliye_tipi == 'oz_mal' and nakliye.arac_id:
                secili_arac = Arac.query.get(nakliye.arac_id)
                if secili_arac: nakliye.plaka = secili_arac.plaka

            nakliye.tutar = to_decimal(form.tutar.data)
            nakliye.taseron_maliyet = to_decimal(form.taseron_maliyet.data)
            
            nakliye.hesapla_ve_guncelle()
            
            CariServis.musteri_nakliye_senkronize_et(nakliye)
            CariServis.taseron_maliyet_senkronize_et(nakliye)
            
            db.session.commit()
            OperationLogService.log(
                module='nakliyeler', action='update',
                user_id=_actor(), username=_uname(),
                entity_type='Nakliye', entity_id=nakliye.id,
                description=f"Nakliye #{nakliye.id} güncellendi.",
                success=True
            )
            flash('Kayıt güncellendi.', 'success')
            return redirect(url_for('nakliyeler.index'))
            
        except Exception as e:
            db.session.rollback()
            OperationLogService.log(
                module='nakliyeler', action='update',
                user_id=_actor(), username=_uname(),
                entity_type='Nakliye', entity_id=id,
                description=f"Nakliye güncelleme hatası: {str(e)}",
                success=False
            )
            flash(f'Hata: {str(e)}', 'danger')

    return render_template('nakliyeler/duzenle.html', form=form, nakliye=nakliye)

# ---------------------------------------------------
# 5. SİLME (Tam Temizlik)
# ---------------------------------------------------
@nakliye_bp.route('/sil/<int:id>', methods=['POST'])
def sil(id):
    nakliye = Nakliye.query.get_or_404(id)
    
    if nakliye.kiralama_id:
        flash('Kiralama bağlantılı kayıtlar silinemez.', 'danger')
        return redirect(url_for('nakliyeler.index'))
    
    try:
        CariServis.nakliye_cari_temizle(nakliye.id)
        db.session.delete(nakliye)
        db.session.commit()
        OperationLogService.log(
            module='nakliyeler', action='delete',
            user_id=_actor(), username=_uname(),
            entity_type='Nakliye', entity_id=id,
            description=f"Nakliye #{id} silindi.",
            success=True
        )
        flash('Kayıt silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        OperationLogService.log(
            module='nakliyeler', action='delete',
            user_id=_actor(), username=_uname(),
            entity_type='Nakliye', entity_id=id,
            description=f"Nakliye silme hatası: {str(e)}",
            success=False
        )
        flash(f'Hata: {str(e)}', 'danger')
        
    return redirect(url_for('nakliyeler.index'))

@nakliye_bp.route('/detay/<int:id>')
def detay(id):
    nakliye = Nakliye.query.get_or_404(id)
    return render_template('nakliyeler/detay.html', nakliye=nakliye)