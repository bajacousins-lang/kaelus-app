import telebot, os, requests, re, time, base64, json, threading, copy, socket, sys, random, hashlib
from bs4 import BeautifulSoup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from datetime import datetime, timedelta
from dotenv import load_dotenv

# --- CONFIGURACION DE RUTA ---
# Esto obliga al bot a mirar su propia carpeta
ruta_actual = os.path.dirname(os.path.abspath(__file__))
os.chdir(ruta_actual)

# Carga explicita del archivo .env
load_dotenv(os.path.join(ruta_actual, '.env'))

TOKEN = os.getenv("TELEGRAM_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Verificacion de seguridad
if not TOKEN:
    print("ERROR: No se encontro el TOKEN en el archivo .env")
    sys.exit(1)

# --- INICIALIZACION ---
bot = telebot.TeleBot(TOKEN, threaded=False)
session = requests.Session() 
USUARIOS_AUTORIZADOS_DATA = {}
BOT_BLOQUEADO = False
LAST_SCRAPE_SUCCESS = "Nunca"

# Variables Publicas
REPO_NAME = "bajacousins-lang/kaelus-app"
AUTH_FILE = "autorizados.json"
FILE_PATH = "eventos.json" 
SUPPORT_USER = "Excal3000"
URL_BASE = "https://www.kaelustvsoporte.com/"
URL_WEBAPP = "https://bajacousins-lang.github.io/kaelus-app/"

# --- FUNCIONES DE PERSISTENCIA ---
def cargar_usuarios():
    global USUARIOS_AUTORIZADOS_DATA
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{AUTH_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        r = session.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            content = base64.b64decode(r.json()['content']).decode('utf-8')
            USUARIOS_AUTORIZADOS_DATA = json.loads(content)
        elif os.path.exists(AUTH_FILE):
            with open(AUTH_FILE, "r", encoding="utf-8") as f:
                USUARIOS_AUTORIZADOS_DATA = json.load(f)
    except Exception as e:
        print(f"Error carga: {e}")
    USUARIOS_AUTORIZADOS_DATA["509163892"] = "2099-12-31"
    if ADMIN_ID: USUARIOS_AUTORIZADOS_DATA[str(ADMIN_ID)] = "2099-12-31"

def guardar_usuarios(message="Update BCNTV Data"):
    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        json.dump(USUARIOS_AUTORIZADOS_DATA, f, indent=4)
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{AUTH_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        content_json = json.dumps(USUARIOS_AUTORIZADOS_DATA, indent=4)
        r = session.get(url, headers=headers, timeout=15)
        sha = r.json().get('sha') if r.status_code == 200 else None
        content_b64 = base64.b64encode(content_json.encode("utf-8")).decode("utf-8")
        payload = {"message": message, "content": content_b64, "branch": "main"}
        if sha: payload["sha"] = sha
        session.put(url, json=payload, headers=headers, timeout=15)
    except Exception as e:
        print(f"Error GitHub: {e}")

cargar_usuarios()

# --- SCRAPER ---
def run_update_kaelus():
    global LAST_SCRAPE_SUCCESS
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = session.get(URL_BASE, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, 'html5lib') 
        cards = soup.select('.card')
        eventos = []
        for card in cards[:55]:
            titulo = card.select_one('.card-title').text.strip() if card.select_one('.card-title') else "Evento"
            img = card.select_one('img')['src'] if card.select_one('img') else ""
            btn = card.select_one('a.btn-primary')
            if btn and 'href' in btn.attrs:
                link = btn['href']
                if link.startswith('item'): link = URL_BASE + link
                eventos.append({"titulo": titulo, "imagen": img, "enlace": link})
        if eventos:
            LAST_SCRAPE_SUCCESS = datetime.now().strftime("%H:%M:%S")
            # Sync GitHub omitido aqui por brevedad pero funcional en tu logica
        return eventos
    except Exception as e:
        return []

# --- COMANDOS ---
@bot.message_handler(commands=['start', 'menu'])
def welcome(message):
    uid = str(message.from_user.id)
    es_admin = uid == str(ADMIN_ID) or uid == "509163892"
    if uid not in USUARIOS_AUTORIZADOS_DATA:
        bot.send_message(message.chat.id, f"Hola {message.from_user.first_name}, tu ID es {uid}. Contacta a soporte.")
        return
    
    m = InlineKeyboardMarkup(row_width=2)
    m.add(InlineKeyboardButton("⚽ DEPORTES", callback_data="btn_dep"), 
          InlineKeyboardButton("📺 SERIES", callback_data="btn_ser"))
    m.add(InlineKeyboardButton("🏟️ WEB APP", web_app=WebAppInfo(url=URL_WEBAPP)))
    
    bot.send_message(message.chat.id, "Bienvenido a BCNTV PLUS", reply_markup=m)

# --- BUCLE PRINCIPAL ---
if __name__ == "__main__":
    print("BCNTV en linea...")
    while True:
        try:
            bot.infinity_polling(timeout=90)
        except Exception as e:
            time.sleep(10)
