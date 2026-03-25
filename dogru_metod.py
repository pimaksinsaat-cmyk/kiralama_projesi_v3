"""
Bu dosya ekipman_rapor_services.py'deki _calculate_kirlama_geliri metodunun
düzeltilmiş versiyonudur. KiralamaKalemi.fiyat → KiralamaKalemi.kiralama_brm_fiyat
ve Kiralama.ekipman_id → KiralamaKalemi.ekipman_id olarak değiştirildi.
"""

from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import func, and_, or_
from app.extensions import db
from app.filo.models import Ekipman, BakimKaydi, KullanilanParca
from app.kiralama.models import Kiralama, KiralamaKalemi

def _calculate_kirlama_geliri_DOGRU(ekipman_id: int, start_date: date = None, end_date: date = None, 
                                     target_currency: str = 'TRY', usd_rate: float = 1, eur_rate: float = 1):
    """
    Makinenin kiralama gelirini hesaplar.
    
    DÜZELTME: 
    - KiralamaKalemi.fiyat → KiralamaKalemi.kiralama_brm_fiyat (birim fiyat)
    - Kiralama.ekipman_id yerine KiralamaKalemi.ekipman_id kullanma
    """
    # KiralamaKalemi kayıtlarını filtrele
    query = db.session.query(
        func.sum(KiralamaKalemi.kiralama_brm_fiyat)
    ).join(
        Kiralama, KiralamaKalemi.kiralama_id == Kiralama.id
    ).filter(
        KiralamaKalemi.ekipman_id == ekipman_id
    )
    
    # Tarih aralığını ekle
    if start_date:
        query = query.filter(
            or_(
                Kiralama.baslangic_tarihi >= start_date,
                Kiralama.bitis_tarihi >= start_date
            )
        )
    if end_date:
        query = query.filter(
            or_(
                Kiralama.baslangic_tarihi <= end_date,
                Kiralama.bitis_tarihi <= end_date
            )
        )
    
    result = query.scalar()
    kirlama_geliri_try = Decimal(result or 0.0)
    
    # Para birimine çevir
    if target_currency == 'USD' and usd_rate > 0:
        return kirlama_geliri_try / Decimal(usd_rate)
    elif target_currency == 'EUR' and eur_rate > 0:
        return kirlama_geliri_try / Decimal(eur_rate)
    else:
        return kirlama_geliri_try
