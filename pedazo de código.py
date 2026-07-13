import requests

TOKEN = "8856454615:AAHG7rQoy2oLqahz4jOV_7nRfLJqQtflcMw" # Reemplaza con tu token real
CHAT_ID = "1965668705"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text=¡Hola! El sistema de automatización está funcionando."
respuesta = requests.get(url)

if respuesta.status_code == 200:
    print("¡Notificación enviada con éxito! Revisa tu Telegram.")
else:
    print(f"Error al enviar: {respuesta.text}")
