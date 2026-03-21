from app import db, create_app
from app.subeler.models import Sube
from app.filo.models import Ekipman

app = create_app()
with app.app_context():
    try:
        print("Testing Sube query...")
        sube = Sube.query.get(1)
        print(f"[OK] Sube found: {sube.isim}")
        
        print("\nTesting bosta machines query...")
        bosta = Ekipman.query.filter_by(sube_id=1, calisma_durumu='bosta', is_active=True).all()
        print(f"[OK] Bosta machines: {len(bosta)}")
        for e in bosta:
            print(f"  - {e.kod}: {e.marka}")
        
        print("\nTesting kirada machines query...")
        kirada = Ekipman.query.filter(
            Ekipman.sube_id == 1,
            Ekipman.calisma_durumu != 'bosta',
            Ekipman.is_active == True
        ).all()
        print(f"[OK] Kirada machines: {len(kirada)}")
        for e in kirada:
            print(f"  - {e.kod}: {e.marka}")
            
        # Now try to build the response like the API does
        print("\nBuilding API response...")
        bosta_list = [{'id': e.id, 'kod': e.kod, 'marka': e.marka} for e in bosta]
        kirada_list = [{'id': e.id, 'kod': e.kod, 'marka': e.marka} for e in kirada]
        
        response_data = {
            'sube_id': sube.id,
            'sube_adi': sube.isim,
            'bosta': bosta_list,
            'kirada': kirada_list,
            'bosta_sayisi': len(bosta),
            'kirada_sayisi': len(kirada)
        }
        
        print("[OK] Response built successfully!")
        import json
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
