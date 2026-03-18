from app import create_app, db
from app.auth.models import User 

# Uygulamayı başlat
app = create_app()

with app.app_context():
    # Veritabanında admin adında biri var mı kontrol et
    admin_var_mi = User.query.filter_by(username='admin').first()
    
    if admin_var_mi:
        print("Sistemde zaten 'admin' adında bir kullanıcı var.")
    else:
        # Yeni admin kullanıcısını modelinize tam uygun şekilde oluşturuyoruz
        # Modelinizde 'email' alanı olmadığı için onu çıkardık.
        yeni_admin = User(
            username='admin',
            rol='admin',         # Modelinizdeki yetki sütunu 'rol'
            is_active=True       # Modelinizdeki aktiflik durumu
        )
        
        # Modelinizdeki şifre belirleme fonksiyonu
        yeni_admin.set_password('123456')

        db.session.add(yeni_admin)
        db.session.commit()
        
        print("✅ Harika! Admin kullanıcısı başarıyla oluşturuldu.")
        print("👉 Kullanıcı Adı: admin")
        print("👉 Şifre: 123456")