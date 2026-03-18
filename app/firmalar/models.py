from app.extensions import db
from datetime import date
from sqlalchemy import func
from app.models.base_model import BaseModel

class Firma(BaseModel):
    """
    Sistemin ana Cari (Ledger) ve Firma modeli. 
    Tüm modüller (Stok, Kiralama, Nakliye, Cari) bu modele bağlıdır.
    """
    __tablename__ = 'firma'
    
    # --- Kimlik Bilgileri ---
    firma_adi = db.Column(db.String(150), nullable=False, index=True)
    yetkili_adi = db.Column(db.String(100), nullable=False)
    telefon = db.Column(db.String(20), nullable=True)
    eposta = db.Column(db.String(120), nullable=True, index=True)
    iletisim_bilgileri = db.Column(db.Text, nullable=False)
    vergi_dairesi = db.Column(db.String(100), nullable=False)
    vergi_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # --- Rol ve Durum ---
    is_musteri = db.Column(db.Boolean, default=True, nullable=False, index=True)
    is_tedarikci = db.Column(db.Boolean, default=False, nullable=False, index=True)
    bakiye = db.Column(db.Numeric(15, 2), default=0, nullable=False)

    # --- Sözleşme ve Operasyon ---
    sozlesme_no = db.Column(db.String(50), unique=False, nullable=True)
    sozlesme_rev_no = db.Column(db.Integer, default=0, nullable=True)
    sozlesme_tarihi = db.Column(db.Date, nullable=True, default=date.today)
    bulut_klasor_adi = db.Column(db.String(100), unique=True, nullable=True)

    # --- Denetim Alanları ---
    imza_yetkisi_kontrol_edildi = db.Column(db.Boolean, default=False, nullable=False)
    imza_yetkisi_kontrol_tarihi = db.Column(db.DateTime, nullable=True)
    imza_yetkisi_kontrol_eden_id = db.Column(db.Integer, nullable=True)
    imza_arsiv_notu = db.Column(db.String(255), nullable=True)
    # --- YENİ EKLENEN KISIM: Sadece Silinmemiş Hareketleri Getiren Özellikler ---
    @property
    def aktif_odemeler(self):
        """Silinmemiş ödeme ve tahsilatları tarihe göre yeninden eskiye sıralı getirir."""
        from app.cari.models import Odeme
        return self.odemeler.filter(Odeme.is_deleted == False).order_by(Odeme.tarih.desc()).all()

    @property
    def aktif_hizmetler(self):
        """Silinmemiş fatura ve hizmet kayıtlarını tarihe göre yeninden eskiye sıralı getirir."""
        from app.cari.models import HizmetKaydi
        return self.hizmet_kayitlari.filter(HizmetKaydi.is_deleted == False).order_by(HizmetKaydi.tarih.desc()).all()
    # -----------------------------------------------------------------------------

    # --- Ledger (Muhasebe) Hesaplama ---
    @property
    def bakiye_ozeti(self):
        """
        Dairesel importu önlemek için modelleri fonksiyon içinde çağırıyoruz.
        Hareketlerden (Odeme ve HizmetKaydi) anlık borç/alacak raporu üretir.
        """
        from app.cari.models import Odeme, HizmetKaydi 
        
        # Borç: Satış Faturaları (giden) + Kasadan Yapılan Ödemeler (odeme)
        h_borc = db.session.query(func.sum(HizmetKaydi.tutar)).filter(
            HizmetKaydi.firma_id == self.id, HizmetKaydi.yon == 'giden', HizmetKaydi.is_deleted == False
        ).scalar() or 0
        
        # Alacak: Alış Faturaları (gelen) + Müşteriden Gelen Tahsilatlar (tahsilat)
        h_alacak = db.session.query(func.sum(HizmetKaydi.tutar)).filter(
            HizmetKaydi.firma_id == self.id, HizmetKaydi.yon == 'gelen', HizmetKaydi.is_deleted == False
        ).scalar() or 0
        
        tahsilat = db.session.query(func.sum(Odeme.tutar)).filter(
            Odeme.firma_musteri_id == self.id, Odeme.yon == 'tahsilat', Odeme.is_deleted == False
        ).scalar() or 0
        
        odeme = db.session.query(func.sum(Odeme.tutar)).filter(
            Odeme.firma_musteri_id == self.id, Odeme.yon == 'odeme', Odeme.is_deleted == False
        ).scalar() or 0

        total_debit = float(h_borc + odeme)
        total_credit = float(h_alacak + tahsilat)
        
        return {
            'borc': total_debit,
            'alacak': total_credit,
            'net_bakiye': total_debit - total_credit
        }

    # --- Modüller Arası İlişkiler (Relationships) ---
    kiralamalar = db.relationship('Kiralama', back_populates='firma_musteri', foreign_keys='Kiralama.firma_musteri_id', cascade="all, delete-orphan", order_by="desc(Kiralama.id)")
    tedarik_edilen_ekipmanlar = db.relationship('Ekipman', back_populates='firma_tedarikci', foreign_keys='Ekipman.firma_tedarikci_id')
    odemeler = db.relationship('Odeme', back_populates='firma_musteri', foreign_keys='Odeme.firma_musteri_id', cascade="all, delete-orphan")
    saglanan_nakliye_hizmetleri = db.relationship('KiralamaKalemi', back_populates='nakliye_tedarikci', foreign_keys='KiralamaKalemi.nakliye_tedarikci_id')
    hizmet_kayitlari = db.relationship('HizmetKaydi', back_populates='firma', foreign_keys='HizmetKaydi.firma_id')
    tedarik_edilen_parcalar = db.relationship('StokKarti', back_populates='varsayilan_tedarikci', foreign_keys='StokKarti.varsayilan_tedarikci_id')
    stok_hareketleri = db.relationship('StokHareket', back_populates='firma', cascade="all, delete-orphan")
    nakliyeler = db.relationship('Nakliye', foreign_keys='Nakliye.firma_id', back_populates='firma', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Firma {self.firma_adi}>'