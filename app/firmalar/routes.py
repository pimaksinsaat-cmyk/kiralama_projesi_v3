import os
from flask import render_template, url_for, redirect, flash, request, current_app
from datetime import date
from flask_login import current_user, login_required
from decimal import Decimal

from app.firmalar import firmalar_bp
from app.firmalar.forms import FirmaForm
from app.firmalar.models import Firma
from app.services.firma_services import FirmaService
from app.services.base import ValidationError

# --- GÜVENLİK YARDIMCISI ---
def get_actor_id():
    """Kullanıcı giriş yapmışsa ID'sini döner, aksi halde None."""
    return getattr(current_user, 'id', None)

# -------------------------------------------------------------------------
# 1. Aktif Firma Listeleme
# -------------------------------------------------------------------------
@firmalar_bp.route('/')
@firmalar_bp.route('/index')
@login_required
def index():
    try:
        page = request.args.get('page', 1, type=int)
        q = request.args.get('q', '', type=str)
        
        query = FirmaService.get_active_firms(search_query=q)
        pagination = query.paginate(page=page, per_page=50, error_out=False)
        
        return render_template('firmalar/index.html', firmalar=pagination.items, pagination=pagination, q=q)
    except Exception as e:
        current_app.logger.error(f"Firma listesi yüklenirken hata: {str(e)}")
        flash("Firma listesi şu an yüklenemiyor.", "danger")
        return redirect(url_for('main.index')) # Ana sayfaya yönlendir

# -------------------------------------------------------------------------
# 2. Pasif (Arşivlenmiş) Firma Listeleme
# -------------------------------------------------------------------------
@firmalar_bp.route('/pasif')
@login_required
def pasif_index():
    try:
        page = request.args.get('page', 1, type=int)
        q = request.args.get('q', '', type=str)
        
        query = FirmaService.get_inactive_firms(search_query=q)
        pagination = query.paginate(page=page, per_page=50, error_out=False)
        
        return render_template('firmalar/pasif_index.html', firmalar=pagination.items, pagination=pagination, q=q)
    except Exception as e:
        current_app.logger.error(f"Pasif firma listesi hatası: {str(e)}")
        flash("Arşivlenmiş firmalar yüklenemedi.", "danger")
        return redirect(url_for('firmalar.index'))

# -------------------------------------------------------------------------
# 3. Yeni Firma Ekleme
# -------------------------------------------------------------------------
@firmalar_bp.route('/ekle', methods=['GET', 'POST'])
@login_required
def ekle():
    form = FirmaForm()
    
    if form.validate_on_submit():
        try:
            # Servis katmanında tanımlı güncellenebilir alanları süzerek al
            data = {k: v for k, v in form.data.items() if k in FirmaService.updatable_fields}
            
            # Başlangıç değerlerini set et
            data.update({
                'bakiye': Decimal('0'),
                'sozlesme_rev_no': 0,
                'sozlesme_no': None
            })
            
            yeni_firma = Firma(**data)
            FirmaService.save(yeni_firma, actor_id=get_actor_id())
            
            flash(f"'{yeni_firma.firma_adi}' başarıyla sisteme kaydedildi.", "success")
            return redirect(url_for('firmalar.index'))
        except ValidationError as e:
            flash(str(e), "warning")
        except Exception as e:
            current_app.logger.error(f"Firma ekleme hatası: {str(e)}")
            flash("Kayıt sırasında sistemsel bir hata oluştu.", "danger")
            
    return render_template('firmalar/ekle.html', form=form, today_date=date.today().strftime('%d.%m.%Y'))

# -------------------------------------------------------------------------
# 4. Sözleşme Hazırla
# -------------------------------------------------------------------------
@firmalar_bp.route('/sozlesme-hazirla/<int:id>', methods=['POST'])
@login_required
def sozlesme_hazirla(id):
    try:
        app_path = os.path.join(os.getcwd(), 'app')
        FirmaService.sozlesme_hazirla(firma_id=id, base_app_path=app_path, actor_id=get_actor_id())
        flash("Sözleşme numarası başarıyla atandı ve arşiv klasörleri oluşturuldu.", "success")
    except ValidationError as e:
        flash(str(e), "warning")
    except Exception as e:
        current_app.logger.error(f"Sözleşme hazırlama hatası (Firma ID: {id}): {str(e)}")
        flash("Klasör yapısı oluşturulurken bir hata meydana geldi.", "danger")
    return redirect(url_for('firmalar.index'))

