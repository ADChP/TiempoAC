'''
Tiempo América Central
Bot en Telegram sobre las condiciones atmosféricas actuales en América Central.

Archivo iniciador.

Autor: Andrés David Chavarría-Palma
Junio - 2023
'''
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import ssl
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
from urllib.request import urlopen

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.message.from_user.first_name
    buttons = [[InlineKeyboardButton("Lista de comandos", callback_data="comandos")]]
    await update.message.reply_text(text=f"¡Bienvenido {nombre}! Estoy para mostrarte la actualidad atmosférica de América Central. Mira la lista de comandos aceptados.",
                                   reply_markup=InlineKeyboardMarkup(buttons))
    
async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    ayuda_text = '''/tiempo para ver imagen satelital actualizada de las condiciones atmosféricas en América Central.
/otros para ver ejemplo.
/saludo otro caso.'''
    await context.bot.send_message(chat_id=update.effective_chat.id, text=ayuda_text)

async def tiempo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='upload_photo')

    ahora = datetime.now()-timedelta(hours=6)
    h18 = ahora.replace(hour=18, minute=0, second=0, microsecond=0)
    h06 = ahora.replace(day=datetime.now().day+1, hour=6, minute=0, second=0, microsecond=0)

    if ahora >= h18 and ahora < h06:

        html = urlopen('https://weather.msfc.nasa.gov/cgi-bin/get-abi?satellite=GOESEastfullDiskband14&lat=11.5&lon=-84.3&zoom=1&width=1000&height=800&quality=100&palette=ir2.pal', context=ctx).read()
        
        soup = BeautifulSoup(html, 'html.parser')
        imagen = 'https://weather.msfc.nasa.gov' + soup.img['src']

        hora_utf = imagen.split('/')[-1][4:6] + ':' + imagen.split('/')[-1][6:8]
        utc6 = timedelta(hours=6)
        utc5 = timedelta(hours=5)
        hora_6 = (datetime.strptime(hora_utf,'%H:%M') - utc6).strftime('%H:%M')
        hora_5 = (datetime.strptime(hora_utf,'%H:%M') - utc5).strftime('%H:%M')

        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=imagen, caption = f'Condiciones atmosféricas a las {hora_6} UTC-6 y a las {hora_5} UTC-5 (horas locales). Fuente: GOES - NOAA. Banda 14, Infrarrojo de onda lejana.')

    else:
        html = urlopen('https://weather.msfc.nasa.gov/cgi-bin/get-abi?satellite=GOESEastfullDiskband02&lat=11.5&lon=-84.3&zoom=4&width=1000&height=800&quality=100', context=ctx).read()
        
        soup = BeautifulSoup(html, 'html.parser')
        imagen = 'https://weather.msfc.nasa.gov' + soup.img['src']

        hora_utf = imagen.split('/')[-1][4:6] + ':' + imagen.split('/')[-1][6:8]
        utc6 = timedelta(hours=6)
        utc5 = timedelta(hours=5)
        hora_6 = (datetime.strptime(hora_utf,'%H:%M') - utc6).strftime('%H:%M')
        hora_5 = (datetime.strptime(hora_utf,'%H:%M') - utc5).strftime('%H:%M')

        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=imagen, caption = f'Condiciones atmosféricas a las {hora_6} UTC-6 y a las {hora_5} UTC-5 (horas locales). Fuente: GOES - NOAA. Banda 2, espectro del rojo visible.')

if __name__ == '__main__':
    application = ApplicationBuilder().token('TOKEN').build()
    
    ayuda_handler = CallbackQueryHandler(ayuda,'comandos')
    start_handler = CommandHandler('start', start)
    tiempo_handler = CommandHandler('tiempo', tiempo)
    application.add_handler(ayuda_handler)
    application.add_handler(start_handler)
    application.add_handler(tiempo_handler)
    
    application.run_polling()
