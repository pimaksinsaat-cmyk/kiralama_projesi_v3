import os
import platform
import subprocess


def convert_docx_to_pdf(docx_path, output_dir, logger=None, timeout_seconds=30):
    """
    DOCX dosyasini platforma gore PDF'e donusturur.
    Windows: docx2pdf
    Linux: libreoffice (soffice)
    """
    current_os = platform.system()
    pdf_path = docx_path.replace(".docx", ".pdf")

    abs_docx = os.path.abspath(docx_path)
    abs_pdf = os.path.abspath(pdf_path)

    if current_os == "Windows":
        try:
            from docx2pdf import convert
            import pythoncom

            pythoncom.CoInitialize()
            if os.path.exists(abs_pdf):
                try:
                    os.remove(abs_pdf)
                except Exception:
                    pass

            convert(abs_docx, abs_pdf)
            return pdf_path if os.path.exists(abs_pdf) else None
        except Exception as e:
            if logger:
                logger.warning(f"docx2pdf ile Windows PDF donusumu basarisiz: {str(e)}")
        finally:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass

    # Fallback: LibreOffice/soffice (Windows dahil tum platformlarda denenir)
    try:
        subprocess.run(
            [
                "soffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                output_dir,
                abs_docx,
            ],
            check=True,
            capture_output=True,
            timeout=timeout_seconds,
        )
        return pdf_path if os.path.exists(abs_pdf) else None
    except Exception as e:
        if logger:
            logger.error(f"soffice ile PDF donusumu basarisiz: {str(e)}")
        return None
