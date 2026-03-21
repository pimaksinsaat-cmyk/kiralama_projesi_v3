from datetime import date
from decimal import Decimal
from uuid import uuid4
from urllib.parse import quote

from app import create_app, db
from app.auth.models import User
from app.filo.models import Ekipman
from app.firmalar.models import Firma
from app.kiralama.models import Kiralama, KiralamaKalemi
from app.services.ekipman_rapor_services import EkipmanRaporuService


def _assert(condition, message):
    if not condition:
        raise AssertionError(message)


def _ensure_admin_user():
    admin = User.query.filter_by(username="admin").first()
    if admin:
        return admin

    admin = User(username="admin", rol="admin", is_active=True)
    admin.set_password("123456")
    db.session.add(admin)
    db.session.commit()
    return admin


def _create_seed_records(suffix):
    firma = Firma(
        firma_adi=f"Test Firma {suffix}",
        yetkili_adi="Test User",
        telefon="5550000000",
        eposta=f"test-{suffix}@example.com",
        iletisim_bilgileri="Test Contact",
        vergi_dairesi="Test VD",
        vergi_no=f"VN{suffix}",
        is_musteri=True,
        is_tedarikci=False,
    )
    db.session.add(firma)
    db.session.flush()

    ekipman = Ekipman(
        kod=f"TST-{suffix}",
        yakit="Dizel",
        tipi="Platform",
        marka="TEST",
        model="M1",
        seri_no=f"SN-{suffix}",
        calisma_yuksekligi=10,
        kaldirma_kapasitesi=1000,
        uretim_yili=2024,
        calisma_durumu="bosta",
        giris_maliyeti=Decimal("500.00"),
        para_birimi="USD",
        temin_doviz_kuru_usd=Decimal("0.0000"),
        temin_doviz_kuru_eur=Decimal("0.0000"),
    )
    db.session.add(ekipman)
    db.session.flush()

    kiralama = Kiralama(
        kiralama_form_no=f"K-{suffix}",
        firma_musteri_id=firma.id,
        doviz_kuru_usd=Decimal("40.0000"),
        doviz_kuru_eur=Decimal("43.0000"),
    )
    db.session.add(kiralama)
    db.session.flush()

    kalem = KiralamaKalemi(
        kiralama_id=kiralama.id,
        ekipman_id=ekipman.id,
        kiralama_baslangici=date.today(),
        kiralama_bitis=date.today(),
        kiralama_brm_fiyat=Decimal("500.00"),
        nakliye_satis_fiyat=Decimal("0.00"),
        sonlandirildi=False,
        is_active=True,
    )
    db.session.add(kalem)
    db.session.commit()

    return firma, ekipman, kiralama, kalem


def _cleanup_records(firma, ekipman, kiralama):
    try:
        # Firma -> kiralamalar -> kalemler zinciri cascade ile temizlenir.
        if ekipman is not None:
            db.session.delete(ekipman)
        if firma is not None:
            db.session.delete(firma)
        db.session.commit()
    except Exception:
        db.session.rollback()


def test_navigation_flow(client, ekipman_id):
    return_to = f"/filo/finansal_rapor/{ekipman_id}"
    expected_gecmis_url = f"/filo/kiralama_gecmisi/{ekipman_id}?return_to={return_to}"

    r1 = client.get(f"/filo/kiralama_gecmisi/{ekipman_id}?return_to={return_to}")
    _assert(r1.status_code == 200, f"kiralama_gecmisi status expected 200, got {r1.status_code}")
    r1_html = r1.get_data(as_text=True)
    _assert(
        f"/filo/bilgi/{ekipman_id}?back=" in r1_html,
        "kiralama_gecmisi page does not contain bilgi link with back parameter"
    )
    encoded_return_to = quote(return_to, safe="")
    double_encoded_return_to = quote(encoded_return_to, safe="")
    _assert(
        (return_to in r1_html) or (encoded_return_to in r1_html) or (double_encoded_return_to in r1_html),
        "kiralama_gecmisi page does not preserve return_to value inside bilgi link"
    )

    bilgi_url = f"/filo/bilgi/{ekipman_id}?back={quote(expected_gecmis_url, safe='')}"
    r2 = client.get(bilgi_url)
    _assert(r2.status_code == 200, f"filo.bilgi status expected 200, got {r2.status_code}")
    r2_html = r2.get_data(as_text=True)
    _assert(
        f"/filo/kiralama_gecmisi/{ekipman_id}?return_to={return_to}" in r2_html,
        "filo.bilgi back button does not return to kiralama_gecmisi"
    )

    r3 = client.get(expected_gecmis_url)
    _assert(r3.status_code == 200, f"kiralama_gecmisi round-trip status expected 200, got {r3.status_code}")
    _assert(
        f'href="{return_to}"' in r3.get_data(as_text=True),
        "kiralama_gecmisi back button does not keep original return_to target"
    )



def test_financial_fx_and_day_count(ekipman_id):
    ozet = EkipmanRaporuService.get_finansal_ozet(ekipman_id, date.today(), date.today())

    _assert(ozet is not None, "financial summary is None")
    _assert(abs(float(ozet["rapor_doviz_kuru_usd"]) - 40.0) < 0.0001, "USD report rate fallback is incorrect")
    _assert(ozet["para_birimi"] == "USD", "report currency should remain USD when fallback rate exists")

    # 1-day rental should produce 500 TRY revenue (not 0)
    _assert(abs(float(ozet["kiralama_geliri_try"]) - 500.0) < 0.0001, "1-day TRY rental revenue calculation is incorrect")
    _assert(abs(float(ozet["kiralama_geliri_orijinal"]) - 12.5) < 0.0001, "USD converted revenue is incorrect")



def main():
    app = create_app()

    with app.app_context():
        admin = _ensure_admin_user()
        suffix = uuid4().hex[:10].upper()

        firma = None
        ekipman = None
        kiralama = None

        try:
            firma, ekipman, kiralama, _ = _create_seed_records(suffix)

            client = app.test_client()
            with client.session_transaction() as sess:
                sess["_user_id"] = str(admin.id)
                sess["_fresh"] = True

            test_navigation_flow(client, ekipman.id)
            test_financial_fx_and_day_count(ekipman.id)

            print("[PASS] Navigation regression test")
            print("[PASS] Financial FX + day-count regression test")
        finally:
            _cleanup_records(firma, ekipman, kiralama)


if __name__ == "__main__":
    main()
