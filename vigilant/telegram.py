import requests


def telegram_bot_sendtext(bot_message):
    bot_token = 'here'  # Your Bot Token from Telegram
    bot_chatID = 'here'  # The Chat ID
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


def report():
##    my_price = print()       Replace this with the current price
    my_message = 'Buying {} BTC for {} EUR via the {} minutes trigger because of a drop of {} %'.format(btc, trigger['eur'], trigger['minutes'], trigger['drop'])   ## Customize your message
    telegram_bot_sendtext(my_message)

# End Telegram Bot Notice - Standard Report can be placed with report() - Be sure to customize your message and price info
