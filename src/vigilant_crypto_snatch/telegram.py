import logging

import requests


logger = logging.getLogger(__name__)


def telegram_bot_sendtext(config: dict, bot_message: str):
    if 'telegram' not in config:
        return

    logger.debug('Sending message to Telegram …')
    bot_token = config['telegram']['token']
    bot_chat_id = config['telegram']['chat_id']
    send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={bot_chat_id}&parse_mode=Markdown&text={bot_message}'
    response = requests.get(send_text)
    return response.json()
