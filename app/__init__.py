# app/__init__.py
import os

from flask import Flask, request, redirect, url_for  # ← 'app' kaldırıldı
from config import Config
from flask_wtf.csrf import CSRFProtect 
from app.extensions import db, migrate, login_manager, server_session
from flask_login import current_user
from datetime import timedelta
from flask import session

csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db_url = os.getenv("DATABASE_URL")

    if db_url:
        db_url = db_url.replace("postgres://", "postgresql://")
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url



    # extensions'dan gelen nesneleri başlatıyoruz
    db.init_app(app)
    migrate.init_app(app, db)
    
    # CSRF uygulamasını başlat
    csrf.init_app(app)

    server_session.init_app(app)

    # Login Manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Bu sayfayı görmek için giriş yapmalısınız.'
    login_manager.login_message_category = 'warning'

    # Tüm uygulamayı login ile koru
    @app.before_request
    def require_login():
        acik_endpointler = ['auth.login', 'auth.logout', 'static']
        if request.endpoint in acik_endpointler:
            return None
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
    
        # Hareketsizlik kontrolü — her istekte süreyi sıfırla
        #session.permanent = True
        app.permanent_session_lifetime = timedelta(seconds=1800)

    # --- BLUEPRINT (MODÜL) KAYITLARI ---

    # 1. Ana Sayfa
    from app.main import main_bp
    app.register_blueprint(main_bp)

    # 2. Firmalar (Müşteri/Tedarikçi)
    from app.firmalar import firmalar_bp
    app.register_blueprint(firmalar_bp, url_prefix='/firmalar')

    # 3. Filo (Makine Parkı)
    from app.filo import filo_bp
    app.register_blueprint(filo_bp, url_prefix='/filo')

    # 4. Kiralama (Sözleşmeler)
    from app.kiralama import kiralama_bp
    app.register_blueprint(kiralama_bp, url_prefix='/kiralama')

    # 5. Cari (Finansal İşlemler)
    from app.cari import cari_bp
    app.register_blueprint(cari_bp, url_prefix='/cari')

    # 6. Nakliyeler
    from app.nakliyeler import nakliye_bp
    app.register_blueprint(nakliye_bp, url_prefix='/nakliyeler')

    # 7. Makine Değişim
    from app.makinedegisim import makinedegisim_bp
    app.register_blueprint(makinedegisim_bp, url_prefix='/makinedegisim')

    # 8. Dökümanlar
    from app.dokumanlar import dokumanlar_bp
    app.register_blueprint(dokumanlar_bp, url_prefix='/dokumanlar')

    # 9. Şubeler & Depolar
    from app.subeler import subeler_bp
    app.register_blueprint(subeler_bp, url_prefix='/subeler')

    # 10. Araçlar (Filo)
    from app.araclar import araclar_bp
    app.register_blueprint(araclar_bp, url_prefix='/araclar')

    # 11. Login & Kullanıcı Yönetimi
    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # 12. fatura yönetimi
    from app.fatura import fatura_bp
    app.register_blueprint(fatura_bp, url_prefix='/fatura')
    
    with app.app_context():
        from flask_migrate import upgrade
        upgrade()

    return app
    

    