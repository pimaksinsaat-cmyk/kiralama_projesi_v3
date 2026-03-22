from datetime import date

from wtforms import StringField, SubmitField, IntegerField, SelectField, HiddenField, FieldList, FormField, TextAreaField
from wtforms.validators import Optional, InputRequired, NumberRange, ValidationError
from decimal import Decimal
# Özel Base sınıflarınızı içe aktarıyoruz 
# (Not: Kendi dosya yolunuza göre bu import'u güncelleyebilirsiniz)
from app.forms.base_form import BaseForm, MoneyField, TRDateField 
from app.utils import secim_hata_mesaji

# 1. KALEM FORMU (Satır Bazlı Detaylar)
class KiralamaKalemiForm(BaseForm):
    class Meta: 
        csrf = False # FieldList içinde performans ve hata yönetimi için kapalı
    
    id = HiddenField('Kalem ID')
    
    # --- MAKİNE SEÇİM VE DIŞ TEDARİK ---
    dis_tedarik_ekipman = IntegerField("Dış Tedarik?", default=0)
    ekipman_id = SelectField('Pimaks Filosu', coerce=int, validators=[Optional()])
    
    # Harici Ekipman Detayları
    harici_ekipman_tedarikci_id = SelectField('Ekipman Tedarikçisi', coerce=int, default=0, validators=[Optional()])
    harici_ekipman_tipi = StringField('Harici Ekipman Tipi', validators=[Optional()])
    harici_ekipman_marka = StringField('Harici Ekipman Markası', validators=[Optional()])
    harici_ekipman_model = StringField('Harici Ekipman Modeli', validators=[Optional()])
    harici_ekipman_seri_no = StringField('Harici Seri No', validators=[Optional()])
    harici_ekipman_calisma_yuksekligi = IntegerField('Çalışma Yüksekliği (m)', validators=[Optional()])
    harici_ekipman_kaldirma_kapasitesi = IntegerField('Kaldırma Kapasitesi (kg)', validators=[Optional()])
    harici_ekipman_uretim_tarihi = IntegerField('Üretim Yılı', validators=[Optional()])
    
    # --- TARİHLER (TRDateField Kullanıldı) ---
    kiralama_baslangici = TRDateField('Başlangıç Tarihi', validators=[InputRequired()],default=date.today)
    kiralama_bitis = TRDateField('Bitiş Tarihi', validators=[InputRequired()])
    
    # --- FİYATLAR (MoneyField Kullanıldı - Virgüllü girişler artık güvende!) ---
    kiralama_brm_fiyat = MoneyField('Günlük Satış Fiyatı', validators=[InputRequired()], default='0.00')
    kiralama_alis_fiyat = MoneyField('Alış Fiyatı (Maliyet)', validators=[Optional()], default='0.00')
    
    # --- NAKLİYE ---
    dis_tedarik_nakliye = IntegerField("Harici Nakliye?", default=0)
    nakliye_satis_fiyat = MoneyField('Nakliye Satış Fiyatı', validators=[Optional()], default='0.00')
    donus_nakliye_fatura_et = IntegerField("Dönüş Nakliyesini de Fatura Et?", default=0)
    nakliye_alis_fiyat = MoneyField('Nakliye Alış Fiyatı', validators=[Optional()], default='0.00')
    nakliye_tedarikci_id = SelectField('Nakliye Tedarikçisi', coerce=int, default=0, validators=[Optional()])
    
    # ÖZ MAL NAKLİYE ARACI
    nakliye_araci_id = SelectField('Nakliye Aracı (Öz Mal)', coerce=int, default=0, validators=[Optional()])

    # --- ÖZEL DOĞRULAYICI: Tarih Kontrolü ---
    def validate_kiralama_bitis(self, field):
        if self.kiralama_baslangici.data and field.data:
            if field.data < self.kiralama_baslangici.data:
                raise ValidationError("Bitiş tarihi başlangıç tarihinden önce olamaz!")

# 2. ANA KİRALAMA FORMU
class KiralamaForm(BaseForm):
    kiralama_form_no = StringField('Kiralama Form No', validators=[Optional()])
    makine_calisma_adresi = TextAreaField('Makine Çalışma Adresi', validators=[Optional()])
    
    # Müşteri Seçimi
    firma_musteri_id = SelectField('Müşteri (Firma) Seç', coerce=int, default=0, 
                                 validators=[NumberRange(min=1, message=secim_hata_mesaji)])
    
    kdv_orani = IntegerField('KDV Oranı (%)', default=20, 
                            validators=[InputRequired(), NumberRange(min=0, max=100)])
    
    # Kur Hassasiyeti (MoneyField kullanıldı)
    doviz_kuru_usd = MoneyField('USD Kuru (TCMB)', default=Decimal('0.00'), validators=[Optional()])
    doviz_kuru_eur = MoneyField('EUR Kuru (TCMB)', default=Decimal('0.00'), validators=[Optional()])
    
    kalemler = FieldList(FormField(KiralamaKalemiForm), min_entries=1)
    submit = SubmitField('Kiralama Formunu Kaydet')