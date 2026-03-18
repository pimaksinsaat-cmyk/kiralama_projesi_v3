from app.extensions import db
from datetime import datetime, timezone
from sqlalchemy import func
from app.models.base_model import BaseModel


# 2. KASA (Nakit / Banka Hesapları / POS)
class Kasa(BaseModel):
    __tablename__ = 'kasa'
    
    kasa_adi = db.Column(db.String(100), nullable=False)
    tipi = db.Column(db.String(20), nullable=False, default='nakit') # nakit, banka, pos
    para_birimi = db.Column(db.String(3), nullable=False, default='TRY')
    
    # Bakiye (Performans için statik tutulur, Service katmanı tarafından güncellenir)
    bakiye = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    
    # İlişkiler
    odemeler = db.relationship('Odeme', back_populates='kasa', lazy='dynamic')
    
    @property
    def hesaplanan_bakiye(self):
        """
        Kasa hareketlerinden (Odeme) bakiye doğrulaması yapar.
        Senkronizasyon (sync-balances) işlemleri için kullanılır.
        """
        giris = db.session.query(func.sum(Odeme.tutar)).filter(
            Odeme.kasa_id == self.id, 
            Odeme.yon == 'tahsilat', 
            Odeme.is_deleted == False
        ).scalar() or 0
        
        cikis = db.session.query(func.sum(Odeme.tutar)).filter(
            Odeme.kasa_id == self.id, 
            Odeme.yon == 'odeme', 
            Odeme.is_deleted == False
        ).scalar() or 0
        
        return float(giris - cikis)
    
    def __repr__(self):
        return f'<Kasa {self.kasa_adi}>'




# 6. ODEME (Para Transferi: Tahsilat / Tediye)
class Odeme(BaseModel):
    """
    Cari Hareket: Kasaya giren veya çıkan parayı temsil eder.
    """
    __tablename__ = 'odeme'
    
    __table_args__ = (
        db.CheckConstraint("yon IN ('tahsilat', 'odeme')", name='check_odeme_yon'),
    )
    
    firma_musteri_id = db.Column(db.Integer, db.ForeignKey('firma.id'), nullable=False)
    kasa_id = db.Column(db.Integer, db.ForeignKey('kasa.id'), nullable=True)
    
    tarih = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())
    tutar = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    
    # 'tahsilat' = Kasaya Para Girişi (+) / Müşteri Bakiyesi Azalır (-)
    # 'odeme'    = Kasadan Para Çıkışı (-) / Tedarikçiye Olan Borç Azalır (+)
    yon = db.Column(db.String(20), default='tahsilat', nullable=False) 
    
    fatura_no = db.Column(db.String(50), nullable=True)
    vade_tarihi = db.Column(db.Date, nullable=True)
    aciklama = db.Column(db.String(250), nullable=True)

    # İlişkiler
    firma_musteri = db.relationship('Firma', back_populates='odemeler', foreign_keys=[firma_musteri_id])
    kasa = db.relationship('Kasa', back_populates='odemeler')
    
    def __repr__(self):
        return f'<Odeme {self.tutar} ({self.yon})>'


# 7. HIZMET KAYDI (Ticari Hareket: Gelir / Gider Faturası)
class HizmetKaydi(BaseModel):
    """
    Cari Hareket: Alınan veya verilen hizmeti temsil eder.
    """
    __tablename__ = 'hizmet_kaydi'
    
    __table_args__ = (
        db.CheckConstraint("yon IN ('gelen', 'giden')", name='check_hizmet_yon'),
    )
    
    firma_id = db.Column(db.Integer, db.ForeignKey('firma.id'), nullable=False)
    nakliye_id = db.Column(
        db.Integer, 
        db.ForeignKey('nakliye.id', ondelete='CASCADE'), 
        nullable=True
    )
    ozel_id = db.Column(db.Integer, nullable=True)
    
    tarih = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())
    tutar = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    
    # 'giden' = Satış Faturası (Gelir) -> Müşteri Borçlanır (+)
    # 'gelen' = Alış Faturası (Gider) -> Biz Tedarikçiye Borçlanırız (-)
    yon = db.Column(db.String(20), nullable=False, default='giden') 
    
    fatura_no = db.Column(db.String(50), nullable=True)
    vade_tarihi = db.Column(db.Date, nullable=True)
    aciklama = db.Column(db.String(250), nullable=True)

    # İlişkiler
    firma = db.relationship('Firma', back_populates='hizmet_kayitlari', foreign_keys=[firma_id])
    
    def __repr__(self):
        return f'<Hizmet {self.tutar} ({self.yon})>'