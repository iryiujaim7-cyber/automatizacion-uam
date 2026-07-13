import os
import requests
import re
import pdfplumber
from playwright.sync_api import sync_playwright

RUTA_DESCARGAS = os.path.join(os.getcwd(), "descargas")
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def automatizar_uam():
    if not os.path.exists(RUTA_DESCARGAS):
        os.makedirs(RUTA_DESCARGAS)

    print("Iniciando navegación...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        page = context.new_page()
        page.set_default_timeout(60000)
        
        page.goto("https://www.uam.mx/")
        page.click("text=PROFESORADO")
        page.click("text=CONVOCATORIAS Y DICTÁMENES")
        
        selector = "a:has-text('CONVOCATORIAS Y DICTÁMENES PARA EL INGRESO DEL PERSONAL ACADÉMICO')"
        pdf_url = page.locator(selector).first.get_attribute("href")
        
        if pdf_url.startswith("/"):
            pdf_url = "https://www.uam.mx" + pdf_url
            
        print(f"URL detectada: {pdf_url}")
        
        match = re.search(r'(\d{2}[a-z]{3}\d{2})', pdf_url)
        nombre_archivo = f"{match.group(1)}.pdf" if match else "convocatoria_default.pdf"
        
        archivo_final = os.path.join(RUTA_DESCARGAS, nombre_archivo)
        
        response = requests.get(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
        with open(archivo_final, "wb") as f:
            f.write(response.content)
        browser.close()
        print(f"Archivo descargado: {nombre_archivo}")

    print("Analizando contenido...")
    encontrado = False
    with pdfplumber.open(archivo_final) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto and "Disciplina: Derecho" in texto:
                encontrado = True
                break

    if True:
        mensaje = "Se detectó la convocatoria con 'Disciplina: Derecho'. Revisa el archivo."
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={mensaje}"
        requests.get(url)
    else:
        print("Disciplina no encontrada.")

if __name__ == "__main__":
    automatizar_uam()
