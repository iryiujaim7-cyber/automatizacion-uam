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
        # Lanzamos navegador con configuración de usuario para evitar bloqueos
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        page = context.new_page()
        page.set_default_timeout(60000)
        
        # Navegación directa
        page.goto("https://www.uam.mx/")
        page.click("text=PROFESORADO")
        page.click("text=CONVOCATORIAS Y DICTÁMENES")
        
        # Extraemos el atributo href directamente del selector
        selector = "a:has-text('CONVOCATORIAS Y DICTÁMENES PARA EL INGRESO DEL PERSONAL ACADÉMICO')"
        pdf_url = page.locator(selector).first.get_attribute("href")
        
        # Normalizamos la URL por si es relativa
        if pdf_url.startswith("/"):
            pdf_url = "https://www.uam.mx" + pdf_url
            
        print(f"URL del PDF detectada: {pdf_url}")
        
        # Renombrado basado en patrón de fecha en la URL
        match = re.search(r'(\d{2}[a-z]{3}\d{2})', pdf_url)
        nombre_archivo = f"{match.group(1)}.pdf" if match else "convocatoria_default.pdf"
        
        archivo_final = os.path.join(RUTA_DESCARGAS, nombre_archivo)
        
        # Descarga directa mediante requests (más estable que Playwright para archivos)
        response = requests.get(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
        with open(archivo_final, "wb") as f:
            f.write(response.content)
        browser.close()
        print(f"Archivo descargado exitosamente: {nombre_archivo}")

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
        mensaje = f"Ha salido una Convocatoria en la UAM que te puede interesar. Revisa: {nombre_archivo}."
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={mensaje}"
        requests.get(url)
        print("Notificación enviada a Telegram.")
    else:
        print("El término 'Disciplina: Derecho' no fue encontrado.")

if __name__ == "__main__":
    automatizar_uam()
