from typing import Dict

from ...historical import CryptoCompareConfig
from ...notifications import TelegramConfig
from ..ui.configuration import ConfigurationTab
from ..ui.configuration import CryptoComparePanel
from ..ui.configuration import GeneralPanel
from ..ui.configuration import TelegramPane


class ConfigurationTabController:
    def __init__(self, widget: ConfigurationTab):
        self.widget = widget
        self.general_panel_controller = GeneralPanelController(
            self.widget.general_panel
        )
        self.crypto_compare_panel_controller = CryptoComparePanelController(
            self.widget.crypto_compare_panel
        )
        self.telegram_pane_controller = TelegramPaneController(
            self.widget.telegram_panel
        )

        self.widget.save_button.clicked.connect(self.save)

    def save(self) -> None:
        config_dict = {}
        try:
            config_dict.update(self.general_panel_controller.get_config())
            crypto_compare_config = self.crypto_compare_panel_controller.get_config()
            print(crypto_compare_config)
            telegram_config = self.telegram_pane_controller.get_config()
            print(telegram_config)
        except RuntimeError as e:
            print(e)
            return
        print(config_dict)


class GeneralPanelController:
    def __init__(self, general_panel: GeneralPanel):
        self.general_panel = general_panel

    def get_config(self) -> Dict:
        text = self.general_panel.poll_interval_edit.text()
        try:
            sleep = int(text)
        except ValueError as e:
            raise RuntimeError(
                f"Cannot parse input {text}. Make sure that it is an integer."
            ) from e
        return {"sleep": sleep}


class CryptoComparePanelController:
    def __init__(self, ui: CryptoComparePanel):
        self.ui = ui

    def get_config(self) -> CryptoCompareConfig:
        api_key = self.ui.api_key_line_edit.text()
        return CryptoCompareConfig(api_key)


class TelegramPaneController:
    def __init__(self, ui: TelegramPane):
        self.ui = ui

    def get_config(self) -> TelegramConfig:
        chat_id = self.ui.chat_id_line_edit.text()
        token = self.ui.token_line_edit.text()
        log_level = self.ui.log_level_combo_box.currentText()
        return TelegramConfig(token, log_level, chat_id)
