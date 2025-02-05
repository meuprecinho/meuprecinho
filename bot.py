import telebot

# 🔑 Substitua pelo seu Token do BotFather
TOKEN = "7939579434:AAHUTCfMWNgkevSSu7cdiQco2ahotn6Ic2I"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Olá! Envie um link de promoção e eu formaterei os detalhes para você. 🚀")

@bot.message_handler(func=lambda message: message.text.startswith("http"))
def format_promo(message):
    link = message.text  # Pegamos o link enviado pelo usuário
    response = f"""
    🔥 Promoção Encontrada! 🔥

    🛍️ Produto: *Nome do Produto Aqui*
    ~de R$ 299,90~
    💸 por *R$ 199,90* 🚨🚨
    💳 ou 10x de R$ 19,99

    🎟️ Use o cupom: *CUPOM10*

    👉 [Link p/ comprar]({link})

    _Promoção sujeita a alteração a qualquer momento._
    """
    bot.reply_to(message, response, parse_mode="Markdown")

print("Bot está rodando...")
bot.polling()
