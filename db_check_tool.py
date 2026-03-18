# Bu araç, migration sonrası hakedis verilerinin e-fatura uyumluluğunu kontrol eder.

from app import create_app
from app.extensions import db
from app.fatura.models import Hakedis, HakedisKalemi
from sqlalchemy import func

def check_hakedis_data():
    app = create_app()
    with app.app_context():
        print("\n--- 5. Madde: Kritik Veri Kontrolü Başlatılıyor ---\n")

        # 1. Kontrol: UUID Benzersizliği ve Doluluğu
        print("[1] UUID ve Hakediş No Kontrolü:")
        all_hakedis = Hakedis.query.all()
        if not all_hakedis:
            print("(!) Henüz hakediş kaydı bulunamadı.\n")
        else:
            uuid_list = [h.uuid for h in all_hakedis]
            is_unique = len(uuid_list) == len(set(uuid_list))
            
            for h in all_hakedis:
                print(f"-> ID: {h.id} | No: {h.hakedis_no} | UUID: {h.uuid}")
            
            if is_unique:
                print("✅ Başarılı: Tüm UUID'ler benzersiz.\n")
            else:
                print("❌ HATA: Mükerrer (aynı) UUID kayıtları tespit edildi!\n")

        # 2. Kontrol: Birim Tipi Uyumluluğu (UBL-TR)
        print("[2] Birim Tipi (UBL-TR) Kontrolü:")
        distinct_units = db.session.query(HakedisKalemi.birim_tipi).distinct().all()
        
        allowed_units = ['DAY', 'MON', 'C62'] # Gün, Ay, Adet
        all_valid = True
        
        if not distinct_units:
            print("(!) Henüz hakediş kalemi bulunamadı.\n")
        else:
            for (unit,) in distinct_units:
                status = "✅" if unit in allowed_units else "❌ (Uyumsuz!)"
                print(f"-> Birim: {unit} {status}")
                if unit not in allowed_units:
                    all_valid = False
            
            if all_valid:
                print("\n✅ Başarılı: Tüm birim tipleri GİB/UBL standartlarına uygun.")
            else:
                print("\n❌ UYARI: Standart dışı birim tipleri var! e-Fatura gönderiminde hata alabilirsiniz.")

        print("\n--- Kontrol Tamamlandı ---")

if __name__ == "__main__":
    check_hakedis_data()