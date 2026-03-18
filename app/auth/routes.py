# app/auth/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timezone
from app import db
from app.auth import auth_bp
from app.auth.models import User
from app.auth.forms import LoginForm
from functools import wraps
from flask import abort
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Hesabınız deaktif edilmiş.', 'danger')
                return render_template('auth/login.html', form=form)
            
            login_user(user, remember=form.beni_hatirla.data)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            
            next_page = request.args.get('next')
            flash(f'Hoş geldiniz, {user.username}!', 'success')
            return redirect(next_page or url_for('main.index'))
        
        flash('Kullanıcı adı veya şifre hatalı.', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yapıldı.', 'info')
    return redirect(url_for('auth.login'))
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/admin/kullanicilar')
@login_required
@admin_required
def kullanici_listesi():
    kullanicilar = User.query.order_by(User.username).all()
    return render_template('auth/admin.html', kullanicilar=kullanicilar)

@auth_bp.route('/admin/kullanici/ekle', methods=['POST'])
@login_required
@admin_required
def kullanici_ekle():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    rol = request.form.get('rol', 'user')
    
    if not username or not password:
        flash('Kullanıcı adı ve şifre zorunludur.', 'warning')
        return redirect(url_for('auth.kullanici_listesi'))
    
    if User.query.filter_by(username=username).first():
        flash('Bu kullanıcı adı zaten mevcut.', 'danger')
        return redirect(url_for('auth.kullanici_listesi'))
    
    yeni = User(username=username, rol=rol)
    yeni.set_password(password)
    db.session.add(yeni)
    db.session.commit()
    flash(f'{username} kullanıcısı oluşturuldu.', 'success')
    return redirect(url_for('auth.kullanici_listesi'))

@auth_bp.route('/admin/kullanici/sil/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def kullanici_sil(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == current_user.id:
        flash('Kendinizi silemezsiniz!', 'danger')
        return redirect(url_for('auth.kullanici_listesi'))
    db.session.delete(user)
    db.session.commit()
    flash(f'{user.username} silindi.', 'success')
    return redirect(url_for('auth.kullanici_listesi'))

@auth_bp.route('/admin/kullanici/sifre/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def sifre_degistir(user_id):
    user = db.get_or_404(User, user_id)
    yeni_sifre = request.form.get('yeni_sifre', '').strip()
    if not yeni_sifre or len(yeni_sifre) < 4:
        flash('Şifre en az 4 karakter olmalıdır.', 'warning')
        return redirect(url_for('auth.kullanici_listesi'))
    user.set_password(yeni_sifre)
    db.session.commit()
    flash(f'{user.username} şifresi güncellendi.', 'success')
    return redirect(url_for('auth.kullanici_listesi'))

@auth_bp.route('/admin/kullanici/rol/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def rol_degistir(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == current_user.id:
        flash('Kendi rolünüzü değiştiremezsiniz!', 'danger')
        return redirect(url_for('auth.kullanici_listesi'))
    user.rol = 'admin' if user.rol == 'user' else 'user'
    db.session.commit()
    flash(f'{user.username} rolü {user.rol} olarak güncellendi.', 'success')
    return redirect(url_for('auth.kullanici_listesi'))