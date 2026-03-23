import os
from datetime import date
from decimal import Decimal
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload, subqueryload

from app.services.base import BaseService, ValidationError
from app.firmalar.models import Firma
from app.kiralama.models import Kiralama, KiralamaKalemi
from app.cari.models import Odeme
from app.extensions import db
from app.ayarlar.models import AppSettings
from app.utils import klasor_adi_temizle

class FirmaService(BaseService):
    """
    Firma (Müşteri/Tedarikçi) yönetimi ve cari hesaplamalar için iş mantığı katmanı.
    """
    model = Firma
    use_soft_delete = True
    
    # Güncellenebilir alanlar
    updatable_fields = [
        'firma_adi', 'yetkili_adi', 'telefon', 'eposta', 
        'iletisim_bilgileri', 'vergi_dairesi', 'vergi_no',
        'is_musteri', 'is_tedarikci', 'sozlesme_no', 
        'sozlesme_rev_no', 'sozlesme_tarihi', 'imza_yetkisi_kontrol_edildi',
        'imza_yetkisi_kontrol_tarihi', 'is_active'
    ]

    @classmethod
    def validate(cls, instance, is_new=True):
        """Vergi numarası benzersizlik kontrolü."""
        if instance.vergi_no:
            mevcut = cls.find_one_by(vergi_no=instance.vergi_no)
            if mevcut and (is_new or mevcut.id != instance.id):
                raise ValidationError(f"'{instance.vergi_no}' vergi numarası başka bir firmada kayıtlı!")

    @classmethod
    def before_save(cls, instance, is_new=True):
        """Kayıt öncesi standartlaştırma."""
        if instance.firma_adi:
            instance.firma_adi = instance.firma_adi.strip().upper()
        if instance.vergi_no:
            instance.vergi_no = instance.vergi_no.strip()

    @classmethod
    def get_active_firms(cls, search_query=None):
        """Aktif firmaları listeler (Dahili Kasa hariç)."""
        query = cls._get_base_query().filter(
            and_(
                Firma.firma_adi != 'Dahili Kasa İşlemleri',
                or_(Firma.is_active == True, Firma.is_active.is_(None))
            )
        )
        if search_query:
            term = f"%{search_query}%"
            query = query.filter(or_(
                Firma.firma_adi.ilike(term),
                Firma.yetkili_adi.ilike(term),
                Firma.vergi_no.ilike(term),
                Firma.telefon.ilike(term),
                Firma.eposta.ilike(term)
            ))
        return query.order_by(Firma.id.desc())
    @classmethod
    def get_inactive_firms(cls, search_query=None):
        """Arşivlenmiş (is_active=False) firmaları listeler."""
        query = cls._get_base_query().filter(Firma.is_active == False)
        if search_query:
            term = f"%{search_query}%"
            query = query.filter(or_(
                Firma.firma_adi.ilike(term),
                Firma.vergi_no.ilike(term)
            ))
        return query.order_by(Firma.id.desc())

    @classmethod
    def archive_with_check(cls, firma_id, actor_id=None):
        """
        Firmayı arşive kaldırır. 
        EĞER üzerinde kiralama kaydı varsa işlemi engeller.
        """
        firma = cls._get_base_query().options(subqueryload(Firma.kiralamalar)).filter_by(id=firma_id).first()
        
        if not firma:
            raise ValidationError("Firma bulunamadı.")

        if firma.kiralamalar:
            raise ValidationError(f"'{firma.firma_adi}' ünvanlı firmanın üzerinde kiralama kayıtları bulunduğu için arşive kaldırılamaz.")

        return cls.update(firma_id, {'is_active': False}, actor_id=actor_id)
    
    @classmethod
    def sozlesme_hazirla(cls, firma_id, base_app_path, actor_id=None):
        """Sözleşme numarası üretir ve fiziksel arşiv klasörlerini açar."""
        firma = cls.get_by_id(firma_id)
        if not firma:
            raise ValidationError("Firma bulunamadı.")
        if firma.sozlesme_no:
            raise ValidationError(f"Bu firma için zaten bir sözleşme ({firma.sozlesme_no}) mevcut.")

        current_year = date.today().year
        settings = AppSettings.get_current()
        start_no = settings.genel_sozlesme_start_no if settings else 1
        prefix = settings.genel_sozlesme_prefix if settings and settings.genel_sozlesme_prefix else 'PS'
        last_firma = cls._get_base_query().filter(Firma.sozlesme_no.like(f"{prefix}-{current_year}-%")).order_by(Firma.sozlesme_no.desc()).first()
        
        next_nr = start_no
        if last_firma and last_firma.sozlesme_no:
            try:
                next_nr = int(last_firma.sozlesme_no.split('-')[-1]) + 1
            except ValueError:
                pass
                
        next_ps_no = f"{prefix}-{current_year}-{next_nr:03d}"
        
        ikinci_parametre = firma.vergi_no if firma.vergi_no else str(firma.id)
        klasor_adi = klasor_adi_temizle(firma.firma_adi, ikinci_parametre)
        
        firma.sozlesme_no = next_ps_no
        # İlk kez hazırlanırken tarihi set et, sonra değişme
        if firma.sozlesme_tarihi is None:
            firma.sozlesme_tarihi = date.today()
        firma.bulut_klasor_adi = klasor_adi
        
        # Fiziksel klasörleri oluştur
        base_path = os.path.join(base_app_path, 'static', 'arsiv', klasor_adi)
        os.makedirs(os.path.join(base_path, 'PS'), exist_ok=True)
        os.makedirs(os.path.join(base_path, 'Kiralama_Formlari'), exist_ok=True)
        
        return cls.save(firma, is_new=False, actor_id=actor_id)

    @classmethod
    def get_financial_summary(cls, firma_id):
        """Firmanın tüm cari hareketlerini (Fatura, Ödeme, Kiralama) hesaplar."""
        firma = cls._get_base_query().options(
            subqueryload(Firma.kiralamalar).options(subqueryload(Kiralama.kalemler).options(joinedload(KiralamaKalemi.ekipman))),
            subqueryload(Firma.odemeler).joinedload(Odeme.kasa),
            subqueryload(Firma.hizmet_kayitlari),
        ).filter_by(id=firma_id).first()
        
        if not firma:
            raise ValidationError("Firma bulunamadı.")
            
        hareketler = []

        # Hizmet/Fatura İşlemleri
        for h in firma.hizmet_kayitlari:
            if getattr(h, 'is_deleted', False):
                continue

            if (
                getattr(h, 'ozel_id', None)
                and getattr(h, 'aciklama', '').startswith('Kiralama Bekleyen Bakiye')
                and not db.session.get(Kiralama, h.ozel_id)
            ):
                continue

            tutar = h.tutar or Decimal('0')
            
            # KESİN TESPİT: 0 veya None değilse (gerçek bir ID varsa) Kiralamadır/Nakliyedir!
            if getattr(h, 'nakliye_id', None):
                tur_adi, tur_tipi, ozel_id = 'Nakliye', 'nakliye', h.nakliye_id
            elif getattr(h, 'ozel_id', None): 
                tur_adi, tur_tipi, ozel_id = 'Kiralama', 'kiralama', h.ozel_id
            else:
                tur_tipi, ozel_id = 'fatura', h.id
                tur_adi = 'Fatura (Satış)' if h.yon == 'giden' else 'Fatura (Alış)'

            hareketler.append({
                'id': h.id, 'ozel_id': ozel_id, 'tarih': h.tarih, 'tur': tur_adi,
                'tur_tipi': tur_tipi, 'aciklama': h.aciklama, 'belge_no': h.fatura_no,
                'borc': tutar if h.yon == 'giden' else Decimal('0'),
                'alacak': tutar if h.yon == 'gelen' else Decimal('0'),
                'nesne': h
            })

        # Ödemeler
        for o in firma.odemeler:
            if getattr(o, 'is_deleted', False):
                continue

            tutar = o.tutar or Decimal('0')
            yon = getattr(o, 'yon', 'tahsilat')
            hareketler.append({
                'id': o.id, 'ozel_id': o.id, 'tarih': o.tarih,
                'tur': 'Tahsilat (Giriş)' if yon == 'tahsilat' else 'Ödeme (Çıkış)',
                'tur_tipi': 'odeme', 'aciklama': o.aciklama or 'Finansal İşlem',
                'belge_no': f"{o.kasa.kasa_adi if o.kasa else 'Kasa Tanımsız'}",
                'borc': tutar if yon == 'odeme' else Decimal('0'),
                'alacak': tutar if yon == 'tahsilat' else Decimal('0'),
                'nesne': o
            })

        # Sıralama ve Bakiye Yürütme
        hareketler.sort(key=lambda x: x['tarih'] if x['tarih'] else date.min)
        
        yuruyen_bakiye, toplam_borc, toplam_alacak = Decimal('0'), Decimal('0'), Decimal('0')
        for islem in hareketler:
            toplam_borc += islem['borc']
            toplam_alacak += islem['alacak']
            yuruyen_bakiye = (yuruyen_bakiye + islem['borc']) - islem['alacak']
            islem['kumulatif_bakiye'] = yuruyen_bakiye

        if yuruyen_bakiye > 0: 
            durum_metni, durum_rengi = "Borçlu", "text-danger"
        elif yuruyen_bakiye < 0: 
            durum_metni, durum_rengi = "Alacaklı", "text-success"
        else: 
            durum_metni, durum_rengi = "Hesap Kapalı", "text-muted"

        return {
            'firma': firma,
            'hareketler': hareketler,
            'toplam_borc': toplam_borc,
            'toplam_alacak': toplam_alacak,
            'bakiye': abs(yuruyen_bakiye),
            'durum_metni': durum_metni,
            'durum_rengi': durum_rengi
        }
    