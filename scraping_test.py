import telebot
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# Sua chave de API do Telegram
TOKEN = '7939579434:AAG6U4ZfG8EGKooZtr6yJ_GAZ8YWvnQp5n0'  # Substitua pela sua chave API
bot = telebot.TeleBot(TOKEN)

# Cache de imagens
IMAGEM_CACHE = {}

def buscar_informacoes(link, chat_id):
    try:
        bot.send_message(chat_id, "Buscando dados do produto...🔍🛍️")

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = uc.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(link)
        
        time.sleep(3)

        nome_produto = "Nome não encontrado"
        preco_original = "Preço original não disponível"
        preco_com_desconto = "Preço com desconto não disponível"
        parcelamento = "Parcelamento não disponível"
        cupom = "Cupom não disponível"
        imagem_url = "Imagem não encontrada"

        # Identificar e extrair informações dependendo da loja
        if "amazon.com.br" in link:
            nome_produto = driver.find_element(By.ID, "productTitle").text
            preco_com_desconto = driver.find_element(By.CSS_SELECTOR, "span.a-price-whole").text
            imagem_url = driver.find_element(By.ID, "landingImage").get_attribute("src")
        
        elif "mercadolivre.com.br" in link:
            nome_produto = driver.find_element(By.CSS_SELECTOR, "h1.ui-pdp-title").text
            preco_com_desconto = driver.find_element(By.CSS_SELECTOR, "span.price-tag-fraction").text
            imagem_url = driver.find_element(By.CSS_SELECTOR, "img.ui-pdp-image").get_attribute("src")
        
        elif "shopee.com.br" in link:
            nome_produto = driver.find_element(By.CSS_SELECTOR, "div.qaNIZv").text
            preco_com_desconto = driver.find_element(By.CSS_SELECTOR, "div.vioxXd span").text
            imagem_url = driver.find_element(By.CSS_SELECTOR, "img._3ZDC1p").get_attribute("src")
        
        elif "shein.com.br" in link:
            nome_produto = driver.find_element(By.CSS_SELECTOR, "h1.product-intro__head-name").text
            preco_com_desconto = driver.find_element(By.CSS_SELECTOR, "span.normal-price").text
            imagem_url = driver.find_element(By.CSS_SELECTOR, "img.jmi-popover-product").get_attribute("src")
        
        elif "magazinevoce.com.br" in link or "magazineluiza.com.br" in link:
            nome_produto = driver.find_element(By.CSS_SELECTOR, "h1[data-testid='heading-product-title']").text
            preco_original = driver.find_element(By.CSS_SELECTOR, "p[data-testid='price-original']").text
            preco_com_desconto = driver.find_element(By.CSS_SELECTOR, "p[data-testid='price-value']").text
            parcelamento_element = driver.find_elements(By.CSS_SELECTOR, "p[data-testid='installment']")
            parcelamento = parcelamento_element[0].text if parcelamento_element else "Parcelamento não disponível"
            cupom_element = driver.find_elements(By.CSS_SELECTOR, "span[data-testid='coupon-code']")
            cupom = cupom_element[0].text if cupom_element else "Cupom não disponível"
            imagem_url = driver.find_element(By.CSS_SELECTOR, "img[data-testid='media-gallery-image']").get_attribute('src')
        
        else:
            driver.quit()
            return None, "Plataforma não suportada ainda."

        if imagem_url not in IMAGEM_CACHE:
            imagem_resposta = requests.get(imagem_url)
            if imagem_resposta.status_code == 200:
                with open("produto.jpg", "wb") as file:
                    file.write(imagem_resposta.content)
                IMAGEM_CACHE[imagem_url] = "produto.jpg"
            imagem_url = "produto.jpg"
        elif imagem_url in IMAGEM_CACHE:
            imagem_url = IMAGEM_CACHE[imagem_url]

        driver.quit()

        msg = (f"🛍️ *{nome_produto}*\n\n"
               f"~~de R$ {preco_original}~~\n"
               f"💸 *por R$ {preco_com_desconto}* 🚨🚨\n")

        if parcelamento and parcelamento != "Parcelamento não disponível":
            msg += f"💳 {parcelamento} sem juros\n\n"
        if cupom != "Cupom não disponível":
            msg += f"🎟️ *Cupom de desconto:* {cupom}\n\n"
        msg += (f"👉 [Link para comprar]({link})\n\n"
                f"_*Promoção sujeita a alteração a qualquer momento_")

        return imagem_url, msg

    except Exception as e:
        print(f"Erro ao buscar informações: {e}")
        return None, "Erro ao buscar informações do produto."

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Olá! Envie um link de produto para eu buscar as informações.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    link = message.text
    chat_id = message.chat.id

    imagem_url, msg = buscar_informacoes(link, chat_id)
    
    if imagem_url and os.path.exists(imagem_url):
        with open(imagem_url, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=msg, parse_mode='Markdown')
    else:
        bot.reply_to(message, msg, parse_mode='Markdown')

bot.polling()
