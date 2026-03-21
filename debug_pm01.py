from app import create_app, db
from app.filo.models import Ekipman
from app.kiralama.models import Kiralama, KiralamaKalemi
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    ekipman = Ekipman.query.filter_by(kod='PM01').first()
    print(f"✓ PM01: {ekipman.kod} (ID: {ekipman.id})\n")
    
    # KiralamaKalemi veri göster
    print("=== MEVCUT KİRALAMA KALEMLERİ ===")
    kalemler = db.session.query(KiralamaKalemi).all()
    print(f"Toplam kale: {len(kalemler)}\n")
    
    for kale in kalemler:
        print(f"ID: {kale.id}")
        print(f"  Ekipman ID: {kale.ekipman_id}")
        print(f"  Kiralama ID: {kale.kiralama_id}")
        print(f"  Kiralama Birim Fiyat: {kale.kiralama_brm_fiyat}")
        print(f"  Kiralama Alış Fiyat: {kale.kiralama_alis_fiyat}")
        print(f"  Kiralama Başlangıç: {kale.kiralama_baslangici}")
        print(f"  Kiralama Bitiş: {kale.kiralama_bitis}")
        
        if kale.ekipman_id == ekipman.id:
            print(f"  ✓ Bu PM01'e ait!")
            if kale.kiralama_alis_fiyat:
                print(f"  → Gelir: {kale.kiralama_alis_fiyat}")
        print()
