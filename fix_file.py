import os
os.chdir(r'c:\Users\cuney\Drive\'ım\kiralama_projesi_v3')

# Dosyayı oku
with open(r'app\services\ekipman_rapor_services.py', 'r', encoding='utf-8') as f:
    content = f.read()

# İyileştirmeler yap
# 1. kirlama_brm_fiyat → kiralama_brm_fiyat (typo fix)
content = content.replace('KiralamaKalemi.kirlama_brm_fiyat', 'KiralamaKalemi.kiralama_brm_fiyat')
content = content.replace('sum(k.kirlama_brm_fiyat', 'sum(k.kiralama_brm_fiyat')

# 2. ORI

NAL sorgu - func.sum() kullandığından emin ol
# Satırları kontrol et
lines = content.split('\n')
for i, line in enumerate(lines[185:210], start=186):
    if 'func.sum' in line or 'kiralama_brm' in line or 'KiralamaKalemi' in line:
        print(f"{i}: {line.strip()}")

# Dosyayı yaz
with open(r'app\services\ekipman_rapor_services.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Dosya düzeltildi!")
