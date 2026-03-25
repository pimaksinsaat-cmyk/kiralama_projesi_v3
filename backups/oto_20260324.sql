PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO "alembic_version" VALUES('1a4fb16c4486');
CREATE TABLE app_settings (
	company_name VARCHAR(150) NOT NULL, 
	company_short_name VARCHAR(80), 
	logo_path VARCHAR(255) NOT NULL, 
	company_address TEXT, 
	company_phone VARCHAR(30), 
	company_email VARCHAR(120), 
	company_website VARCHAR(200), 
	invoice_title VARCHAR(150), 
	invoice_address TEXT, 
	invoice_tax_office VARCHAR(100), 
	invoice_tax_number VARCHAR(50), 
	invoice_mersis_no VARCHAR(16), 
	invoice_iban VARCHAR(64), 
	invoice_notes TEXT, 
	kiralama_form_start_no INTEGER DEFAULT '1' NOT NULL, 
	genel_sozlesme_start_no INTEGER DEFAULT '1' NOT NULL, 
	id INTEGER NOT NULL, 
	is_active BOOLEAN DEFAULT 1 NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	updated_by_id INTEGER, 
	is_deleted BOOLEAN DEFAULT 0 NOT NULL, 
	deleted_at DATETIME, 
	deleted_by_id INTEGER, kiralama_form_prefix VARCHAR(10) DEFAULT 'PF' NOT NULL, genel_sozlesme_prefix VARCHAR(10) DEFAULT 'PS' NOT NULL, 
	CONSTRAINT pk_app_settings PRIMARY KEY (id)
);
INSERT INTO "app_settings" VALUES('PIMAKS İNŞAAT TAAHHÜT VE DIŞ TIC LTD ŞTI','PIMAKS INŞAAT','uploads/settings/company_logo_d6dd58a0752a41fd9766b54ea1481a3c.jpg','İKITELLI OSGB SEFAKÖY SAN.SIT.4.BLOK NO:5 BAŞAKŞEHIR/İSTANBUL','0212 212 11 51','cuneytdemir@pimaksinsaat.com','www.pimaksinsaat.com','PIMAKS İNŞAAT TAAHHÜT VE DIŞ TIC LTD ŞTI','İKITELLI OSGB SEFAKÖY SAN.SIT.4.BLOK NO:5 BAŞAKŞEHIR/İSTANBUL','IKITELLI','7300377202','','TR','',47,32,1,1,'2026-03-22 21:44:02.140035','2026-03-23 08:51:51.646250',NULL,NULL,0,NULL,NULL,'PF','PS');
CREATE TABLE "araclar" (
	plaka VARCHAR(20) NOT NULL, 
	arac_tipi VARCHAR(50), 
	marka_model VARCHAR(100), 
	muayene_tarihi DATE, 
	sigorta_tarihi DATE, 
	is_active BOOLEAN, 
	kayit_tarihi DATETIME, 
	id INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	updated_by_id INTEGER, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at DATETIME, 
	deleted_by_id INTEGER, 
	sube_id INTEGER, 
	CONSTRAINT pk_araclar PRIMARY KEY (id), 
	CONSTRAINT fk_araclar_sube_id_subeler FOREIGN KEY(sube_id) REFERENCES subeler (id)
);
INSERT INTO "araclar" VALUES('34ERJ782','kayar kasa','mitsubishi','2027-01-13','2026-03-31',1,'2026-03-21 11:27:41.950471',1,'2026-03-21 11:27:41.950475','2026-03-21 22:21:13.430743',NULL,NULL,0,NULL,NULL,2);
INSERT INTO "araclar" VALUES('34GSP972','kayar kasa','mitsubishi','2026-04-05','2026-03-30',1,'2026-03-21 11:27:55.266198',2,'2026-03-21 11:27:55.266201','2026-03-22 16:45:19.218008',NULL,NULL,0,NULL,NULL,1);
CREATE TABLE bakim_kaydi (
	ekipman_id INTEGER NOT NULL, 
	tarih DATE NOT NULL, 
	aciklama VARCHAR(500), 
	calisma_saati INTEGER, 
	id INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	updated_by_id INTEGER, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at DATETIME, 
	deleted_by_id INTEGER, 
	CONSTRAINT pk_bakim_kaydi PRIMARY KEY (id), 
	CONSTRAINT fk_bakim_kaydi_ekipman_id_ekipman FOREIGN KEY(ekipman_id) REFERENCES ekipman (id)
);
CREATE TABLE cari_hareket (
	firma_id INTEGER NOT NULL, 
	tarih DATE NOT NULL, 
	vade_tarihi DATE, 
	para_birimi VARCHAR(3) NOT NULL, 
	yon VARCHAR(20) NOT NULL, 
	tutar NUMERIC(15, 2) NOT NULL, 
	kalan_tutar NUMERIC(15, 2) NOT NULL, 
	durum VARCHAR(10) NOT NULL, 
	kaynak_modul VARCHAR(50), 
	kaynak_id INTEGER, 
	ozel_id INTEGER, 
	belge_no VARCHAR(50), 
	aciklama VARCHAR(250), 
	referans_hareket_id INTEGER, 
	id INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	updated_by_id INTEGER, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at DATETIME, 
	deleted_by_id INTEGER, 
	CONSTRAINT pk_cari_hareket PRIMARY KEY (id), 
	CONSTRAINT ck_cari_hareket_check_cari_hareket_durum CHECK (durum IN ('acik', 'kapali', 'iptal')), 
	CONSTRAINT ck_cari_hareket_check_cari_hareket_yon CHECK (yon IN ('gelen', 'giden')), 
	CONSTRAINT fk_cari_hareket_firma_id_firma FOREIGN KEY(firma_id) REFERENCES firma (id), 
	CONSTRAINT fk_cari_hareket_referans_hareket_id_cari_hareket FOREIGN KEY(referans_hareket_id) REFERENCES cari_hareket (id)
);
CREATE TABLE cari_mahsup (
	borc_hareket_id INTEGER NOT NULL, 
	alacak_hareket_id INTEGER NOT NULL, 
	tarih DATE NOT NULL, 
	tutar NUMERIC(15, 2) NOT NULL, 
	aciklama VARCHAR(250), 
	id INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	updated_by_id INTEGER, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at DATETIME, 
	deleted_by_id INTEGER, 
	CONSTRAINT pk_cari_mahsup PRIMARY KEY (id), 
	CONSTRAINT fk_cari_mahsup_alacak_hareket_id_cari_hareket FOREIGN KEY(alacak_hareket_id) REFERENCES cari_hareket (id) ON DELETE CASCADE, 
	CONSTRAINT fk_cari_mahsup_borc_hareket_id_cari_hareket FOREIGN KEY(borc_hareket_id) REFERENCES cari_hareket (id) ON DELETE CASCADE
);
CREATE TABLE "ekipman" (
	kod VARCHAR(100) NOT NULL, 
	yakit VARCHAR(50) NOT NULL, 
	tipi VARCHAR(100) NOT NULL, 
	marka VARCHAR(100) NOT NULL, 
	model VARCHAR(100), 
	seri_no VARCHAR(100) NOT NULL, 
	calisma_yuksekligi INTEGER NOT NULL, 
	kaldirma_kapasitesi INTEGER NOT NULL, 
	agirlik FLOAT, 
	ic_mekan_uygun BOOLEAN NOT NULL, 
	genislik FLOAT, 
	uzunluk FLOAT, 
	kapali_yukseklik FLOAT, 
	uretim_yili INTEGER NOT NULL, 
	calisma_durumu VARCHAR(50) NOT NULL, 
	giris_maliyeti NUMERIC(15, 2), 
	para_birimi VARCHAR(3) NOT NULL, 
	temin_doviz_kuru_usd NUMERIC(10, 4), 
	temin_doviz_kuru_eur NUMERIC(10, 4), 
	sube_id INTEGER, 
	firma_tedarikci_id INTEGER, 
	id INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	updated_by_id INTEGER, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at DATETIME, 
	deleted_by_id INTEGER, 
	arazi_tipi_uygun BOOLEAN DEFAULT 0 NOT NULL, 
	CONSTRAINT pk_ekipman PRIMARY KEY (id), 
	CONSTRAINT fk_ekipman_sube_id_subeler FOREIGN KEY(sube_id) REFERENCES subeler (id), 
	CONSTRAINT _tedarikci_seri_no_uc UNIQUE (firma_tedarikci_id, seri_no), 
	CONSTRAINT fk_ekipman_firma_tedarikci_id_firma FOREIGN KEY(firma_tedarikci_id) REFERENCES firma (id)
);
INSERT INTO "ekipman" VALUES('PM01','Akülü','MAKAS','Mantall','XE 140W','03000994',14,350,3400.0,1,1.25,2.5,1.8,2014,'bosta',22000,'USD',0,0,2,NULL,1,1,'2026-03-21 11:21:42.921392','2026-03-22 15:21:59.055467',2,2,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM02','Akülü','MAKAS','Haulotte','COMPACT 12','CE161056',12,300,2800.0,1,1.25,2.5,1.8,2016,'kirada',12500,'EUR',0,0,2,NULL,2,1,'2026-03-21 11:22:44.298382','2026-03-23 09:25:39.174241',2,2,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM03','Akülü','MAKAS','Mantall','XE 80W','030001529',8,550,2200.0,1,1.25,2.5,1.8,2014,'bosta',15000,'USD',0,0,2,NULL,3,1,'2026-03-22 05:54:22.084870','2026-03-22 15:21:59.058728',2,2,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM04','Akülü','MAKAS','Mantall','XE 60 MINI','9000177',6,240,750.0,1,0.75,1.5,1.6,2014,'bosta',8500,'USD',0,0,1,NULL,4,1,'2026-03-22 05:58:39.633451','2026-03-22 15:21:59.059118',2,2,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM05','Akülü','MAKAS','Sinoboom','GTJZ 1412','0101700393',16,230,3500.0,1,1.25,2.5,1.8,2017,'kirada',22000,'USD',0,0,2,NULL,5,1,'2026-03-22 06:02:53.976887','2026-03-23 07:15:26.293311',2,2,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM06','Akülü','MAKAS','Sinoboom','GTJZ 1012','0101501260',12,250,720.0,1,1.25,2.5,1.8,2017,'bosta',18000,'USD',0,0,2,NULL,6,1,'2026-03-22 06:06:38.631199','2026-03-22 15:21:59.060794',2,2,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM07','Akülü','MAKAS','Sinoboom','GTJZ 0808','0101400449',10,310,2200.0,1,1.25,2.5,1.8,2017,'bosta',15000,'USD',0,0,2,NULL,7,1,'2026-03-22 06:07:16.557297','2026-03-22 15:21:59.061926',2,2,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM08','Akülü','MAKAS','Dingli','JCPT1212 HD','MS121123-2',10,320,2200.0,1,1.25,2.5,1.8,2013,'bosta',18000,'USD',0,0,2,NULL,8,1,'2026-03-22 06:11:09.487653','2026-03-22 15:21:59.063145',2,2,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM09','Akülü','MAKAS','Dingli','JCPT1212 HD','MS121123-4',12,320,2800.0,1,1.25,2.5,1.8,2013,'bosta',18000,'USD',0,0,1,NULL,9,1,'2026-03-22 06:12:02.383554','2026-03-22 15:21:59.063969',2,2,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM10','Akülü','MAKAS','Dingli','JCPT1212 HD','MS170306-100',12,320,2800.0,1,1.25,2.5,1.8,2017,'bosta',18000,'USD',0,0,2,NULL,10,1,'2026-03-22 06:12:43.403813','2026-03-22 15:21:59.064661',2,2,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM11','Akülü','MAKAS','Dingli','JCPT1212 HD','MS150307-5',12,320,2800.0,1,1.25,2.5,1.8,2015,'bosta',18000,'TRY',0,0,2,NULL,11,1,'2026-03-22 06:28:36.095080','2026-03-22 15:21:59.065328',2,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM12','Akülü','MAKAS','Haulotte','COMPACT 8','CE143974',8,230,1600.0,1,1.25,2.5,1.9,2010,'kirada',7500,'EUR',0,0,2,NULL,12,1,'2026-03-22 06:32:30.863834','2026-03-23 10:55:29.914654',2,2,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM13','Akülü','MAKAS','Haulotte','COMPACT 8','CE141377',8,350,1600.0,1,1.25,2.5,1.9,2009,'bosta',7500,'EUR',0,0,2,NULL,13,1,'2026-03-22 06:32:51.433244','2026-03-22 15:21:59.066652',2,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM14','Akülü','MAKAS','Haulotte','COMPACT 8','CE143652',8,350,1600.0,1,1.25,2.5,1.9,2010,'bosta',7500,'EUR',0,0,2,NULL,14,1,'2026-03-22 06:33:56.193972','2026-03-22 15:21:59.067299',2,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM15','Akülü','MAKAS','Haulotte','COMPACT 8','CE143760',8,350,1600.0,1,1.25,2.5,1.9,2010,'bosta',7500,'EUR',0,0,2,NULL,15,1,'2026-03-22 06:34:29.754868','2026-03-22 15:21:59.068070',2,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM16','Akülü','MAKAS','Sinoboom','GTJZ 0808S','0103815215',8,230,1600.0,1,1.25,2.5,1.8,2023,'bosta',12000,'USD',0,0,2,NULL,16,1,'2026-03-22 06:48:22.609025','2026-03-22 15:21:59.068716',2,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM17','Akülü','MAKAS','Haulotte','OPTIMIM 8','CE143551',8,230,1600.0,1,1.25,2.5,1.8,2010,'bosta',7500,'EUR',0,0,1,NULL,17,1,'2026-03-22 06:49:04.514213','2026-03-22 15:21:59.069484',2,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM18','Akülü','MAKAS','Haulotte','COMPACT 10N','CE144432',10,450,2200.0,1,1.25,2.5,1.8,2011,'bosta',9000,'EUR',0,0,2,NULL,18,1,'2026-03-22 06:50:08.072070','2026-03-22 15:21:59.070174',2,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM19','Akülü','MAKAS','Dingli','S0807AC+','JPAC125C01059',8,272,1600.0,1,1.25,2.5,1.8,2025,'bosta',12500,'USD',0,0,1,NULL,19,1,'2026-03-22 07:08:52.070165','2026-03-22 15:21:59.070810',NULL,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM20','Akülü','MAKAS','Mantall','XE120W','0331150165',12,320,2800.0,1,1.25,2.5,1.8,2015,'bosta',14000,'USD',0,0,2,NULL,20,1,'2026-03-22 08:18:13.896982','2026-03-22 15:21:59.071455',NULL,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM21','Akülü','MAKAS','Mantall','XE120W','0331150162',12,320,2800.0,1,1.25,2.5,1.8,2015,'bosta',14000,'USD',0,0,2,NULL,21,1,'2026-03-22 08:18:13.901539','2026-03-22 15:21:59.072085',NULL,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM22','Akülü','MAKAS','Haulotte','COMPACT 8','2109941',8,350,1650.0,1,1.25,2.5,1.8,2022,'bosta',13000,'EUR',0,0,1,NULL,22,1,'2026-03-22 13:54:40.969683','2026-03-22 15:21:59.072722',2,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM23','Akülü','MAKAS','Dingli','JCPT0807 HD','MS220217-8',8,350,1650.0,1,1.25,2.5,1.8,2022,'bosta',15000,'USD',0,0,2,NULL,23,1,'2026-03-22 14:02:56.056444','2026-03-22 15:21:59.073375',2,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM24','Akülü','MAKAS','Mantall','XE 120W','0331150155',12,350,2800.0,1,1.25,2.5,1.8,2015,'bosta',10000,'USD',0,0,2,NULL,24,1,'2026-03-22 14:04:55.583086','2026-03-22 15:21:59.074047',2,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM25','Akülü','MAKAS','Zoomlion','ZS0607HD','0775300001N002518',8,230,1600.0,1,1.25,2.5,1.8,2020,'bosta',8500,'USD',0,0,2,NULL,25,1,'2026-03-22 14:07:42.316121','2026-03-22 15:21:59.074697',2,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM26','Akülü','MAKAS','Sinoboom','GTJZ0608S','0103811945',8,230,1600.0,1,1.25,2.5,1.8,2022,'bosta',9500,'USD',0,0,2,NULL,26,1,'2026-03-22 14:10:40.793696','2026-03-22 15:21:59.075324',NULL,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM27','Akülü','MAKAS','Sinoboom','GTJZ0608S','0103811504',8,230,1600.0,1,1.25,2.5,1.8,2022,'bosta',9500,'USD',0,0,2,NULL,27,1,'2026-03-22 15:21:59.078618',NULL,NULL,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM28','Akülü','MAKAS','Zoomlion','ZS0808 HD','0775400000N000831',10,230,2200.0,1,1.25,2.5,1.8,2022,'bosta',10500,'USD',0,0,2,NULL,28,1,'2026-03-22 15:21:59.080068',NULL,NULL,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM29','Akülü','MAKAS','Zoomlion','ZS0808 HD','0775400000N000818',10,230,2200.0,1,1.25,2.5,1.8,2022,'bosta',10500,'USD',0,0,2,NULL,29,1,'2026-03-22 15:21:59.081044',NULL,NULL,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM30','Akülü','MAKAS','Zoomlion','ZS0808 HD','0775400000N000809',10,230,2200.0,1,1.25,2.5,1.8,2022,'bosta',10500,'USD',0,0,2,NULL,30,1,'2026-03-22 15:21:59.082017',NULL,NULL,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM31','Akülü','MAKAS','Zoomlion','ZS0808 HD','0775400000N000806',10,230,2200.0,1,1.25,2.5,1.8,2022,'bosta',10500,'USD',0,0,2,NULL,31,1,'2026-03-22 15:21:59.082983',NULL,NULL,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM32','Akülü','MAKAS','Sinoboom','GTJZ0608S','0103814467',8,230,1600.0,1,1.25,2.5,1.8,2023,'bosta',10500,'USD',0,0,2,NULL,32,1,'2026-03-22 15:21:59.083942',NULL,NULL,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM33','Akülü','MAKAS','Sinoboom','GTJZ0608S','0103814471',8,230,1600.0,1,1.25,2.5,1.8,2023,'bosta',10500,'USD',0,0,2,NULL,33,1,'2026-03-22 15:21:59.084878',NULL,NULL,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM34','Akülü','MAKAS','Sinoboom','GTJZ0608S','0103814321',8,230,1600.0,1,1.25,2.5,1.8,2023,'bosta',10500,'USD',0,0,2,NULL,34,1,'2026-03-22 15:21:59.085820',NULL,NULL,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM35','Akülü','MAKAS','Sinoboom','GTJZ0608S','0106400152',16,350,3500.0,1,1.25,2.5,1.8,2023,'bosta',22000,'USD',0,0,2,NULL,35,1,'2026-03-22 15:21:59.086749',NULL,NULL,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM36','Akülü','MAKAS','Zoomlion','ZS0407 DCS','0775200101R000615',6,240,1100.0,1,1.25,2.5,1.8,2024,'bosta',7100,'USD',0,0,2,NULL,36,1,'2026-03-22 15:21:59.088336',NULL,NULL,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM37','Akülü','MAKAS','Zoomlion','ZS0407 DCS','0775200101R000663',6,240,1100.0,1,1.25,2.5,1.8,2024,'bosta',7000,'USD',0,0,2,NULL,37,1,'2026-03-22 15:21:59.089413',NULL,NULL,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM38','Akülü','MAKAS','Zoomlion','ZS0607 HD','0775303002R000495',8,230,1600.0,1,1.25,2.5,1.8,2024,'bosta',10000,'USD',0,0,2,NULL,38,1,'2026-03-22 15:21:59.090476',NULL,NULL,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM39','Akülü','EKLEMLI PLATFORM','Zoomlion','ZA14NJE','2564300500R000035',16,230,4500.0,1,1.25,2.5,2.2,2025,'bosta',42000,'USD',0,0,2,NULL,39,1,'2026-03-22 15:21:59.091826','2026-03-22 15:34:40.780678',NULL,2,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM40','Akülü','MAKAS','Dingli','JCPT1008HA','MS211105-2',10,230,2200.0,1,1.25,2.5,2.2,2021,'bosta',9000,'USD',0,0,2,NULL,40,1,'2026-03-22 15:21:59.093262',NULL,NULL,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PM41','Akülü','MAKAS','Dingli','JCPT0607DCS','MS220318-4',6,230,1100.0,1,1.25,2.5,2.2,2022,'bosta',7500,'USD',0,0,2,NULL,41,1,'2026-03-22 15:21:59.097287',NULL,NULL,NULL,0,NULL,NULL,0);
INSERT INTO "ekipman" VALUES('PF-1','Dizel','FORKLIFT','LONKING','LG30DT','320030518729',4,3000,4500.0,1,1.5,3.25,2.2,2020,'bosta',14500,'USD',0,0,1,NULL,42,1,'2026-03-22 15:21:59.098361','2026-03-22 15:34:40.753513',NULL,2,0,NULL,NULL,1);
INSERT INTO "ekipman" VALUES('PF-2','Dizel','FORKLIFT','YGS','FD35','216012128',4,3500,5200.0,1,1.5,3.25,2.2,2020,'bosta',1100,'USD',0,0,2,NULL,43,1,'2026-03-22 15:21:59.099329','2026-03-23 09:25:39.173177',NULL,2,0,NULL,NULL,0);
CREATE TABLE firma (
	firma_adi VARCHAR(150) NOT NULL, 
	yetkili_adi VARCHAR(100) NOT NULL, 
	telefon VARCHAR(20), 
	eposta VARCHAR(120), 
	iletisim_bilgileri TEXT NOT NULL, 
	tckn VARCHAR(11), 
	mersis_no VARCHAR(16), 
	ticaret_sicil_no VARCHAR(50), 
	adres_satiri_1 VARCHAR(250), 
	adres_satiri_2 VARCHAR(250), 
	ilce VARCHAR(100), 
	il VARCHAR(100), 
	posta_kodu VARCHAR(20), 
	ulke VARCHAR(100) NOT NULL, 
	ulke_kodu VARCHAR(2) NOT NULL, 
	web_sitesi VARCHAR(200), 
	etiket_uuid VARCHAR(120), 
	is_efatura_mukellefi BOOLEAN NOT NULL, 
	vergi_dairesi VARCHAR(100) NOT NULL, 
	vergi_no VARCHAR(50) NOT NULL, 
	is_musteri BOOLEAN NOT NULL, 
	is_tedarikci BOOLEAN NOT NULL, 
	bakiye NUMERIC(15, 2) NOT NULL, 
	sozlesme_no VARCHAR(50), 
	sozlesme_rev_no INTEGER, 
	sozlesme_tarihi DATE, 
	bulut_klasor_adi VARCHAR(100), 
	imza_yetkisi_kontrol_edildi BOOLEAN NOT NULL, 
	imza_yetkisi_kontrol_tarihi DATETIME, 
	imza_yetkisi_kontrol_eden_id INTEGER, 
	imza_arsiv_notu VARCHAR(255), 
	id INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	updated_by_id INTEGER, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at DATETIME, 
	deleted_by_id INTEGER, 
	CONSTRAINT pk_firma PRIMARY KEY (id), 
	CONSTRAINT uq_firma_bulut_klasor_adi UNIQUE (bulut_klasor_adi)
);
INSERT INTO "firma" VALUES('SCM MARINE TURIZM TIC LTD.ŞTI','Bayram sayın','','','eskiçeşme mah. caferpaşa cad. no:9 bodrum/muğla',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Turkiye','TR',NULL,NULL,0,'kurumlar','7570461481',1,0,0,'PS-2026-032',0,'2026-03-23','7570461481_scm_mari',0,NULL,NULL,NULL,1,1,'2026-03-23 06:19:49.691022','2026-03-23 06:20:02.379466',2,2,0,NULL,NULL);
INSERT INTO "firma" VALUES('AHMET AKDEMIR','nizamettin aydemir','05425460868','ahmet@sahis.com','istiklal mah perçem sokak no 36 d:2 esenyurt istanbul',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Turkiye','TR',NULL,NULL,0,'tc','34109300976',1,0,0,'PS-2026-033',0,'2026-03-23','34109300976_ahmet_ak',0,NULL,NULL,NULL,2,1,'2026-03-23 08:07:22.003423','2026-03-23 10:45:55.483855',2,2,0,NULL,NULL);
INSERT INTO "firma" VALUES('ENSARİ BİLİCİ','ENSARİ BİLİCİ','05325436828','ensari@ensari.com','1332 sokak no 18/3 cumhuriyet mah ergene /tekirdağ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Turkiye','TR',NULL,NULL,0,'tc','19567310316',1,0,0,'PS-2026-034',0,'2026-03-23','19567310316_ensari_b',0,NULL,NULL,NULL,3,1,'2026-03-23 10:51:11.059211','2026-03-23 10:52:19.684559',2,2,0,NULL,NULL);
INSERT INTO "firma" VALUES('ACR PLATFORM VE MAKİNA KİRALAMA HİZ. TİC. A.Ş.','Cenk yücel','0530 108 18 06','cenkyucel@rentrise.com.tr','anadolu mah. kanuni cad. no:30 34956 orhanlı istanbul',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Turkiye','TR',NULL,NULL,0,'tuzla','0050544697',1,1,0,NULL,0,'2026-03-23',NULL,0,NULL,NULL,NULL,4,1,'2026-03-23 16:11:36.537824',NULL,2,NULL,0,NULL,NULL);
CREATE TABLE hakedis (
	hakedis_no VARCHAR(50), 
	fatura_no VARCHAR(50), 
	belge_tipi VARCHAR(20) NOT NULL, 
	firma_id INTEGER NOT NULL, 
	kiralama_id INTEGER NOT NULL, 
	proje_adi VARCHAR(200), 
	santiye_adresi TEXT, 
	baslangic_tarihi DATE NOT NULL, 
	bitis_tarihi DATE NOT NULL, 
	uuid VARCHAR(36), 
	duzenleme_tarihi DATE NOT NULL, 
	duzenleme_saati TIME NOT NULL, 
	fatura_senaryosu VARCHAR(20), 
	fatura_tipi VARCHAR(20), 
	para_birimi VARCHAR(3), 
	kur_degeri NUMERIC(10, 4), 
	siparis_referans_no VARCHAR(50), 
	siparis_referans_tarihi DATE, 
	toplam_matrah NUMERIC(15, 2), 
	toplam_kdv NUMERIC(15, 2), 
	toplam_tevkifat NUMERIC(15, 2), 
	genel_toplam NUMERIC(15, 2), 
	durum VARCHAR(20), 
	is_faturalasti BOOLEAN, 
	cari_hareket_id INTEGER, 
	id INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	updated_by_id INTEGER, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at DATETIME, 
	deleted_by_id INTEGER, 
	CONSTRAINT pk_hakedis PRIMARY KEY (id), 
	CONSTRAINT ck_hakedis_ck_hakedis_belge_tipi CHECK (belge_tipi IN ('EFATURA', 'EARSIV')), 
	CONSTRAINT ck_hakedis_ck_hakedis_durum CHECK (durum IN ('taslak', 'onaylandi', 'faturalasti', 'iptal')), 
	CONSTRAINT ck_hakedis_ck_hakedis_senaryo CHECK (fatura_senaryosu IN ('TEMELFATURA', 'TICARIFATURA')), 
	CONSTRAINT ck_hakedis_ck_hakedis_tip CHECK (fatura_tipi IN ('SATIS', 'IADE', 'TEVKIFAT', 'OZELMATRAH', 'ISTISNA')), 
	CONSTRAINT fk_hakedis_cari_hareket_id_hizmet_kaydi FOREIGN KEY(cari_hareket_id) REFERENCES hizmet_kaydi (id), 
	CONSTRAINT fk_hakedis_firma_id_firma FOREIGN KEY(firma_id) REFERENCES firma (id), 
	CONSTRAINT fk_hakedis_kiralama_id_kiralama FOREIGN KEY(kiralama_id) REFERENCES kiralama (id), 
	CONSTRAINT uq_hakedis_uuid UNIQUE (uuid)
);
CREATE TABLE hakedis_kalemi (
	hakedis_id INTEGER NOT NULL, 
	kiralama_kalemi_id INTEGER NOT NULL, 
	ekipman_id INTEGER NOT NULL, 
	mal_hizmet_adi VARCHAR(250) NOT NULL, 
	mal_hizmet_aciklama VARCHAR(500), 
	miktar NUMERIC(10, 2) NOT NULL, 
	birim_tipi VARCHAR(10), 
	birim_kodu VARCHAR(10) NOT NULL, 
	birim_fiyat NUMERIC(15, 2) NOT NULL, 
	ara_toplam NUMERIC(15, 2) NOT NULL, 
	iskonto_orani NUMERIC(5, 2), 
	iskonto_tutari NUMERIC(15, 2), 
	kdv_orani INTEGER, 
	kdv_tutari NUMERIC(15, 2), 
	tevkifat_kodu VARCHAR(10), 
	tevkifat_orani INTEGER, 
	tevkifat_pay INTEGER, 
	tevkifat_payda INTEGER, 
	tevkifat_tutari NUMERIC(15, 2), 
	ozel_matrah_tutari NUMERIC(15, 2), 
	ozel_matrah_kdv_orani INTEGER, 
	istisna_kodu VARCHAR(10), 
	istisna_nedeni VARCHAR(250), 
	satir_toplami NUMERIC(15, 2) NOT NULL, 
	id INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	updated_by_id INTEGER, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at DATETIME, 
	deleted_by_id INTEGER, 
	CONSTRAINT pk_hakedis_kalemi PRIMARY KEY (id), 
	CONSTRAINT ck_hakedis_kalemi_ck_kalem_birim CHECK (birim_tipi IN ('DAY', 'MON', 'C62', 'HUR')), 
	CONSTRAINT fk_hakedis_kalemi_ekipman_id_ekipman FOREIGN KEY(ekipman_id) REFERENCES ekipman (id), 
	CONSTRAINT fk_hakedis_kalemi_hakedis_id_hakedis FOREIGN KEY(hakedis_id) REFERENCES hakedis (id)
);
CREATE TABLE hizmet_kaydi (
	firma_id INTEGER NOT NULL, 
	nakliye_id INTEGER, 
	ozel_id INTEGER, 
	tarih DATE NOT NULL, 
	tutar NUMERIC(15, 2) NOT NULL, 
	yon VARCHAR(20) NOT NULL, 
	fatura_no VARCHAR(50), 
	vade_tarihi DATE, 
	aciklama VARCHAR(250), 
	id INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	updated_by_id INTEGER, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at DATETIME, 
	deleted_by_id INTEGER, 
	CONSTRAINT pk_hizmet_kaydi PRIMARY KEY (id), 
	CONSTRAINT ck_hizmet_kaydi_check_hizmet_yon CHECK (yon IN ('gelen', 'giden')), 
	CONSTRAINT fk_hizmet_kaydi_firma_id_firma FOREIGN KEY(firma_id) REFERENCES firma (id), 
	CONSTRAINT fk_hizmet_kaydi_nakliye_id_nakliye FOREIGN KEY(nakliye_id) REFERENCES nakliye (id) ON DELETE CASCADE
);
INSERT INTO "hizmet_kaydi" VALUES(2,NULL,2,'2026-03-23',5500,'giden','PF-2026/0049',NULL,'Kiralama Bekleyen Bakiye - PF-2026/0049',2,1,'2026-03-22 09:47:33.829120','2026-03-23 11:12:51.658550',NULL,NULL,0,NULL,NULL);
INSERT INTO "hizmet_kaydi" VALUES(1,NULL,1,'2026-03-23',4567,'giden','PF-2026/0045',NULL,'Kiralama Bekleyen Bakiye - PF-2026/0045',7,1,'2026-03-23 08:12:52.448305',NULL,NULL,NULL,0,NULL,NULL);
INSERT INTO "hizmet_kaydi" VALUES(4,6,NULL,'2026-03-23',4250,'giden',NULL,NULL,'Nakliye Hizmeti: 34ERJ782 | ikitelli - hadımköy',9,1,'2026-03-23 16:15:16.320170','2026-03-23 16:19:33.889459',NULL,NULL,0,NULL,NULL);
CREATE TABLE "kasa" (
	kasa_adi VARCHAR(100) NOT NULL, 
	tipi VARCHAR(20) NOT NULL, 
	para_birimi VARCHAR(3) NOT NULL, 
	bakiye NUMERIC(15, 2) NOT NULL, 
	id INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	updated_by_id INTEGER, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at DATETIME, 
	deleted_by_id INTEGER, 
	sube_id INTEGER, banka_sube_adi VARCHAR(120), 
	CONSTRAINT pk_kasa PRIMARY KEY (id), 
	CONSTRAINT fk_kasa_sube_id_subeler FOREIGN KEY(sube_id) REFERENCES subeler (id)
);
INSERT INTO "kasa" VALUES('Yapı Kredi Bankası','banka','TRY',0,1,1,'2026-03-22 16:01:02.331489','2026-03-22 16:15:04.631004',2,2,0,NULL,NULL,NULL,'Ataşehir');
INSERT INTO "kasa" VALUES('Kuveyt Türk','banka','TRY',0,2,1,'2026-03-22 16:05:00.260445','2026-03-22 16:15:20.087000',2,2,0,NULL,NULL,NULL,'İkitelli');
INSERT INTO "kasa" VALUES('Cenk Yücel','nakit','TRY',16000,3,1,'2026-03-23 15:56:29.671008','2026-03-23 15:57:57.903412',2,NULL,0,NULL,NULL,NULL,'İkitelli');
INSERT INTO "kasa" VALUES('Cüneyt Demir','nakit','TRY',0,4,1,'2026-03-23 15:57:00.294366','2026-03-23 16:00:14.392155',2,2,0,NULL,NULL,NULL,'İkitelli');
CREATE TABLE "kiralama" (
	kiralama_form_no VARCHAR(100) NOT NULL, 
	kdv_orani INTEGER NOT NULL, 
	doviz_kuru_usd NUMERIC(10, 4), 
	doviz_kuru_eur NUMERIC(10, 4), 
	firma_musteri_id INTEGER NOT NULL, 
	id INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	updated_by_id INTEGER, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at DATETIME, 
	deleted_by_id INTEGER, 
	makine_calisma_adresi TEXT, 
	kiralama_olusturma_tarihi DATE, 
	CONSTRAINT pk_kiralama PRIMARY KEY (id), 
	CONSTRAINT fk_kiralama_firma_musteri_id_firma FOREIGN KEY(firma_musteri_id) REFERENCES firma (id), 
	CONSTRAINT uq_kiralama_kiralama_form_no UNIQUE (kiralama_form_no)
);
INSERT INTO "kiralama" VALUES('PF-2026/0045',20,44.21,51.01,1,1,1,'2026-03-23 07:08:53.462139','2026-03-23 08:12:52.440844',2,2,0,NULL,NULL,'yakuplu west marina','2026-03-23');
INSERT INTO "kiralama" VALUES('PF-2026/0049',20,44.21,51.01,2,2,1,'2026-03-23 09:09:54.579514','2026-03-23 09:25:39.170406',2,2,0,NULL,NULL,'kuru gıda hali igtod şahintepe başakşehir istanbul','2026-03-23');
INSERT INTO "kiralama" VALUES('PF-2026/0050',20,44.21,51.01,3,3,1,'2026-03-23 10:55:29.903476','2026-03-23 10:55:38.064269',2,NULL,0,NULL,NULL,'İstoç','2026-03-23');
CREATE TABLE "kiralama_kalemi" (
	kiralama_id INTEGER NOT NULL, 
	ekipman_id INTEGER, 
	is_dis_tedarik_ekipman BOOLEAN, 
	harici_ekipman_tipi VARCHAR(100), 
	harici_ekipman_marka VARCHAR(100), 
	harici_ekipman_model VARCHAR(100), 
	harici_ekipman_seri_no VARCHAR(100), 
	harici_ekipman_kapasite INTEGER, 
	harici_ekipman_yukseklik INTEGER, 
	harici_ekipman_uretim_yili INTEGER, 
	harici_ekipman_tedarikci_id INTEGER, 
	kiralama_baslangici DATE NOT NULL, 
	kiralama_bitis DATE NOT NULL, 
	kiralama_brm_fiyat NUMERIC(15, 2) NOT NULL, 
	kiralama_alis_fiyat NUMERIC(15, 2), 
	is_oz_mal_nakliye BOOLEAN, 
	is_harici_nakliye BOOLEAN, 
	nakliye_satis_fiyat NUMERIC(15, 2), 
	nakliye_alis_fiyat NUMERIC(15, 2), 
	nakliye_tedarikci_id INTEGER, 
	nakliye_araci_id INTEGER, 
	sonlandirildi BOOLEAN NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	parent_id INTEGER, 
	versiyon_no INTEGER NOT NULL, 
	degisim_nedeni VARCHAR(50), 
	degisim_tarihi DATETIME, 
	cikis_saati INTEGER, 
	donus_saati INTEGER, 
	degisim_aciklama TEXT, 
	chain_id INTEGER, 
	id INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	updated_by_id INTEGER, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at DATETIME, 
	deleted_by_id INTEGER, 
	donus_nakliye_satis_fiyat NUMERIC(15, 2), 
	donus_nakliye_fatura_et BOOLEAN DEFAULT 0 NOT NULL, 
	CONSTRAINT pk_kiralama_kalemi PRIMARY KEY (id), 
	CONSTRAINT fk_kiralama_kalemi_ekipman_id_ekipman FOREIGN KEY(ekipman_id) REFERENCES ekipman (id), 
	CONSTRAINT fk_kiralama_kalemi_parent_id_kiralama_kalemi FOREIGN KEY(parent_id) REFERENCES kiralama_kalemi (id), 
	CONSTRAINT fk_kiralama_kalemi_nakliye_tedarikci_id_firma FOREIGN KEY(nakliye_tedarikci_id) REFERENCES firma (id), 
	CONSTRAINT fk_kiralama_kalemi_nakliye_araci_id_ekipman FOREIGN KEY(nakliye_araci_id) REFERENCES ekipman (id), 
	CONSTRAINT fk_kiralama_kalemi_kiralama_id_kiralama FOREIGN KEY(kiralama_id) REFERENCES kiralama (id), 
	CONSTRAINT fk_kiralama_kalemi_harici_ekipman_tedarikci_id_firma FOREIGN KEY(harici_ekipman_tedarikci_id) REFERENCES firma (id)
);
INSERT INTO "kiralama_kalemi" VALUES(1,5,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-03-23','2026-04-21',1067,0,1,0,3500,0,NULL,NULL,0,1,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,1,'2026-03-23 07:08:53.466410','2026-03-23 08:12:52.442936',2,2,0,NULL,NULL,NULL,0);
INSERT INTO "kiralama_kalemi" VALUES(2,2,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-03-23','2026-04-06',500,0,1,0,5000,0,NULL,NULL,0,1,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,2,'2026-03-23 09:09:54.584424','2026-03-23 09:25:39.173967',2,2,0,NULL,NULL,NULL,1);
INSERT INTO "kiralama_kalemi" VALUES(3,12,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-03-24','2026-04-22',400,0,1,0,4000,0,NULL,1,0,1,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,3,'2026-03-23 10:55:29.912465',NULL,2,NULL,0,NULL,NULL,NULL,1);
CREATE TABLE kullanilan_parca (
	bakim_kaydi_id INTEGER NOT NULL, 
	stok_karti_id INTEGER NOT NULL, 
	kullanilan_adet INTEGER NOT NULL, 
	id INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	updated_by_id INTEGER, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at DATETIME, 
	deleted_by_id INTEGER, 
	CONSTRAINT pk_kullanilan_parca PRIMARY KEY (id), 
	CONSTRAINT fk_kullanilan_parca_bakim_kaydi_id_bakim_kaydi FOREIGN KEY(bakim_kaydi_id) REFERENCES bakim_kaydi (id), 
	CONSTRAINT fk_kullanilan_parca_stok_karti_id_stok_karti FOREIGN KEY(stok_karti_id) REFERENCES stok_karti (id)
);
CREATE TABLE makine_degisim (
	kiralama_id INTEGER NOT NULL, 
	eski_kalem_id INTEGER NOT NULL, 
	yeni_kalem_id INTEGER NOT NULL, 
	eski_ekipman_id INTEGER, 
	yeni_ekipman_id INTEGER, 
	neden VARCHAR(50) NOT NULL, 
	tarih DATETIME NOT NULL, 
	aciklama TEXT, 
	eski_ekipman_donus_saati INTEGER, 
	yeni_ekipman_cikis_saati INTEGER, 
	servis_kayit_id INTEGER, 
	id INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	updated_by_id INTEGER, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at DATETIME, 
	deleted_by_id INTEGER, 
	CONSTRAINT pk_makine_degisim PRIMARY KEY (id), 
	CONSTRAINT fk_makine_degisim_eski_ekipman_id_ekipman FOREIGN KEY(eski_ekipman_id) REFERENCES ekipman (id), 
	CONSTRAINT fk_makine_degisim_eski_kalem_id_kiralama_kalemi FOREIGN KEY(eski_kalem_id) REFERENCES kiralama_kalemi (id), 
	CONSTRAINT fk_makine_degisim_kiralama_id_kiralama FOREIGN KEY(kiralama_id) REFERENCES kiralama (id), 
	CONSTRAINT fk_makine_degisim_yeni_ekipman_id_ekipman FOREIGN KEY(yeni_ekipman_id) REFERENCES ekipman (id), 
	CONSTRAINT fk_makine_degisim_yeni_kalem_id_kiralama_kalemi FOREIGN KEY(yeni_kalem_id) REFERENCES kiralama_kalemi (id)
);
CREATE TABLE nakliye (
	kiralama_id INTEGER, 
	id INTEGER NOT NULL, 
	tarih DATE NOT NULL, 
	firma_id INTEGER NOT NULL, 
	nakliye_tipi VARCHAR(20), 
	arac_id INTEGER, 
	taseron_firma_id INTEGER, 
	guzergah VARCHAR(200) NOT NULL, 
	plaka VARCHAR(20), 
	aciklama TEXT, 
	tutar NUMERIC(15, 2) NOT NULL, 
	kdv_orani INTEGER, 
	toplam_tutar NUMERIC(15, 2) NOT NULL, 
	taseron_maliyet NUMERIC(15, 2), 
	cari_islendi_mi BOOLEAN, 
	is_active BOOLEAN NOT NULL, 
	CONSTRAINT pk_nakliye PRIMARY KEY (id), 
	CONSTRAINT fk_nakliye_arac_id_araclar FOREIGN KEY(arac_id) REFERENCES araclar (id), 
	CONSTRAINT fk_nakliye_firma_id_firma FOREIGN KEY(firma_id) REFERENCES firma (id), 
	CONSTRAINT fk_nakliye_kiralama_id_kiralama FOREIGN KEY(kiralama_id) REFERENCES kiralama (id) ON DELETE CASCADE, 
	CONSTRAINT fk_nakliye_taseron_firma_id_firma FOREIGN KEY(taseron_firma_id) REFERENCES firma (id)
);
INSERT INTO "nakliye" VALUES(1,3,'2026-03-23',1,'oz_mal',NULL,NULL,'PM05 İkitelli şubesinden SCM MARINE TURIZM TIC LTD.ŞTI firmasının yakuplu west marina''ne götürüldü',NULL,'Gidiş: PF-2026/0045',3500,20,3500,0,0,1);
INSERT INTO "nakliye" VALUES(2,4,'2026-03-23',2,'oz_mal',NULL,NULL,'PM02 İkitelli şubesinden AHMET AKDEMIR firmasının kuru gıda hali igtod şahintepe başakşehir istanbul''ne götürüldü',NULL,'Gidiş: PF-2026/0049',2500,20,2500,0,0,1);
INSERT INTO "nakliye" VALUES(3,5,'2026-03-24',3,'oz_mal',1,NULL,'PM12 İkitelli şubesinden ENSARİ BİLİCİ firmasının İstoç''ne götürüldü','34ERJ782','Gidiş: PF-2026/0050',2000,20,2000,0,0,1);
INSERT INTO "nakliye" VALUES(NULL,6,'2026-03-23',4,'oz_mal',1,0,'ikitelli - hadımköy','34ERJ782','intermat hadımköye C14 götürüldü',4250,20,4250,0,0,1);
CREATE TABLE odeme (
	firma_musteri_id INTEGER NOT NULL, 
	kasa_id INTEGER, 
	tarih DATE NOT NULL, 
	tutar NUMERIC(15, 2) NOT NULL, 
	yon VARCHAR(20) NOT NULL, 
	fatura_no VARCHAR(50), 
	vade_tarihi DATE, 
	aciklama VARCHAR(250), 
	id INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	updated_by_id INTEGER, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at DATETIME, 
	deleted_by_id INTEGER, 
	CONSTRAINT pk_odeme PRIMARY KEY (id), 
	CONSTRAINT ck_odeme_check_odeme_yon CHECK (yon IN ('tahsilat', 'odeme')), 
	CONSTRAINT fk_odeme_firma_musteri_id_firma FOREIGN KEY(firma_musteri_id) REFERENCES firma (id), 
	CONSTRAINT fk_odeme_kasa_id_kasa FOREIGN KEY(kasa_id) REFERENCES kasa (id)
);
INSERT INTO "odeme" VALUES(3,3,'2026-03-23',16000,'tahsilat','',NULL,'',1,1,'2026-03-23 15:57:57.889958',NULL,2,NULL,0,NULL,NULL);
CREATE TABLE operation_log (
	id INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	user_id INTEGER, 
	username VARCHAR(80), 
	module VARCHAR(80) NOT NULL, 
	action VARCHAR(80) NOT NULL, 
	entity_type VARCHAR(80), 
	entity_id INTEGER, 
	success BOOLEAN NOT NULL, 
	description TEXT, 
	ip_address VARCHAR(64), 
	request_path VARCHAR(255), 
	CONSTRAINT pk_operation_log PRIMARY KEY (id)
);
INSERT INTO "operation_log" VALUES(1,'2026-03-22 13:56:23.119187',2,'cuneytdemir','kiralama','create','Kiralama',3,1,'Kiralama oluşturuldu: PF-2026/0003','127.0.0.1','/kiralama/ekle');
INSERT INTO "operation_log" VALUES(2,'2026-03-22 13:56:49.345343',2,'cuneytdemir','kiralama','delete','Kiralama',1,1,'Kiralama silindi (soft/hard): ID=1','127.0.0.1','/kiralama/sil/1');
INSERT INTO "operation_log" VALUES(3,'2026-03-22 13:59:39.476048',2,'cuneytdemir','kiralama','sonlandir_kalem','KiralamaKalemi',4,1,'Kiralama kalemi sonlandırıldı: kalem_id=4','127.0.0.1','/kiralama/kalem/sonlandir');
INSERT INTO "operation_log" VALUES(4,'2026-03-22 14:02:56.065405',2,'cuneytdemir','filo','create','Ekipman',23,1,'PM23 makine eklendi.','127.0.0.1','/filo/ekle');
INSERT INTO "operation_log" VALUES(5,'2026-03-22 14:04:55.593111',2,'cuneytdemir','filo','create','Ekipman',24,1,'PM24 makine eklendi.','127.0.0.1','/filo/ekle');
INSERT INTO "operation_log" VALUES(6,'2026-03-22 14:07:42.322708',2,'cuneytdemir','filo','create','Ekipman',25,1,'PM25 makine eklendi.','127.0.0.1','/filo/ekle');
INSERT INTO "operation_log" VALUES(7,'2026-03-22 15:22:51.150005',2,'cuneytdemir','filo','update','Ekipman',39,1,'PM39 makine bilgileri güncellendi.','127.0.0.1','/filo/duzelt/39');
INSERT INTO "operation_log" VALUES(8,'2026-03-22 15:23:19.973025',2,'cuneytdemir','filo','update','Ekipman',42,1,'PF-1 makine bilgileri güncellendi.','127.0.0.1','/filo/duzelt/42');
INSERT INTO "operation_log" VALUES(9,'2026-03-22 15:23:47.263207',2,'cuneytdemir','filo','update','Ekipman',43,1,'PF-2 makine bilgileri güncellendi.','127.0.0.1','/filo/duzelt/43');
INSERT INTO "operation_log" VALUES(10,'2026-03-22 15:23:54.047605',2,'cuneytdemir','filo','update','Ekipman',42,1,'PF-1 makine bilgileri güncellendi.','127.0.0.1','/filo/duzelt/42');
INSERT INTO "operation_log" VALUES(11,'2026-03-22 16:01:02.340377',2,'cuneytdemir','cari','kasa_ekle','Kasa',1,1,'Yapı Kredi Bankası kasası oluşturuldu.','127.0.0.1','/cari/kasa/ekle');
INSERT INTO "operation_log" VALUES(12,'2026-03-22 16:05:00.270460',2,'cuneytdemir','cari','kasa_ekle','Kasa',2,1,'Kuveyt Türk kasası oluşturuldu.','127.0.0.1','/cari/kasa/ekle');
INSERT INTO "operation_log" VALUES(13,'2026-03-22 16:11:02.094725',2,'cuneytdemir','nakliyeler','create','Nakliye',5,1,'Nakliye seferi eklendi (#5).','127.0.0.1','/nakliyeler/ekle');
INSERT INTO "operation_log" VALUES(14,'2026-03-22 16:15:04.641692',2,'cuneytdemir','cari','kasa_duzelt','Kasa',1,1,'Kasa #1 (Yapı Kredi Bankası) güncellendi.','127.0.0.1','/cari/kasa/duzelt/1');
INSERT INTO "operation_log" VALUES(15,'2026-03-22 16:15:20.093682',2,'cuneytdemir','cari','kasa_duzelt','Kasa',2,1,'Kasa #2 (Kuveyt Türk) güncellendi.','127.0.0.1','/cari/kasa/duzelt/2');
INSERT INTO "operation_log" VALUES(16,'2026-03-22 17:04:26.311973',2,'cuneytdemir','dokumanlar','kiralama_formu_yazdir_pdf','Kiralama',2,1,'Kiralama formu PDF üretildi: PF-2026_0002','127.0.0.1','/dokumanlar/yazdir/form/2');
INSERT INTO "operation_log" VALUES(17,'2026-03-22 20:20:42.146361',2,'cuneytdemir','kiralama','create','Kiralama',4,1,'Kiralama oluşturuldu: PF-2026/0004','127.0.0.1','/kiralama/ekle');
INSERT INTO "operation_log" VALUES(18,'2026-03-22 20:59:22.364774',2,'cuneytdemir','kiralama','update','Kiralama',4,1,'Kiralama güncellendi: PF-2026/0004','127.0.0.1','/kiralama/duzenle/4');
INSERT INTO "operation_log" VALUES(19,'2026-03-22 22:49:56.319466',2,'cuneytdemir','dokumanlar','kiralama_formu_yazdir_pdf','Kiralama',2,1,'Kiralama formu PDF üretildi: PF-2026_0002','127.0.0.1','/dokumanlar/yazdir/form/2');
INSERT INTO "operation_log" VALUES(20,'2026-03-23 06:22:40.148689',2,'cuneytdemir','kiralama','create','Kiralama',1,1,'Kiralama oluşturuldu: PF-2026/0045','127.0.0.1','/kiralama/ekle');
INSERT INTO "operation_log" VALUES(21,'2026-03-23 06:29:16.380733',2,'cuneytdemir','filo','update','Ekipman',5,1,'PM05 makine bilgileri güncellendi.','127.0.0.1','/filo/duzelt/5');
INSERT INTO "operation_log" VALUES(22,'2026-03-23 06:29:30.787782',2,'cuneytdemir','kiralama','delete','Kiralama',1,1,'Kiralama silindi (soft/hard): ID=1','127.0.0.1','/kiralama/sil/1');
INSERT INTO "operation_log" VALUES(23,'2026-03-23 06:30:15.281261',2,'cuneytdemir','kiralama','create','Kiralama',1,1,'Kiralama oluşturuldu: PF-2026/0045','127.0.0.1','/kiralama/ekle');
INSERT INTO "operation_log" VALUES(24,'2026-03-23 06:36:48.081728',2,'cuneytdemir','filo','update','Ekipman',5,1,'PM05 makine bilgileri güncellendi.','127.0.0.1','/filo/duzelt/5');
INSERT INTO "operation_log" VALUES(25,'2026-03-23 07:08:53.484064',2,'cuneytdemir','kiralama','create','Kiralama',1,1,'Kiralama oluşturuldu: PF-2026/0045','127.0.0.1','/kiralama/ekle');
INSERT INTO "operation_log" VALUES(26,'2026-03-23 07:09:41.104837',2,'cuneytdemir','dokumanlar','kiralama_formu_yazdir_pdf','Kiralama',1,1,'Kiralama formu PDF üretildi: PF-2026_0045','127.0.0.1','/dokumanlar/yazdir/form/1');
INSERT INTO "operation_log" VALUES(27,'2026-03-23 07:11:19.087469',2,'cuneytdemir','kiralama','sonlandir_kalem','KiralamaKalemi',1,1,'Kiralama kalemi sonlandırıldı: kalem_id=1','127.0.0.1','/kiralama/kalem/sonlandir');
INSERT INTO "operation_log" VALUES(28,'2026-03-23 07:12:03.798524',2,'cuneytdemir','kiralama','iptal_sonlandirma','KiralamaKalemi',1,1,'Kalem sonlandırma iptal edildi: kalem_id=1','127.0.0.1','/kiralama/kalem/iptal_et');
INSERT INTO "operation_log" VALUES(29,'2026-03-23 07:15:14.598717',2,'cuneytdemir','kiralama','sonlandir_kalem','KiralamaKalemi',1,1,'Kiralama kalemi sonlandırıldı: kalem_id=1','127.0.0.1','/kiralama/kalem/sonlandir');
INSERT INTO "operation_log" VALUES(30,'2026-03-23 07:15:26.304291',2,'cuneytdemir','kiralama','iptal_sonlandirma','KiralamaKalemi',1,1,'Kalem sonlandırma iptal edildi: kalem_id=1','127.0.0.1','/kiralama/kalem/iptal_et');
INSERT INTO "operation_log" VALUES(31,'2026-03-23 08:12:27.481308',2,'cuneytdemir','kiralama','create','Kiralama',2,1,'Kiralama oluşturuldu: PF-2026/0046','127.0.0.1','/kiralama/ekle');
INSERT INTO "operation_log" VALUES(32,'2026-03-23 08:12:52.453375',2,'cuneytdemir','kiralama','update','Kiralama',1,1,'Kiralama güncellendi: PF-2026/0045','127.0.0.1','/kiralama/duzenle/1');
INSERT INTO "operation_log" VALUES(33,'2026-03-23 08:50:34.631507',2,'cuneytdemir','kiralama','delete','Kiralama',2,1,'Kiralama silindi (soft/hard): ID=2','127.0.0.1','/kiralama/sil/2');
INSERT INTO "operation_log" VALUES(34,'2026-03-23 08:51:27.012756',2,'cuneytdemir','kiralama','create','Kiralama',2,1,'Kiralama oluşturuldu: PF-2026/0046','127.0.0.1','/kiralama/ekle');
INSERT INTO "operation_log" VALUES(35,'2026-03-23 08:52:32.766155',2,'cuneytdemir','kiralama','delete','Kiralama',2,1,'Kiralama silindi (soft/hard): ID=2','127.0.0.1','/kiralama/sil/2');
INSERT INTO "operation_log" VALUES(36,'2026-03-23 09:09:54.609121',2,'cuneytdemir','kiralama','create','Kiralama',2,1,'Kiralama oluşturuldu: PF-2026/0049','127.0.0.1','/kiralama/ekle');
INSERT INTO "operation_log" VALUES(37,'2026-03-23 09:13:59.389250',2,'cuneytdemir','kiralama','update','Kiralama',2,1,'Kiralama güncellendi: PF-2026/0049','127.0.0.1','/kiralama/duzenle/2');
INSERT INTO "operation_log" VALUES(38,'2026-03-23 09:25:39.184667',2,'cuneytdemir','kiralama','update','Kiralama',2,1,'Kiralama güncellendi: PF-2026/0049','127.0.0.1','/kiralama/duzenle/2');
INSERT INTO "operation_log" VALUES(39,'2026-03-23 09:28:21.878494',2,'cuneytdemir','dokumanlar','kiralama_formu_yazdir_pdf','Kiralama',2,1,'Kiralama formu PDF üretildi: PF-2026_0049','127.0.0.1','/dokumanlar/yazdir/form/2');
INSERT INTO "operation_log" VALUES(40,'2026-03-23 09:32:59.204540',2,'cuneytdemir','dokumanlar','kiralama_formu_yazdir_docx_fallback','Kiralama',2,0,'PDF üretilemedi, DOCX gönderildi: PF-2026_0049','127.0.0.1','/dokumanlar/yazdir/form/2');
INSERT INTO "operation_log" VALUES(41,'2026-03-23 09:33:07.769382',2,'cuneytdemir','dokumanlar','kiralama_formu_yazdir_hata','Kiralama',2,0,'Kiralama formu yazdırma hatası: [Errno 13] Permission denied: "C:\\Users\\cuney\\Drive''ım\\kiralama_projesi_v3\\app\\static\\arsiv\\Genel_Arsiv\\Formlar\\PF-2026_0049_Form.docx"','127.0.0.1','/dokumanlar/yazdir/form/2');
INSERT INTO "operation_log" VALUES(42,'2026-03-23 09:33:37.515112',2,'cuneytdemir','dokumanlar','kiralama_formu_yazdir_hata','Kiralama',2,0,'Kiralama formu yazdırma hatası: [Errno 13] Permission denied: "C:\\Users\\cuney\\Drive''ım\\kiralama_projesi_v3\\app\\static\\arsiv\\Genel_Arsiv\\Formlar\\PF-2026_0049_Form.docx"','127.0.0.1','/dokumanlar/yazdir/form/2');
INSERT INTO "operation_log" VALUES(43,'2026-03-23 09:34:26.488575',2,'cuneytdemir','dokumanlar','kiralama_formu_yazdir_pdf','Kiralama',2,1,'Kiralama formu PDF üretildi: PF-2026_0049','127.0.0.1','/dokumanlar/yazdir/form/2');
INSERT INTO "operation_log" VALUES(44,'2026-03-23 10:46:48.003359',2,'cuneytdemir','dokumanlar','kiralama_formu_yazdir_pdf','Kiralama',2,1,'Kiralama formu PDF üretildi: PF-2026_0049','127.0.0.1','/dokumanlar/yazdir/form/2');
INSERT INTO "operation_log" VALUES(45,'2026-03-23 10:55:29.942339',2,'cuneytdemir','kiralama','create','Kiralama',3,1,'Kiralama oluşturuldu: PF-2026/0050','127.0.0.1','/kiralama/ekle');
INSERT INTO "operation_log" VALUES(46,'2026-03-23 10:55:47.135141',2,'cuneytdemir','dokumanlar','kiralama_formu_yazdir_pdf','Kiralama',3,1,'Kiralama formu PDF üretildi: PF-2026_0050','127.0.0.1','/dokumanlar/yazdir/form/3');
INSERT INTO "operation_log" VALUES(47,'2026-03-23 15:56:29.682289',2,'cuneytdemir','cari','kasa_ekle','Kasa',3,1,'Cenk Yücel kasası oluşturuldu.','127.0.0.1','/cari/kasa/ekle');
INSERT INTO "operation_log" VALUES(48,'2026-03-23 15:57:00.305842',2,'cuneytdemir','cari','kasa_ekle','Kasa',4,1,'Cüneyt Demir kasası oluşturuldu.','127.0.0.1','/cari/kasa/ekle');
INSERT INTO "operation_log" VALUES(49,'2026-03-23 15:57:57.915364',2,'cuneytdemir','cari','odeme_ekle','Odeme',1,1,'TAHSILAT 16000.00 - ','127.0.0.1','/cari/odeme/ekle');
INSERT INTO "operation_log" VALUES(50,'2026-03-23 16:00:14.402009',2,'cuneytdemir','cari','kasa_duzelt','Kasa',4,1,'Kasa #4 (Cüneyt Demir) güncellendi.','127.0.0.1','/cari/kasa/duzelt/4');
INSERT INTO "operation_log" VALUES(51,'2026-03-23 16:15:16.330904',2,'cuneytdemir','nakliyeler','create','Nakliye',6,1,'Nakliye seferi eklendi (#6).','127.0.0.1','/nakliyeler/ekle');
INSERT INTO "operation_log" VALUES(52,'2026-03-23 16:19:33.902127',2,'cuneytdemir','nakliyeler','update','Nakliye',6,1,'Nakliye #6 güncellendi.','127.0.0.1','/nakliyeler/duzenle/6');
CREATE TABLE stok_hareket (
	stok_karti_id INTEGER NOT NULL, 
	firma_id INTEGER, 
	tarih DATE NOT NULL, 
	adet INTEGER NOT NULL, 
	birim_fiyat NUMERIC(15, 2) NOT NULL, 
	hareket_tipi VARCHAR(20) NOT NULL, 
	fatura_no VARCHAR(50), 
	aciklama VARCHAR(250), 
	id INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	updated_by_id INTEGER, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at DATETIME, 
	deleted_by_id INTEGER, 
	CONSTRAINT pk_stok_hareket PRIMARY KEY (id), 
	CONSTRAINT fk_stok_hareket_firma_id_firma FOREIGN KEY(firma_id) REFERENCES firma (id), 
	CONSTRAINT fk_stok_hareket_stok_karti_id_stok_karti FOREIGN KEY(stok_karti_id) REFERENCES stok_karti (id)
);
CREATE TABLE stok_karti (
	parca_kodu VARCHAR(100) NOT NULL, 
	parca_adi VARCHAR(250) NOT NULL, 
	mevcut_stok INTEGER NOT NULL, 
	varsayilan_tedarikci_id INTEGER, 
	id INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	updated_by_id INTEGER, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at DATETIME, 
	deleted_by_id INTEGER, 
	CONSTRAINT pk_stok_karti PRIMARY KEY (id), 
	CONSTRAINT fk_stok_karti_varsayilan_tedarikci_id_firma FOREIGN KEY(varsayilan_tedarikci_id) REFERENCES firma (id)
);
CREATE TABLE sube_transferleri (
	id INTEGER NOT NULL, 
	tarih DATETIME, 
	ekipman_id INTEGER NOT NULL, 
	gonderen_sube_id INTEGER NOT NULL, 
	alan_sube_id INTEGER NOT NULL, 
	arac_id INTEGER NOT NULL, 
	neden VARCHAR(50) NOT NULL, 
	aciklama TEXT, 
	CONSTRAINT pk_sube_transferleri PRIMARY KEY (id), 
	CONSTRAINT fk_sube_transferleri_alan_sube_id_subeler FOREIGN KEY(alan_sube_id) REFERENCES subeler (id), 
	CONSTRAINT fk_sube_transferleri_arac_id_araclar FOREIGN KEY(arac_id) REFERENCES araclar (id), 
	CONSTRAINT fk_sube_transferleri_ekipman_id_ekipman FOREIGN KEY(ekipman_id) REFERENCES ekipman (id), 
	CONSTRAINT fk_sube_transferleri_gonderen_sube_id_subeler FOREIGN KEY(gonderen_sube_id) REFERENCES subeler (id)
);
CREATE TABLE subeler (
	id INTEGER NOT NULL, 
	isim VARCHAR(100) NOT NULL, 
	adres TEXT, 
	konum_linki VARCHAR(500), 
	yetkili_kisi VARCHAR(100), 
	telefon VARCHAR(20), 
	email VARCHAR(100), 
	is_active BOOLEAN, 
	CONSTRAINT pk_subeler PRIMARY KEY (id)
);
INSERT INTO "subeler" VALUES(1,'Ferhatpaşa','','','Salih Baltacı','05322305573','pimaksinsaat@gmail.com',1);
INSERT INTO "subeler" VALUES(2,'İkitelli','','','Cüneyt Demir','05322305573','pimaksinsaat@gmail.com',1);
CREATE TABLE takvim_hatirlatma (
	user_id INTEGER NOT NULL, 
	tarih DATE NOT NULL, 
	baslik VARCHAR(150) NOT NULL, 
	aciklama TEXT, 
	id INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	created_by_id INTEGER, 
	updated_by_id INTEGER, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at DATETIME, 
	deleted_by_id INTEGER, 
	CONSTRAINT pk_takvim_hatirlatma PRIMARY KEY (id), 
	CONSTRAINT fk_takvim_hatirlatma_user_id_user FOREIGN KEY(user_id) REFERENCES user (id)
);
INSERT INTO "takvim_hatirlatma" VALUES(2,'2026-03-24','deneme',NULL,1,0,'2026-03-22 16:32:50.726121','2026-03-22 16:35:32.388105',2,NULL,1,NULL,2);
INSERT INTO "takvim_hatirlatma" VALUES(2,'2026-03-24','pm06 obaya gidecek',NULL,2,0,'2026-03-23 07:51:08.023767','2026-03-23 07:51:18.885017',2,NULL,1,NULL,2);
CREATE TABLE user (
	id INTEGER NOT NULL, 
	username VARCHAR(80) NOT NULL, 
	password_hash VARCHAR(256) NOT NULL, 
	rol VARCHAR(20) NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME, 
	last_login DATETIME, 
	CONSTRAINT pk_user PRIMARY KEY (id)
);
INSERT INTO "user" VALUES(1,'admin','scrypt:32768:8:1$QSIwkPQSgMwNfrR9$848d5254d51e429d7adf1b9a1099a3dcde7167396dec1ebf90cff8b174d4d7c9aa4db21fd6ac712a6822048d65f7aa9dedbe0721a0ac9b02ffafeae85f6ca0b4','admin',1,'2026-03-21 10:41:53.512079','2026-03-22 08:15:18.354206');
INSERT INTO "user" VALUES(2,'cuneytdemir','scrypt:32768:8:1$6zMpB3xUspPoeHQB$6c14996a48081eb0beeb01c25c97382857a2b96e11916df881be4d84a442586999861d762caf4390a311c9050849a6cfde7e6cfd6c6e451a3c33d9b49afec6c8','admin',1,'2026-03-21 11:19:44.070598','2026-03-23 18:03:38.323524');
CREATE INDEX ix_firma_eposta ON firma (eposta);
CREATE INDEX ix_firma_etiket_uuid ON firma (etiket_uuid);
CREATE INDEX ix_firma_firma_adi ON firma (firma_adi);
CREATE INDEX ix_firma_is_active ON firma (is_active);
CREATE INDEX ix_firma_is_deleted ON firma (is_deleted);
CREATE INDEX ix_firma_is_musteri ON firma (is_musteri);
CREATE INDEX ix_firma_is_tedarikci ON firma (is_tedarikci);
CREATE INDEX ix_firma_tckn ON firma (tckn);
CREATE UNIQUE INDEX ix_firma_vergi_no ON firma (vergi_no);
CREATE UNIQUE INDEX ix_user_username ON user (username);
CREATE INDEX ix_cari_hareket_belge_no ON cari_hareket (belge_no);
CREATE INDEX ix_cari_hareket_durum ON cari_hareket (durum);
CREATE INDEX ix_cari_hareket_firma_id ON cari_hareket (firma_id);
CREATE INDEX ix_cari_hareket_is_active ON cari_hareket (is_active);
CREATE INDEX ix_cari_hareket_is_deleted ON cari_hareket (is_deleted);
CREATE INDEX ix_cari_hareket_kaynak_id ON cari_hareket (kaynak_id);
CREATE INDEX ix_cari_hareket_kaynak_modul ON cari_hareket (kaynak_modul);
CREATE INDEX ix_cari_hareket_tarih ON cari_hareket (tarih);
CREATE INDEX ix_cari_hareket_vade_tarihi ON cari_hareket (vade_tarihi);
CREATE INDEX ix_cari_hareket_yon ON cari_hareket (yon);
CREATE INDEX ix_odeme_is_active ON odeme (is_active);
CREATE INDEX ix_odeme_is_deleted ON odeme (is_deleted);
CREATE INDEX ix_stok_karti_is_active ON stok_karti (is_active);
CREATE INDEX ix_stok_karti_is_deleted ON stok_karti (is_deleted);
CREATE UNIQUE INDEX ix_stok_karti_parca_kodu ON stok_karti (parca_kodu);
CREATE INDEX ix_bakim_kaydi_is_active ON bakim_kaydi (is_active);
CREATE INDEX ix_bakim_kaydi_is_deleted ON bakim_kaydi (is_deleted);
CREATE INDEX ix_cari_mahsup_alacak_hareket_id ON cari_mahsup (alacak_hareket_id);
CREATE INDEX ix_cari_mahsup_borc_hareket_id ON cari_mahsup (borc_hareket_id);
CREATE INDEX ix_cari_mahsup_is_active ON cari_mahsup (is_active);
CREATE INDEX ix_cari_mahsup_is_deleted ON cari_mahsup (is_deleted);
CREATE INDEX ix_cari_mahsup_tarih ON cari_mahsup (tarih);
CREATE INDEX ix_nakliye_cari_islendi_mi ON nakliye (cari_islendi_mi);
CREATE INDEX ix_stok_hareket_is_active ON stok_hareket (is_active);
CREATE INDEX ix_stok_hareket_is_deleted ON stok_hareket (is_deleted);
CREATE INDEX ix_hizmet_kaydi_is_active ON hizmet_kaydi (is_active);
CREATE INDEX ix_hizmet_kaydi_is_deleted ON hizmet_kaydi (is_deleted);
CREATE INDEX ix_kullanilan_parca_is_active ON kullanilan_parca (is_active);
CREATE INDEX ix_kullanilan_parca_is_deleted ON kullanilan_parca (is_deleted);
CREATE INDEX ix_makine_degisim_is_active ON makine_degisim (is_active);
CREATE INDEX ix_makine_degisim_is_deleted ON makine_degisim (is_deleted);
CREATE INDEX ix_hakedis_durum ON hakedis (durum);
CREATE UNIQUE INDEX ix_hakedis_fatura_no ON hakedis (fatura_no);
CREATE UNIQUE INDEX ix_hakedis_hakedis_no ON hakedis (hakedis_no);
CREATE INDEX ix_hakedis_is_active ON hakedis (is_active);
CREATE INDEX ix_hakedis_is_deleted ON hakedis (is_deleted);
CREATE INDEX ix_hakedis_kalemi_is_active ON hakedis_kalemi (is_active);
CREATE INDEX ix_hakedis_kalemi_is_deleted ON hakedis_kalemi (is_deleted);
CREATE INDEX ix_kiralama_kalemi_chain_id ON kiralama_kalemi (chain_id);
CREATE INDEX ix_kiralama_kalemi_is_deleted ON kiralama_kalemi (is_deleted);
CREATE INDEX ix_araclar_is_deleted ON araclar (is_deleted);
CREATE UNIQUE INDEX ix_araclar_plaka ON araclar (plaka);
CREATE UNIQUE INDEX ix_ekipman_kod ON ekipman (kod);
CREATE INDEX ix_ekipman_seri_no ON ekipman (seri_no);
CREATE INDEX ix_ekipman_is_deleted ON ekipman (is_deleted);
CREATE INDEX ix_ekipman_is_active ON ekipman (is_active);
CREATE INDEX ix_operation_log_action ON operation_log (action);
CREATE INDEX ix_operation_log_created_at ON operation_log (created_at);
CREATE INDEX ix_operation_log_entity_id ON operation_log (entity_id);
CREATE INDEX ix_operation_log_entity_type ON operation_log (entity_type);
CREATE INDEX ix_operation_log_module ON operation_log (module);
CREATE INDEX ix_operation_log_success ON operation_log (success);
CREATE INDEX ix_operation_log_user_id ON operation_log (user_id);
CREATE INDEX ix_operation_log_username ON operation_log (username);
CREATE INDEX ix_kasa_is_deleted ON kasa (is_deleted);
CREATE INDEX ix_kasa_is_active ON kasa (is_active);
CREATE INDEX ix_takvim_hatirlatma_user_id ON takvim_hatirlatma (user_id);
CREATE INDEX ix_takvim_hatirlatma_tarih ON takvim_hatirlatma (tarih);
CREATE INDEX ix_takvim_hatirlatma_is_active ON takvim_hatirlatma (is_active);
CREATE INDEX ix_takvim_hatirlatma_is_deleted ON takvim_hatirlatma (is_deleted);
CREATE INDEX ix_app_settings_is_active ON app_settings (is_active);
CREATE INDEX ix_app_settings_is_deleted ON app_settings (is_deleted);
CREATE INDEX ix_kiralama_is_deleted ON kiralama (is_deleted);
CREATE INDEX ix_kiralama_is_active ON kiralama (is_active);
COMMIT;
