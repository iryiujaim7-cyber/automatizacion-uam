from playwright.sync_api import sync_playwright
import os
import re
import requests

def probar_sesion1():
    # 1. Configuración de carpetas
    ruta_descargas = os.path.join(os.getcwd(), "descargas")
    if not os.path.exists(ruta_descargas):
        os.makedirs(ruta_descargas)
    
    with sync_playwright() as p:
        # Lanzamos el navegador
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("1. Entrando a UAM...")
        page.goto("https://www.uam.mx/")
        
        print("2. Dando clic en PROFESORADO...")
        page.click("text=PROFESORADO")
        
        print("3. Dando clic en CONVOCATORIAS Y DICTÁMENES...")
        page.click("text=CONVOCATORIAS Y DICTÁMENES")
        
        print("4. Intentando acceder al PDF...")
        # Esperamos a que se abra la nueva página con el PDF
        with context.expect_page() as new_page_info:
            page.locator("a:has-text('CONVOCATORIAS Y DICTÁMENES PARA EL INGRESO DEL PERSONAL ACADÉMICO')").first.click()
        
        new_page = new_page_info.value
        new_page.wait_for_load_state("load")
        
        pdf_url = new_page.url
        print(f"URL del PDF detectada: {pdf_url}")
        
        # 5. Lógica de renombrado para extraer '06jul26' de la URL
        # Busca el patrón de: 2 dígitos + 3 letras + 2 dígitos (ej. 06jul26)
        match = re.search(r'(\d{2}[a-z]{3}\d{2})', pdf_url)
        
        if match:
            fecha_archivo = match.group(1)
            nombre_archivo = f"{fecha_archivo}.pdf"
        else:
            nombre_archivo = "convocatoria_default.pdf"
        
        # 6. Descarga del archivo
        response = requests.get(pdf_url)
        archivo_final = os.path.join(ruta_descargas, nombre_archivo)
        
        with open(archivo_final, "wb") as f:
            f.write(response.content)
            
        print(f"¡Éxito! Archivo guardado en: {archivo_final}")
        browser.close()

if __name__ == "__main__":
    probar_sesion1()
