"""
EkipmanRaporuService - Makine finansal analizi ve raporlama
Makinenin satın alma maliyeti, kiralama geliri, servis masrafları ve ROI hesaplamaları
"""

from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import func, and_, or_
from app.extensions import db
from app.filo.models import Ekipman, BakimKaydi, KullanilanParca
from app.kiralama.models import Kiralama, KiralamaKalemi


class EkipmanRaporuService:
    """
    Makine finansal analizi servisi
    - Satın alma maliyeti
    - Kiralama gelirleri (dönem bazında)
    - Servis ve nakliye masrafları
    - ROI ve amorti durum hesaplamaları
    """
    
    @staticmethod
    def get_finansal_ozet(ekipman_id: int, start_date: date = None, end_date: date = None):
        """
        Makinenin finansal özetini hesaplar.
        
        Args:
            ekipman_id: Makine ID
            start_date: Başlangıç tarihi (None = min tarih)
            end_date: Bitiş tarihi (None = bugün)
            
        Returns:
            dict: Finansal özet bilgileri
        """
        ekipman = Ekipman.query.get(ekipman_id)
        if not ekipman:
            return None
        
        # Varsayılan tarih aralığı (hiç kiralama tarihi varsa)
        if end_date is None:
            end_date = date.today()
        
        # Temin maliyeti
        temin_bedeli = float(ekipman.giris_maliyeti or 0.0)
        temin_tarihi = ekipman.created_at.date() if ekipman.created_at else None
        
        # Kiralama gelirleri (TRY cinsinden, döviz kurlarıyla dönüştürülen)
        kiralama_geliri_try = EkipmanRaporuService._calculate_kirlama_geliri(
            ekipman_id, start_date, end_date
        )
        
        # Servis masrafları
        servis_giderleri_try = EkipmanRaporuService._calculate_servis_giderleri(
            ekipman_id, start_date, end_date
        )
        
        # Nakliye masrafları
        nakliye_giderleri_try = EkipmanRaporuService._calculate_nakliye_giderleri(
            ekipman_id, start_date, end_date
        )
        
        total_masraf = servis_giderleri_try + nakliye_giderleri_try
        net_gelir = kiralama_geliri_try - total_masraf
        
        # ROI Hesaplaması
        if temin_bedeli > 0:
            roi_yuzde = (net_gelir / Decimal(temin_bedeli)) * 100
        else:
            roi_yuzde = 0
        
        # Durum Belirleme
        durum = EkipmanRaporuService._determine_status(roi_yuzde)
        
        # Kiralama istatistikleri
        kiralama_stats = EkipmanRaporuService._get_kiralama_istatistikleri(
            ekipman_id, start_date, end_date
        )
        
        return {
            'ekipman_id': ekipman_id,
            'ekipman_kodu': ekipman.kod,
            'ekipman_adi': f"{ekipman.marka} - {ekipman.model}",
            'temin_bedeli': float(temin_bedeli),
            'temin_tarihi': temin_tarihi,
            'temin_doviz_kuru_usd': float(ekipman.temin_doviz_kuru_usd or 0),
            'temin_doviz_kuru_eur': float(ekipman.temin_doviz_kuru_eur or 0),
            'kiralama_geliri_try': float(kiralama_geliri_try),
            'servis_giderleri_try': float(servis_giderleri_try),
            'nakliye_giderleri_try': float(nakliye_giderleri_try),
            'toplam_giderler_try': float(total_masraf),
            'net_gelir': float(net_gelir),
            'roi_yuzde': float(roi_yuzde),
            'durum': durum,
            'start_date': start_date,
            'end_date': end_date,
            'kiralama_istatistikleri': kiralama_stats
        }
    
    @staticmethod
    def _calculate_kirlama_geliri(ekipman_id: int, start_date: date = None, end_date: date = None) -> Decimal:
        """
        Makinenin belirtilen tarih aralığında elde ettiği kiralama gelirini hesaplar.
        Döviz kurlarıyla TRY'ye dönüştürülmüş şekilde.
        """
        query = db.session.query(
            func.sum(KiralamaKalemi.kiralama_brm_fiyat).label('total_price')
        ).filter(
            KiralamaKalemi.ekipman_id == ekipman_id,
            KiralamaKalemi.is_active == True,
            KiralamaKalemi.sonlandirildi == True
        )
        
        if start_date:
            query = query.filter(KiralamaKalemi.kiralama_baslangici >= start_date)
        if end_date:
            query = query.filter(KiralamaKalemi.kiralama_bitis <= end_date)
        
        result = query.first()
        
        # Eğer sonuç yoksa 0 döndür
        if not result or result.total_price is None:
            return Decimal(0)
        
        return Decimal(result.total_price)
    
    @staticmethod
    def _calculate_servis_giderleri(ekipman_id: int, start_date: date = None, end_date: date = None) -> Decimal:
        """
        Makinenin belirtilen tarih aralığında yapılan servis masraflarını hesaplar.
        """
        # BakimKaydi → KullanilanParca → StokKarti → StokHareket
        query = db.session.query(
            func.sum(KullanilanParca.kullanilan_adet).label('total_adet')
        ).join(
            BakimKaydi, KullanilanParca.bakim_kaydi_id == BakimKaydi.id
        ).filter(
            BakimKaydi.ekipman_id == ekipman_id
        )
        
        if start_date:
            query = query.filter(BakimKaydi.tarih >= start_date)
        if end_date:
            query = query.filter(BakimKaydi.tarih <= end_date)
        
        result = query.first()
        
        # TODO: Parça birim fiyatları ile çarpılıp toplamı hesaplanmalı
        # Şimdilik sadece adet sayısı alıyoruz, gerçek implementasyonda:
        # SUM(KullanilanParca.kullanilan_adet * StokKarti.birim_fiyat)
        
        if not result or result.total_adet is None:
            return Decimal(0)
        
        # Örnek: Adet başına 100 TRY varsayalım (gerçek fiyat StokHareket'den gelmeliydi)
        return Decimal(result.total_adet or 0) * Decimal(100)
    
    @staticmethod
    def _calculate_nakliye_giderleri(ekipman_id: int, start_date: date = None, end_date: date = None) -> Decimal:
        """
        Makinenin nakliye masraflarını hesaplar (nakliye aracı olarak kullanıldığında)
        """
        query = db.session.query(
            func.sum(KiralamaKalemi.nakliye_alis_fiyat).label('total_nakliye')
        ).filter(
            KiralamaKalemi.nakliye_araci_id == ekipman_id
        )
        
        if start_date:
            query = query.filter(KiralamaKalemi.kiralama_baslangici >= start_date)
        if end_date:
            query = query.filter(KiralamaKalemi.kiralama_bitis <= end_date)
        
        result = query.first()
        
        if not result or result.total_nakliye is None:
            return Decimal(0)
        
        return Decimal(result.total_nakliye)
    
    @staticmethod
    def _determine_status(roi_yuzde: float) -> str:
        """
        ROI yüzdesine göre makine durumunu belirler
        """
        if roi_yuzde < 0:
            return "amorti_olmadi_zarar"  # Henüz amorti olmadı (zarar)
        elif roi_yuzde < 20:
            return "amorti_surecinde"  # Amorti süreci başladı
        elif roi_yuzde < 100:
            return "amorti_surecinde"  # Hala amorti süreci içinde
        elif roi_yuzde < 200:
            return "amorti_oldu"  # Kendini amorti etti
        else:
            return "kar_asamasi"  # Kâr aşamasında
    
    @staticmethod
    def _get_kiralama_istatistikleri(ekipman_id: int, start_date: date = None, end_date: date = None) -> dict:
        """
        Kiralama istatistiklerini (sayı, gün, vb) hesaplar
        """
        query = KiralamaKalemi.query.filter(
            KiralamaKalemi.ekipman_id == ekipman_id,
            KiralamaKalemi.is_active == True,
            KiralamaKalemi.sonlandirildi == True
        )
        
        if start_date:
            query = query.filter(KiralamaKalemi.kiralama_baslangici >= start_date)
        if end_date:
            query = query.filter(KiralamaKalemi.kiralama_bitis <= end_date)
        
        kiralamalar = query.all()
        
        toplam_gu = 0
        toplam_kiralama = len(kiralamalar)
        musteri_listesi = set()
        
        for kalem in kiralamalar:
            gu = (kalem.kiralama_bitis - kalem.kiralama_baslangici).days
            toplam_gu += gu
            if kalem.kiralama.firma_musteri:
                musteri_listesi.add(kalem.kiralama.firma_musteri.adi)
        
        return {
            'toplam_kiralama_sayisi': toplam_kiralama,
            'toplam_gun_sayisi': toplam_gu,
            'ortalama_gun_per_kiralama': toplam_gu / toplam_kiralama if toplam_kiralama > 0 else 0,
            'farkli_musteri_sayisi': len(musteri_listesi),
            'musteriler': list(musteri_listesi)
        }
    
    @staticmethod
    def get_kiralama_detaylari(ekipman_id: int, start_date: date = None, end_date: date = None) -> list:
        """
        Makinenin belirtilen tarih aralığındaki tüm kiralama detaylarını döner
        """
        query = KiralamaKalemi.query.filter(
            KiralamaKalemi.ekipman_id == ekipman_id,
            KiralamaKalemi.is_active == True,
            KiralamaKalemi.sonlandirildi == True
        ).join(Kiralama).order_by(KiralamaKalemi.kiralama_baslangici.desc())
        
        if start_date:
            query = query.filter(KiralamaKalemi.kiralama_baslangici >= start_date)
        if end_date:
            query = query.filter(KiralamaKalemi.kiralama_bitis <= end_date)
        
        kiralamalar = query.all()
        
        detaylar = []
        for kalem in kiralamalar:
            gu = (kalem.kiralama_bitis - kalem.kiralama_baslangici).days
            
            # Döviz cinsinden gelir (kuru ile çarpma)
            gelir_try = float(kalem.kiralama_brm_fiyat or 0)
            gelir_usd = gelir_try / float(kalem.kiralama.doviz_kuru_usd or 1) if kalem.kiralama.doviz_kuru_usd else 0
            gelir_eur = gelir_try / float(kalem.kiralama.doviz_kuru_eur or 1) if kalem.kiralama.doviz_kuru_eur else 0
            
            detaylar.append({
                'kiralama_no': kalem.kiralama.kiralama_form_no,
                'musteri': kalem.kiralama.firma_musteri.adi if kalem.kiralama.firma_musteri else '-',
                'baslangic_tarihi': kalem.kiralama_baslangici,
                'bitis_tarihi': kalem.kiralama_bitis,
                'gun_sayisi': gu,
                'gelir_try': gelir_try,
                'gelir_usd': gelir_usd,
                'gelir_eur': gelir_eur,
                'doviz_kuru_usd': float(kalem.kiralama.doviz_kuru_usd or 0),
                'doviz_kuru_eur': float(kalem.kiralama.doviz_kuru_eur or 0)
            })
        
        return detaylar
