import os
import requests
import re
import pdfplumber
from playwright.sync_api import sync_playwright

# --- CONFIGURACIÓN (GitHub Actions usará las variables de entorno) ---
RUTA_DESCARGAS = os.path.join(os.getcwd(), "descargas")
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def automatizar_uam():
    # Asegurar carpeta de descargas
    if not os.path.exists(RUTA_DESCARGAS):
        os.makedirs(RUTA_DESCARGAS)

    # 1. NAVEGACIÓN Y DESCARGA
    print("Iniciando navegación...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("https://www.uam.mx/")
        page.click("text=PROFESORADO")
        page.click("text=CONVOCATORIAS Y DICTÁMENES")
        
        with context.expect_page() as new_page_info:
            page.locator("a:has-text('CONVOCATORIAS Y DICTÁMENES PARA EL INGRESO DEL PERSONAL ACADÉMICO')").first.click()
        
        new_page = new_page_info.value
        new_page.wait_for_load_state("load")
        pdf_url = new_page.url
        
        # Renombrado basado en URL
        match = re.search(r'(\d{2}[a-z]{3}\d{2})', pdf_url)
        nombre_archivo = f"{match.group(1)}.pdf" if match else "convocatoria_default.pdf"
        
        archivo_final = os.path.join(RUTA_DESCARGAS, nombre_archivo)
        response = requests.get(pdf_url)
        with open(archivo_final, "wb") as f:
            f.write(response.content)
        browser.close()
        print(f"Archivo descargado: {nombre_archivo}")

    # 2. BÚSQUEDA Y NOTIFICACIÓN
    print("Analizando contenido...")
    encontrado = False
    with pdfplumber.open(archivo_final) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto and "Disciplina: Derecho" in texto:
                encontrado = True
                break

    if encontrado:
        mensaje = f"Ha salido una Convocatoria en la UAM que te puede interesar. Revisa la Convocatoria: {nombre_archivo}. Éxito"
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={mensaje}"
        requests.get(url)
        print("Notificación enviada a Telegram.")
    else:
        print("El término 'Disciplina: Derecho' no fue encontrado.")

if __name__ == "__main__":
    automatizar_uam()
