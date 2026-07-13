import pdfplumber
import os

def analizar_pdf(nombre_archivo):
    # Ruta donde se encuentra el PDF descargado
    ruta_archivo = os.path.join(os.getcwd(), "descargas", nombre_archivo)
    
    # Abrimos el archivo PDF
    with pdfplumber.open(ruta_archivo) as pdf:
        contenido_completo = ""
        # Recorremos cada página del PDF para extraer el texto
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                contenido_completo += texto.lower() # Convertimos a minúsculas
        
        # Buscamos el término
        if "derecho" in contenido_completo:
            print(f"¡Éxito! Se encontró el término 'derecho' en {nombre_archivo}")
            return True
        else:
            print(f"No se encontró el término en {nombre_archivo}")
            return False

# Prueba rápida
# Sustituye '06jul26.pdf' por el nombre del archivo que descargaste en la Sesión 1
if __name__ == "__main__":
    analizar_pdf("06jul26.pdf")