# -------------------------------------------------------------------------
# 5. Firma Düzenleme
# -------------------------------------------------------------------------
@firmalar_bp.route('/duzelt/<int:id>', methods=['GET', 'POST'])
@login_required
def duzelt(id):
    firma = FirmaService.get_by_id(id)
    if not firma:
        flash("Düzenlenmek istenen firma bulunamadı!", "danger")
        return redirect(url_for('firmalar.index'))
        
    form = FirmaForm(obj=firma)
    
    # Özel alanları form verisine elle eşle (Form yapısına göre)
    if request.method == 'GET':
        form.genel_sozlesme_no.data = firma.sozlesme_no
        form.sozlesme_rev_no.data = firma.sozlesme_rev_no
        form.sozlesme_tarihi.data = firma.sozlesme_tarihi

    if form.validate_on_submit():
        try:
            data = {k: v for k, v in form.data.items() if k in FirmaService.updatable_fields}
            
            # Formdaki özel alanları veritabanı alanlarıyla eşleştir
            data.update({
                'sozlesme_no': form.genel_sozlesme_no.data,
                'sozlesme_rev_no': form.sozlesme_rev_no.data,
                'sozlesme_tarihi': form.sozlesme_tarihi.data
            })
            
            FirmaService.update(id, data, actor_id=get_actor_id())
            flash(f"'{firma.firma_adi}' bilgileri başarıyla güncellendi.", 'success')
            return redirect(url_for('firmalar.index'))
        except ValidationError as e:
            flash(str(e), "danger")
        except Exception as e:
            current_app.logger.error(f"Firma güncelleme hatası (ID: {id}): {str(e)}")
            flash("Bilgiler güncellenirken bir hata oluştu.", "danger")
            
    return render_template('firmalar/duzelt.html', form=form, firma=firma)

# -------------------------------------------------------------------------
# 6. Firma Bilgi / Cari Ekstre
# -------------------------------------------------------------------------
@firmalar_bp.route('/bilgi/<int:id>', methods=['GET'])
@login_required
def bilgi(id):
    try:
        finans_verileri = FirmaService.get_financial_summary(id)
        return render_template('firmalar/bilgi.html', **finans_verileri)
    except ValidationError as e:
        flash(str(e), "danger")
        return redirect(url_for('firmalar.index'))
    except Exception as e:
        current_app.logger.error(f"Cari özet yükleme hatası (Firma ID: {id}): {str(e)}")
        flash("Finansal veriler şu an hesaplanamıyor.", "danger")
        return redirect(url_for('firmalar.index'))

# -------------------------------------------------------------------------
# 7. Firmayı Arşive Kaldır (Silme - Kontrollü)
# -------------------------------------------------------------------------
@firmalar_bp.route('/sil/<int:id>', methods=['POST'])
@login_required
def sil(id):
    try:
        FirmaService.archive_with_check(id, actor_id=get_actor_id())
        flash("Firma başarıyla arşive kaldırıldı.", 'success')
    except ValidationError as e:
        flash(str(e), 'warning')
    except Exception as e:
        current_app.logger.error(f"Arşivleme hatası (ID: {id}): {str(e)}")
        flash("İşlem sırasında sistemsel bir hata oluştu.", 'danger')
    return redirect(url_for('firmalar.index'))

# -------------------------------------------------------------------------
# 8. Firmayı Aktifleştir (Arşivden Geri Al)
# -------------------------------------------------------------------------
@firmalar_bp.route('/aktiflestir/<int:id>', methods=['POST'])
@login_required
def aktiflestir(id):
    try:
        FirmaService.update(id, {'is_active': True}, actor_id=get_actor_id())
        flash("Firma başarıyla tekrar aktif hale getirildi.", "success")
    except Exception as e:
        current_app.logger.error(f"Aktifleştirme hatası (ID: {id}): {str(e)}")
        flash("İşlem başarısız oldu.", "danger")
    return redirect(url_for('firmalar.pasif_index'))

# -------------------------------------------------------------------------
# 9. İmza Yetkisi Kontrolü
# -------------------------------------------------------------------------
@firmalar_bp.route('/imza-kontrol/<int:id>', methods=['POST'])
@login_required
def imza_kontrol(id):
    try:
        FirmaService.update(
            id, 
            {'imza_yetkisi_kontrol_edildi': True, 'imza_yetkisi_kontrol_tarihi': date.today()}, 
            actor_id=get_actor_id()
        )
        flash("İmza yetkisi başarıyla onaylandı.", "success")
    except ValidationError as e:
        flash(str(e), "danger")
    except Exception as e:
        current_app.logger.error(f"İmza kontrol hatası (ID: {id}): {str(e)}")
        flash("Onay işlemi yapılamadı.", "danger")
    return redirect(url_for('firmalar.bilgi', id=id))