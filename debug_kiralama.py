#!/usr/bin/env python
from app import create_app, db
from app.filo.models import Ekipman
from app.kiralama.models import Kiralama, KiralamaKalemi
from datetime import date, timedelta

app = create_app()

with app.app_context():
    # PM01 makinesini bul
    ekipman = Ekipman.query.filter_by(kod='PM01').first()
    
    if ekipman:
        print(f"✓ Makine Bulundu: {ekipman.kod} - {ekipman.marka} {ekipman.model}")
        print(f"  Para Birimi: {ekipman.para_birimi}")
        print(f"  Giriş Maliyeti: {ekipman.giris_maliyeti}")
        print(f"  Temin USD Kuru: {ekipman.temin_doviz_kuru_usd}")
        print(f"  Temin EUR Kuru: {ekipman.temin_doviz_kuru_eur}")
        print()
        
        # KiralamaKalemi tablosunda bu ekipmanla ilgili kiralama var mı?
        kiralama_items = KiralamaKalemi.query.filter_by(ekipman_id=ekipman.id).all()
        
        print(f"Kiralama Kalemi Sayısı: {len(kiralama_items)}")
        
        if kiralama_items:
            toplam_gelir = 0
            for item in kiralama_items:
                kiralama = Kiralama.query.get(item.kiralama_id)
                print(f"\n  Kiralama #{kiralama.id}")
                print(f"    Cari: {kiralama.cari.ad}")
                print(f"    Başlangıç: {kiralama.baslangic_tarihi}")
                print(f"    Bitiş: {kiralama.bitis_tarihi if kiralama.bitis_tarihi else 'Aktif'}")
                print(f"    Başına Fiyat: {item.basinafiyat}")
                print(f"    Gün Sayısı: {item.gun_sayisi}")
                print(f"    Toplam: {item.toplam_fiyat}")
                toplam_gelir += item.toplam_fiyat or 0
            
            print(f"\n  ▶ TOPLAM KİRALAMA GELİRİ: {toplam_gelir} TRY")
        else:
            print("✗ Bu makineye ait kiralama kayıtları YOK!")
            
            # Kiralama tablısunda bu ID'nin olduğu kaydı ara
            kiralama_with_items = db.session.query(Kiralama).join(
                KiralamaKalemi, Kiralama.id == KiralamaKalemi.kiralama_id
            ).filter(KiralamaKalemi.ekipman_id == ekipman.id).all()
            
            print(f"  Sorgu sonucu: {len(kiralama_with_items)} kiralama")
    else:
        print("✗ PM01 makinesini bulamamadım")
        
        # Tüm makineleri listele
        print("\nMevcut Makineler:")
        all_machines = Ekipman.query.all()
        for m in all_machines[:10]:
            kiralama_count = KiralamaKalemi.query.filter_by(ekipman_id=m.id).count()
            print(f"  - {m.kod} ({m.marka} {m.model}) - Kiralama: {kiralama_count}")
