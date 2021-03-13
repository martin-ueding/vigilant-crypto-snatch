import logging

import requests


logger = logging.getLogger('vigilant_crypto_snatch')


class TelegramBot(logging.Handler):
    def __init__(self, token: str):
        super().__init__(logging.INFO)
        self.token = token
        self.get_chat_id()

    def get_chat_id(self) -> None:
        response = requests.get(f'https://api.telegram.org/bot{self.token}/getUpdates')
        response.raise_for_status()
        data = response.json()
        self.chat_id = int(data['result'][-1]['message']['chat']['id'])

    def send_message(self, message: str) -> dict:
        logger.debug('Sending message to Telegram …')
        send_text = f'https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.chat_id}&parse_mode=Markdown&text={message}'
        response = requests.get(send_text)
        return response.json()

    def emit(self, record: logging.LogRecord) -> None:
        self.send_message(record.getMessage())