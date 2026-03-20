from flask import render_template, redirect, url_for, flash, request
from app.extensions import db
from . import araclar_bp
from .models import Arac
from .forms import AracForm

@araclar_bp.route('/')
def index():
    araclar = Arac.query.order_by(Arac.plaka).all()
    return render_template('araclar/index.html', araclar=araclar)

@araclar_bp.route('/ekle', methods=['GET', 'POST'])
def ekle():
    form = AracForm()
    if form.validate_on_submit():
        yeni_arac = Arac(
            plaka=form.plaka.data.upper().replace(" ", ""),
            arac_tipi=form.arac_tipi.data,
            marka_model=form.marka_model.data,
            muayene_tarihi=form.muayene_tarihi.data,
            sigorta_tarihi=form.sigorta_tarihi.data
        )
        db.session.add(yeni_arac)
        db.session.commit()
        flash(f'{yeni_arac.plaka} plakalı araç sisteme eklendi.', 'success')
        return redirect(url_for('araclar.index'))
    return render_template('araclar/ekle.html', form=form)