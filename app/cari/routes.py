from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user

from app.cari import cari_bp
# DÜZELTME: KasaHizliIslemForm ve KasaTransferForm import listesine eklendi
from app.cari.forms import OdemeForm, HizmetKaydiForm, KasaForm, KasaTransferForm, KasaHizliIslemForm
from app.cari.models import Kasa, Odeme, HizmetKaydi
from app.firmalar.models import Firma

# --- YENİ SERVİS MİMARİSİ İÇE AKTARIMLARI ---
from app.services.cari_services import (
    KasaService, OdemeService, HizmetKaydiService, 
    CariRaporService, get_dahili_islem_firmasi
)
from app.services.base import ValidationError
from app.services.operation_log_service import OperationLogService

from decimal import Decimal
from datetime import date, datetime
import traceback

# -------------------------------------------------------------------------
# 🛠️ YARDIMCI FONKSİYONLAR
# -------------------------------------------------------------------------
class ListPagination:
    def __init__(self, total, page, per_page):
        self.total = max(0, int(total or 0))
        self.page = max(1, int(page or 1))
        self.per_page = max(1, int(per_page or 1))

        if self.total == 0:
            self.pages = 0
        else:
            self.pages = (self.total + self.per_page - 1) // self.per_page

        if self.pages and self.page > self.pages:
            self.page = self.pages

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def prev_num(self):
        return self.page - 1

    @property
    def next_num(self):
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if (
                num <= left_edge
                or (self.page - left_current - 1 < num < self.page + right_current)
                or num > self.pages - right_edge
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num


def get_actor():
    """Audit Log için işlemi yapan kullanıcının ID'sini döndürür."""
    return current_user.id if current_user.is_authenticated else None

# -------------------------------------------------------------------------
# 1. ÖDEME VE TAHSİLAT
# -------------------------------------------------------------------------
@cari_bp.route('/odeme/ekle', methods=['GET', 'POST'])
def odeme_ekle():
    firma_id = request.args.get('firma_id', type=int)
    yon_param = request.args.get('yon', 'tahsilat')
    form = OdemeForm()
    
    # Seçenekleri dinamik yükle (is_deleted kontrolü servis üzerinden değil modelden geçici olarak yapılıyor)
    form.firma_musteri_id.choices = [(f.id, f.firma_adi) for f in Firma.query.filter_by(is_active=True, is_deleted=False).all()]
    form.kasa_id.choices = [(k.id, f"{k.kasa_adi} ({k.bakiye} {k.para_birimi})") 
                            for k in Kasa.query.filter_by(is_active=True, is_deleted=False).all()]
    
    if request.method == 'GET':
        if firma_id: form.firma_musteri_id.data = firma_id
        form.tarih.data = date.today()
        form.yon.data = yon_param

    if form.validate_on_submit():
        try:
            yeni_odeme = Odeme(
                firma_musteri_id=form.firma_musteri_id.data,
                kasa_id=form.kasa_id.data,
                tarih=form.tarih.data,
                tutar=form.tutar.data, # MoneyField sayesinde otomatik Decimal
                yon=form.yon.data,
                aciklama=form.aciklama.data,
                fatura_no=form.fatura_no.data,
                vade_tarihi=form.vade_tarihi.data
            )
            
            OdemeService.save(yeni_odeme, is_new=True, actor_id=get_actor())
            OperationLogService.log(
                module='cari', action='odeme_ekle',
                user_id=get_actor(), username=getattr(current_user, 'username', None),
                entity_type='Odeme', entity_id=yeni_odeme.id,
                description=f"{yeni_odeme.yon.upper()} {yeni_odeme.tutar} - {getattr(yeni_odeme, 'aciklama', '')}",
                success=True
            )
            flash('İşlem başarıyla kaydedildi.', 'success')
            return redirect(url_for('firmalar.bilgi', id=form.firma_musteri_id.data))
            
        except ValidationError as e:
            OperationLogService.log(
                module='cari', action='odeme_ekle',
                user_id=get_actor(), username=getattr(current_user, 'username', None),
                entity_type='Odeme',
                description=f"Ödeme ekleme hatası: {str(e)}",
                success=False
            )
            flash(str(e), "warning")
        except Exception as e:
            OperationLogService.log(
                module='cari', action='odeme_ekle',
                user_id=get_actor(), username=getattr(current_user, 'username', None),
                entity_type='Odeme',
                description=f"Ödeme ekleme hatası: {str(e)}",
                success=False
            )
            flash(f"Hata: {str(e)}", "danger")
            
    return render_template('cari/odeme_ekle.html', form=form)

@cari_bp.route('/odeme/duzelt/<int:id>', methods=['GET', 'POST'])
def odeme_duzelt(id):
    odeme = OdemeService.get_by_id(id)
    if not odeme or odeme.is_deleted:
        flash("Kayıt bulunamadı", "danger")
        return redirect(request.referrer or url_for('cari.finans_menu'))
        
    form = OdemeForm(obj=odeme)
    form.firma_musteri_id.choices = [(f.id, f.firma_adi) for f in Firma.query.filter_by(is_active=True, is_deleted=False).all()]
    form.kasa_id.choices = [(k.id, f"{k.kasa_adi} ({k.bakiye} {k.para_birimi})") 
                            for k in Kasa.query.filter_by(is_active=True, is_deleted=False).all()]

    if form.validate_on_submit():
        try:
            odeme.firma_musteri_id = form.firma_musteri_id.data
            odeme.kasa_id = form.kasa_id.data
            odeme.tarih = form.tarih.data
            odeme.tutar = form.tutar.data
            odeme.yon = form.yon.data
            odeme.aciklama = form.aciklama.data
            odeme.fatura_no = form.fatura_no.data
            odeme.vade_tarihi = form.vade_tarihi.data
            
            # Servis katmanında after_save kancası eski bakiyeyi geri alıp yeniyi işler
            OdemeService.save(odeme, is_new=False, actor_id=get_actor())
            OperationLogService.log(
                module='cari', action='odeme_duzelt',
                user_id=get_actor(), username=getattr(current_user, 'username', None),
                entity_type='Odeme', entity_id=id,
                description=f"Ödeme #{id} güncellendi.",
                success=True
            )
            flash('İşlem güncellendi.', 'success')
            return redirect(url_for('firmalar.bilgi', id=odeme.firma_musteri_id))
        except ValidationError as e:
            OperationLogService.log(
                module='cari', action='odeme_duzelt',
                user_id=get_actor(), username=getattr(current_user, 'username', None),
                entity_type='Odeme', entity_id=id,
                description=f"Ödeme güncelleme hatası: {str(e)}",
                success=False
            )
            flash(str(e), "warning")
            
    return render_template('cari/odeme_ekle.html', form=form, title="Ödeme Düzenle")

@cari_bp.route('/odeme/sil/<int:id>', methods=['POST'])
def odeme_sil(id):
    odeme = OdemeService.get_by_id(id)
    if not odeme:
        flash('Ödeme kaydı bulunamadı.', 'danger')
        return redirect(request.referrer or url_for('cari.kasa_listesi'))
        
    f_id = odeme.firma_musteri_id
    try:
        OdemeService.delete(id, actor_id=get_actor())
        OperationLogService.log(
            module='cari', action='odeme_sil',
            user_id=get_actor(), username=getattr(current_user, 'username', None),
            entity_type='Odeme', entity_id=id,
            description=f"Ödeme #{id} silindi.",
            success=True
        )
        flash('Ödeme/Tahsilat kaydı silindi ve kasa bakiyesi düzeltildi.', 'success')
    except ValidationError as e:
        OperationLogService.log(
            module='cari', action='odeme_sil',
            user_id=get_actor(), username=getattr(current_user, 'username', None),
            entity_type='Odeme', entity_id=id,
            description=f"Ödeme silme hatası: {str(e)}",
            success=False
        )
        flash(str(e), "warning")
    except Exception as e:
        OperationLogService.log(
            module='cari', action='odeme_sil',
            user_id=get_actor(), username=getattr(current_user, 'username', None),
            entity_type='Odeme', entity_id=id,
            description=f"Ödeme silme hatası: {str(e)}",
            success=False
        )
        flash(f'Hata: {str(e)}', 'danger')
        
    return redirect(url_for('firmalar.bilgi', id=f_id))

# -------------------------------------------------------------------------
# 2. HİZMET / FATURA
# -------------------------------------------------------------------------
@cari_bp.route('/hizmet/ekle', methods=['GET', 'POST'])
def hizmet_ekle():
    firma_id = request.args.get('firma_id', type=int)
    form = HizmetKaydiForm()
    form.firma_id.choices = [(f.id, f.firma_adi) for f in Firma.query.filter_by(is_active=True, is_deleted=False).all()]
    
    if request.method == 'GET':
        if firma_id: form.firma_id.data = firma_id
        form.tarih.data = date.today()

    if form.validate_on_submit():
        try:
            yeni_hizmet = HizmetKaydi(
                firma_id=form.firma_id.data,
                tarih=form.tarih.data,
                tutar=form.tutar.data,
                yon=form.yon.data,
                aciklama=form.aciklama.data,
                fatura_no=form.fatura_no.data
            )
            HizmetKaydiService.save(yeni_hizmet, actor_id=get_actor())
            OperationLogService.log(
                module='cari', action='hizmet_ekle',
                user_id=get_actor(), username=getattr(current_user, 'username', None),
                entity_type='HizmetKaydi', entity_id=yeni_hizmet.id,
                description=f"Hizmet/Fatura kaydı eklendi: {getattr(yeni_hizmet, 'aciklama', '')}",
                success=True
            )
            flash('Fatura kaydedildi.', 'success')
            return redirect(url_for('firmalar.bilgi', id=form.firma_id.data))
        except ValidationError as e:
            OperationLogService.log(
                module='cari', action='hizmet_ekle',
                user_id=get_actor(), username=getattr(current_user, 'username', None),
                entity_type='HizmetKaydi',
                description=f"Hizmet ekleme hatası: {str(e)}",
                success=False
            )
            flash(str(e), "warning")
            
    return render_template('cari/hizmet_ekle.html', form=form)

@cari_bp.route('/hizmet/duzelt/<int:id>', methods=['GET', 'POST'])
def hizmet_duzelt(id):
    hizmet = HizmetKaydiService.get_by_id(id)
    if not hizmet or hizmet.is_deleted:
        flash('Kayıt bulunamadı', 'danger')
        return redirect(request.referrer)
    
    form = HizmetKaydiForm(obj=hizmet)
    form.firma_id.choices = [(f.id, f.firma_adi) for f in Firma.query.filter_by(is_active=True, is_deleted=False).all()]

    if form.validate_on_submit():
        try:
            hizmet.firma_id = form.firma_id.data
            hizmet.tarih = form.tarih.data
            hizmet.tutar = form.tutar.data
            hizmet.yon = form.yon.data
            hizmet.aciklama = form.aciklama.data
            hizmet.fatura_no = form.fatura_no.data
            
            HizmetKaydiService.save(hizmet, is_new=False, actor_id=get_actor())
            OperationLogService.log(
                module='cari', action='hizmet_duzelt',
                user_id=get_actor(), username=getattr(current_user, 'username', None),
                entity_type='HizmetKaydi', entity_id=id,
                description=f"Hizmet/Fatura #{id} güncellendi.",
                success=True
            )
            flash('Fatura güncellendi.', 'success')
            return redirect(url_for('firmalar.bilgi', id=hizmet.firma_id))
        except ValidationError as e:
            OperationLogService.log(
                module='cari', action='hizmet_duzelt',
                user_id=get_actor(), username=getattr(current_user, 'username', None),
                entity_type='HizmetKaydi', entity_id=id,
                description=f"Hizmet güncelleme hatası: {str(e)}",
                success=False
            )
            flash(str(e), "warning")
            
    return render_template('cari/hizmet_ekle.html', form=form, title="Fatura Düzenle")

@cari_bp.route('/hizmet/sil/<int:id>', methods=['POST'])
def hizmet_sil(id):
    hizmet = HizmetKaydiService.get_by_id(id)
    if not hizmet: return redirect(request.referrer)
        
    f_id = hizmet.firma_id
    try:
        HizmetKaydiService.delete(id, actor_id=get_actor())
        OperationLogService.log(
            module='cari', action='hizmet_sil',
            user_id=get_actor(), username=getattr(current_user, 'username', None),
            entity_type='HizmetKaydi', entity_id=id,
            description=f"Hizmet/Fatura #{id} silindi.",
            success=True
        )
        flash('Fatura kaydı silindi.', 'success')
    except ValidationError as e:
        OperationLogService.log(
            module='cari', action='hizmet_sil',
            user_id=get_actor(), username=getattr(current_user, 'username', None),
            entity_type='HizmetKaydi', entity_id=id,
            description=f"Hizmet silme hatası: {str(e)}",
            success=False
        )
        flash(str(e), 'warning')
        
    return redirect(url_for('firmalar.bilgi', id=f_id))

# -------------------------------------------------------------------------
# 3. KASA YÖNETİMİ VE TRANSFER
# -------------------------------------------------------------------------
@cari_bp.route('/kasa/listesi')
def kasa_listesi():
    kasalar = KasaService.find_by(is_active=True, is_deleted=False)
    
    # Modal transfer formu
    transfer_form = KasaTransferForm()
    kasa_choices = [(k.id, f"{k.kasa_adi} ({k.para_birimi})") for k in kasalar]
    transfer_form.kaynak_kasa_id.choices = kasa_choices
    transfer_form.hedef_kasa_id.choices = kasa_choices
    
    # Modal hızlı işlem formu
    hizli_form = KasaHizliIslemForm()
    hizli_form.kasa_id.choices = kasa_choices

    kasalar_json = [
        {
            'id': str(k.id),
            'adi': k.kasa_adi or '',
            'birim': k.para_birimi or '',
            'bakiye': float(k.bakiye or 0),
        }
        for k in kasalar
    ]

    return render_template('cari/kasa_listesi.html', 
                           kasalar=kasalar, 
                           form=transfer_form, 
                           hizli_form=hizli_form,
                           kasalar_json=kasalar_json)

@cari_bp.route('/kasa/transfer', methods=['POST'])
def kasa_transfer():
    kasalar = KasaService.find_by(is_active=True, is_deleted=False)
    form = KasaTransferForm()
    kasa_choices = [(k.id, k.kasa_adi) for k in kasalar]
    form.kaynak_kasa_id.choices = kasa_choices
    form.hedef_kasa_id.choices = kasa_choices

    if form.validate_on_submit():
        try:
            KasaService.transfer_yap(
                form.kaynak_kasa_id.data, 
                form.hedef_kasa_id.data, 
                form.tutar.data, 
                actor_id=get_actor()
            )
            OperationLogService.log(
                module='cari', action='kasa_transfer',
                user_id=get_actor(), username=getattr(current_user, 'username', None),
                entity_type='Kasa',
                description=f"Kasa transfer: {form.tutar.data} (kasa {form.kaynak_kasa_id.data} → {form.hedef_kasa_id.data}).",
                success=True
            )
            flash('Para transferi başarıyla tamamlandı.', 'success')
        except ValidationError as e:
            OperationLogService.log(
                module='cari', action='kasa_transfer',
                user_id=get_actor(), username=getattr(current_user, 'username', None),
                entity_type='Kasa',
                description=f"Kasa transfer hatası: {str(e)}",
                success=False
            )
            flash(str(e), "warning")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", "danger")
                
    return redirect(url_for('cari.kasa_listesi'))

@cari_bp.route('/kasa/hizli_islem', methods=['POST'])
def kasa_hizli_islem():
    """
    KasaHizliIslemForm kullanarak manuel parse işlemlerinden kurtulduk.
    """
    form = KasaHizliIslemForm()
    kasalar = KasaService.find_by(is_active=True, is_deleted=False)
    form.kasa_id.choices = [(k.id, k.kasa_adi) for k in kasalar]

    if form.validate_on_submit():
        try:
            dahili = get_dahili_islem_firmasi()
            yon = 'tahsilat' if form.islem_yonu.data == 'giris' else 'odeme'
            
            odeme = Odeme(
                firma_musteri_id=dahili.id,
                kasa_id=form.kasa_id.data,
                tarih=date.today(),
                tutar=form.tutar.data, # MoneyField sayesinde temiz Decimal gelir
                yon=yon,
                aciklama=f"Hızlı Kasa İşlemi: {form.aciklama.data}"
            )

            OdemeService.save(odeme, actor_id=get_actor())
            OperationLogService.log(
                module='cari', action='kasa_hizli_islem',
                user_id=get_actor(), username=getattr(current_user, 'username', None),
                entity_type='Kasa', entity_id=form.kasa_id.data,
                description=f"Hızlı kasa işlemi: {form.islem_yonu.data} {form.tutar.data} - {form.aciklama.data}",
                success=True
            )
            flash("Kasa işlemi başarıyla kaydedildi", "success")

        except ValidationError as e:
            OperationLogService.log(
                module='cari', action='kasa_hizli_islem',
                user_id=get_actor(), username=getattr(current_user, 'username', None),
                entity_type='Kasa',
                description=f"Hızlı kasa işlem hatası: {str(e)}",
                success=False
            )
            flash(str(e), "warning")
        except Exception as e:
            OperationLogService.log(
                module='cari', action='kasa_hizli_islem',
                user_id=get_actor(), username=getattr(current_user, 'username', None),
                entity_type='Kasa',
                description=f"Hızlı kasa işlem hatası: {str(e)}",
                success=False
            )
            flash(f"Hızlı kasa işlem hatası: {str(e)}", "danger")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return redirect(url_for('cari.kasa_listesi'))

@cari_bp.route('/kasa/ekle', methods=['GET', 'POST'])
def kasa_ekle():
    form = KasaForm()

    if form.validate_on_submit():
        try:
            yeni_kasa = Kasa(
                kasa_adi=form.kasa_adi.data,
                tipi=form.tipi.data,
                para_birimi=form.para_birimi.data,
                banka_sube_adi=(form.banka_sube_adi.data or '').strip() or None,
                bakiye=form.bakiye.data or 0
            )
            KasaService.save(yeni_kasa, actor_id=get_actor())
            OperationLogService.log(
                module='cari', action='kasa_ekle',
                user_id=get_actor(), username=getattr(current_user, 'username', None),
                entity_type='Kasa', entity_id=yeni_kasa.id,
                description=f"{yeni_kasa.kasa_adi} kasası oluşturuldu.",
                success=True
            )
            flash(f'{yeni_kasa.kasa_adi} başarıyla oluşturuldu.', 'success')
            return redirect(url_for('cari.kasa_listesi'))
        except ValidationError as e:
            OperationLogService.log(
                module='cari', action='kasa_ekle',
                user_id=get_actor(), username=getattr(current_user, 'username', None),
                entity_type='Kasa',
                description=f"Kasa ekleme hatası: {str(e)}",
                success=False
            )
            flash(str(e), "warning")
            
    return render_template('cari/kasa_ekle.html', form=form, title="Yeni Kasa Ekle")

@cari_bp.route('/kasa/duzelt/<int:id>', methods=['GET', 'POST'])
def kasa_duzelt(id):
    kasa = KasaService.get_by_id(id)
    if not kasa or kasa.is_deleted:
        flash("Kasa bulunamadı", "danger")
        return redirect(url_for('cari.kasa_listesi'))
        
    form = KasaForm(obj=kasa)

    if form.validate_on_submit():
        try:
            kasa.kasa_adi = form.kasa_adi.data
            kasa.tipi = form.tipi.data
            kasa.para_birimi = form.para_birimi.data
            kasa.banka_sube_adi = (form.banka_sube_adi.data or '').strip() or None
            KasaService.save(kasa, is_new=False, actor_id=get_actor())
            OperationLogService.log(
                module='cari', action='kasa_duzelt',
                user_id=get_actor(), username=getattr(current_user, 'username', None),
                entity_type='Kasa', entity_id=id,
                description=f"Kasa #{id} ({kasa.kasa_adi}) güncellendi.",
                success=True
            )
            flash('Kasa bilgileri güncellendi.', 'success')
            return redirect(url_for('cari.kasa_listesi'))
        except ValidationError as e:
            OperationLogService.log(
                module='cari', action='kasa_duzelt',
                user_id=get_actor(), username=getattr(current_user, 'username', None),
                entity_type='Kasa', entity_id=id,
                description=f"Kasa güncelleme hatası: {str(e)}",
                success=False
            )
            flash(str(e), "warning")
            
    return render_template('cari/kasa_ekle.html', form=form, title="Kasa Düzenle")

@cari_bp.route('/kasa/sil/<int:id>', methods=['POST'])
def kasa_sil(id):
    hedef_kasa_id = request.form.get('hedef_kasa_id', type=int)
    try:
        KasaService.kasa_kapat_ve_devret(id, hedef_kasa_id, actor_id=get_actor())
        OperationLogService.log(
            module='cari', action='kasa_sil',
            user_id=get_actor(), username=getattr(current_user, 'username', None),
            entity_type='Kasa', entity_id=id,
            description=f"Kasa #{id} kapatıldı ve bakiye devredildi.",
            success=True
        )
        flash('Kasa hesabı başarıyla kapatıldı.', 'success')
    except ValidationError as e:
        OperationLogService.log(
            module='cari', action='kasa_sil',
            user_id=get_actor(), username=getattr(current_user, 'username', None),
            entity_type='Kasa', entity_id=id,
            description=f"Kasa kapatma hatası: {str(e)}",
            success=False
        )
        flash(str(e), 'warning')
    except Exception as e:
        OperationLogService.log(
            module='cari', action='kasa_sil',
            user_id=get_actor(), username=getattr(current_user, 'username', None),
            entity_type='Kasa', entity_id=id,
            description=f"Kasa kapatma hatası: {str(e)}",
            success=False
        )
        flash(f"Hata: {str(e)}", 'danger')
        
    return redirect(url_for('cari.kasa_listesi'))

@cari_bp.route('/kasa/hareketleri/<int:id>')
def kasa_hareketleri(id):
    kasa = KasaService.get_by_id(id)
    if not kasa or kasa.is_deleted:
        flash("Kasa bulunamadı", "danger")
        return redirect(url_for('cari.kasa_listesi'))

    hareketler = Odeme.query.filter_by(kasa_id=kasa.id, is_deleted=False)\
                      .order_by(Odeme.tarih.desc(), Odeme.id.desc()).all()
    return render_template('cari/kasa_hareketleri.html', kasa=kasa, hareketler=hareketler)

# -------------------------------------------------------------------------
# 4. RAPORLAR VE MENÜ
# -------------------------------------------------------------------------
@cari_bp.route('/finans-menu')
def finans_menu():
    return render_template('cari/finans_menu.html')

@cari_bp.route('/cari-durum-raporu')
def cari_durum_raporu():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        sort_by = request.args.get('sort_by', 'firma_adi', type=str)
        sort_dir = request.args.get('sort_dir', 'asc', type=str)
        q = (request.args.get('q', '', type=str) or '').strip()

        allowed_per_page = {10, 25, 50, 100}
        allowed_sort_by = {'firma_adi', 'bakiye', 'durum'}
        allowed_sort_dir = {'asc', 'desc'}

        if per_page not in allowed_per_page:
            per_page = 10
        if sort_by not in allowed_sort_by:
            sort_by = 'firma_adi'
        if sort_dir not in allowed_sort_dir:
            sort_dir = 'asc'

        rapor, genel_toplam = CariRaporService.get_durum_raporu()

        if q:
            q_lower = q.casefold()
            rapor = [
                satir for satir in rapor
                if q_lower in (satir.get('firma_adi') or '').casefold()
            ]

        if sort_by == 'firma_adi':
            sort_key = lambda s: (s.get('firma_adi') or '').casefold()
        elif sort_by == 'bakiye':
            sort_key = lambda s: float(s.get('bakiye') or 0)
        else:
            def durum_key(s):
                bakiye = float(s.get('bakiye') or 0)
                if bakiye > 0:
                    return 'borclu'
                if bakiye < 0:
                    return 'alacakli'
                return 'kapali'
            sort_key = durum_key

        rapor = sorted(rapor, key=sort_key, reverse=(sort_dir == 'desc'))

        toplam_kayit = len(rapor)
        pagination = ListPagination(total=toplam_kayit, page=page, per_page=per_page)
        baslangic = (pagination.page - 1) * pagination.per_page
        bitis = baslangic + pagination.per_page
        rapor_sayfa = rapor[baslangic:bitis]

        return render_template(
            'cari/cari_durum_raporu.html',
            rapor=rapor_sayfa,
            genel_toplam=genel_toplam,
            pagination=pagination,
            per_page=per_page,
            sort_by=sort_by,
            sort_dir=sort_dir,
            q=q,
        )
    except ValidationError as e:
        flash(str(e), "danger")
        return redirect(url_for('cari.finans_menu'))