import os
import platform
import subprocess

def convert_docx_to_pdf(docx_path, output_dir, logger=None, timeout_seconds=30):
    current_os = platform.system()
    
    # Dosya yollarını kesinleştir (Absolute Path her zaman daha güvenlidir)
    abs_docx = os.path.abspath(docx_path)
    # LibreOffice çıktı ismini otomatik belirler, biz sadece yolunu hazırlayalım
    filename = os.path.basename(abs_docx).replace(".docx", ".pdf")
    abs_pdf = os.path.join(os.path.abspath(output_dir), filename)

    if current_os == "Windows":
        # ... (Windows kısmın kalsın, orası doğru görünüyor)
        pass

    # --- LinuX / Helsinki Tarafı İçin İyileştirilmiş Bölüm ---
    try:
        # LibreOffice sunucuda çalışırken bazen bir 'Home' dizini arar.
        # -env:UserInstallation ile ona geçici bir çalışma alanı gösteriyoruz.
        command = [
            "soffice",
            "-env:UserInstallation=file:///tmp/libreoffice_profile", # Bu satır hayat kurtarır
            "--headless",
            "--convert-to", "pdf",
            "--outdir", os.path.abspath(output_dir),
            abs_docx
        ]
        
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            timeout=timeout_seconds,
        )
        
        if os.path.exists(abs_pdf):
            return abs_pdf
        else:
            if logger: logger.error(f"PDF oluştu denildi ama dosya bulunamadı: {abs_pdf}")
            return None

    except Exception as e:
        msg = f"soffice ile PDF donusumu basarisiz: {str(e)}"
        if logger: logger.error(msg)
        print(msg)
        return None