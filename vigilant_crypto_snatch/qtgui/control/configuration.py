import traceback
from typing import Iterable
from typing import Optional

import yaml
from PySide6.QtWidgets import QMessageBox

from ...commands.testdrive import try_historical
from ...configuration import Configuration
from ...configuration import update_yaml_config
from ...configuration import YamlConfigurationFactory
from ...core import AssetPair
from ...historical import CryptoCompareConfig
from ...marketplace import BitstampConfig
from ...marketplace import CCXTConfig
from ...marketplace import KrakenConfig
from ...marketplace import KrakenWithdrawalConfig
from ...marketplace.bitstamp_adaptor import BitstampMarketplace
from ...marketplace.ccxt_adapter import CCXTMarketplace
from ...marketplace.krakenex_adaptor import KrakenexMarketplace
from ...notifications import TelegramConfig
from ...notifications import TelegramSender
from ...triggers import TriggerSpec
from ..ui.configuration import BitstampPane
from ..ui.configuration import CCXTPane
from ..ui.configuration import ConfigurationTab
from ..ui.configuration import CryptoComparePanel
from ..ui.configuration import GeneralPanel
from ..ui.configuration import KrakenPane
from ..ui.configuration import KrakenWithdrawalEditWindow
from ..ui.configuration import KrakenWithdrawalPane
from ..ui.configuration import SingleTriggerEdit
from ..ui.configuration import TelegramPane
from ..ui.configuration import TriggerEditWindow
from ..ui.configuration import TriggerPane


def handle_exception_with_dialog(e: Exception) -> None:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setText(str(e))
    msg.setWindowTitle("Configuration Error")
    msg.setDetailedText(traceback.format_exc())
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()


def show_success_dialog(message: str) -> None:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setText(message)
    msg.setWindowTitle("Success")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()


class ConfigurationTabController:
    def __init__(self, ui: ConfigurationTab, update_config):
        self.ui = ui

        self.general_panel_controller = GeneralPanelController(ui.general_panel)
        self.crypto_compare_panel_controller = CryptoComparePanelController(
            ui.crypto_compare_panel
        )
        self.telegram_pane_controller = TelegramPaneController(ui.telegram_panel)
        self.trigger_pane_controller = TriggerPaneController(ui.trigger_pane)
        self.kraken_pane_controller = KrakenPaneController(self.ui.kraken_pane)
        self.bitstamp_pane_controller = BitstampPaneController(self.ui.bitstamp_pane)
        self.ccxt_controller = CCXTPaneController(self.ui.ccxt_pane)

        self.update_config = update_config

        ui.save_button.clicked.connect(self.save)

        self.populate_ui()

    def save(self) -> None:
        new_config = self._gather_config()
        if new_config is not None:
            self.update_config(new_config)
            update_yaml_config(new_config)

    def _gather_config(self) -> Optional[Configuration]:
        try:
            general = self.general_panel_controller.get_config()
            result = Configuration(
                polling_interval=general["sleep"],
                crypto_compare=self.crypto_compare_panel_controller.get_config(),
                triggers=self.trigger_pane_controller.get_config(),
                marketplace=general["marketplace"],
                kraken=self.kraken_pane_controller.get_config(),
                bitstamp=self.bitstamp_pane_controller.get_config(),
                telegram=self.telegram_pane_controller.get_config(),
            )

        except RuntimeError as e:
            handle_exception_with_dialog(e)
            return None
        return result

    def populate_ui(self) -> None:
        try:
            config = YamlConfigurationFactory().make_config()
        except RuntimeError as e:
            print(e)
            return
        self.general_panel_controller.populate_ui(
            config.polling_interval, config.marketplace
        )
        self.crypto_compare_panel_controller.populate_ui(config.crypto_compare)
        if config.telegram is not None:
            self.telegram_pane_controller.populate_ui(config.telegram)
        self.trigger_pane_controller.populate_ui(config.triggers)
        if config.kraken is not None:
            self.kraken_pane_controller.populate_ui(config.kraken)
        if config.bitstamp is not None:
            self.bitstamp_pane_controller.populate_ui(config.bitstamp)
        self.ccxt_controller.populate_ui(config.ccxt)


class GeneralPanelController:
    def __init__(self, general_panel: GeneralPanel):
        self.ui = general_panel

    def get_config(self) -> dict:
        text = self.ui.poll_interval_edit.text()
        try:
            sleep = int(text)
        except ValueError as e:
            raise RuntimeError(
                f"Cannot parse input {text}. Make sure that it is an integer."
            ) from e
        return {"sleep": sleep, "marketplace": self.ui.marketplace_edit.currentText()}

    def populate_ui(self, polling_inverval: int, marketplace: str) -> None:
        self.ui.poll_interval_edit.setText(str(polling_inverval))
        self.ui.marketplace_edit.setCurrentText(marketplace)


class CryptoComparePanelController:
    def __init__(self, ui: CryptoComparePanel):
        self.ui = ui
        self.ui.test.clicked.connect(self.test)

    def get_config(self) -> CryptoCompareConfig:
        api_key = self.ui.api_key_line_edit.text()
        return CryptoCompareConfig(api_key)

    def populate_ui(self, config: CryptoCompareConfig) -> None:
        self.ui.api_key_line_edit.setText(config.api_key)

    def test(self) -> None:
        print("Test")
        try:
            try_historical(self.get_config())
        except Exception as e:
            handle_exception_with_dialog(e)
        else:
            show_success_dialog("Crypto Compare is configured correctly.")


class TelegramPaneController:
    def __init__(self, ui: TelegramPane):
        self.ui = ui
        self.ui.test.clicked.connect(self.test)

    def get_config(self) -> TelegramConfig:
        chat_id_text = self.ui.chat_id_line_edit.text()
        if chat_id_text:
            try:
                chat_id = int(chat_id_text)
            except ValueError as e:
                raise RuntimeError(
                    f"Cannot parse Telegram chat ID {chat_id_text}. Make sure that it is an integer."
                ) from e
        else:
            chat_id = None
        token = self.ui.token_line_edit.text()
        log_level = self.ui.log_level_combo_box.currentText()
        return TelegramConfig(token, log_level, chat_id)

    def populate_ui(self, config: TelegramConfig) -> None:
        if config.chat_id:
            self.ui.chat_id_line_edit.setText(str(config.chat_id))
        self.ui.token_line_edit.setText(config.token)
        self.ui.log_level_combo_box.setCurrentText(config.level)

    def test(self) -> None:
        try:
            telegram_sender = TelegramSender(self.get_config())
            telegram_sender.send_message("Telegram is set up correctly! 🎉")
        except Exception as e:
            handle_exception_with_dialog(e)
        else:
            show_success_dialog("Telegram is configured correctly.")


class KrakenPaneController:
    def __init__(self, ui: KrakenPane):
        self.ui = ui
        self.withdrawal_pane_controller = KrakenWithdrawalPaneController(
            ui.kraken_withdrawal_pane
        )
        self.ui.test.clicked.connect(self.test)

    def populate_ui(self, config: KrakenConfig):
        self.ui.api_key.setText(config.key)
        self.ui.api_secret.setText(config.secret)
        self.ui.prefer_fee.setChecked(config.prefer_fee_in_base_currency)
        self.withdrawal_pane_controller.populate_ui(config.withdrawal.values())

    def get_config(self) -> KrakenConfig:
        config = KrakenConfig(
            key=self.ui.api_key.text(),
            secret=self.ui.api_secret.text(),
            prefer_fee_in_base_currency=self.ui.prefer_fee.isChecked(),
            withdrawal=self.withdrawal_pane_controller.get_config(),
        )
        return config

    def test(self) -> None:
        try:
            marketplace = KrakenexMarketplace(self.get_config())
            marketplace.get_balance()
        except Exception as e:
            handle_exception_with_dialog(e)
        else:
            show_success_dialog("Kraken is configured correctly.")


class BitstampPaneController:
    def __init__(self, ui: BitstampPane):
        self.ui = ui
        self.ui.test.clicked.connect(self.test)

    def populate_ui(self, config: BitstampConfig):
        self.ui.key.setText(config.key)
        self.ui.secret.setText(config.secret)
        self.ui.username.setText(config.username)

    def get_config(self) -> BitstampConfig:
        config = BitstampConfig(
            key=self.ui.key.text(),
            secret=self.ui.secret.text(),
            username=self.ui.username.text(),
        )
        return config

    def test(self) -> None:
        try:
            marketplace = BitstampMarketplace(self.get_config())
            marketplace.get_balance()
        except Exception as e:
            handle_exception_with_dialog(e)
        else:
            show_success_dialog("Bitstamp is configured correctly.")


class CCXTPaneController:
    def __init__(self, ui: CCXTPane):
        self.ui = ui
        self.ui.test.clicked.connect(self.test)

    def populate_ui(self, config: Optional[CCXTConfig]):
        if config is not None:
            self.ui.exchange.setText(config.exchange)
            self.ui.parameters.setText(yaml.dump(config.parameters))

    def get_config(self) -> CCXTConfig:
        config = CCXTConfig(
            exchange=self.ui.exchange.text(),
            parameters=yaml.safe_load(self.ui.parameters.toPlainText()),
        )
        return config

    def test(self) -> None:
        try:
            marketplace = CCXTMarketplace(self.get_config())
            marketplace.get_balance()
        except Exception as e:
            handle_exception_with_dialog(e)
        else:
            show_success_dialog("CCXT is configured correctly.")


class KrakenWithdrawalPaneController:
    def __init__(self, ui: KrakenWithdrawalPane):
        self.ui = ui
        self.configs: list[KrakenWithdrawalConfig] = []

        ui.add.clicked.connect(self.add)
        ui.edit.clicked.connect(self.edit)
        ui.delete.clicked.connect(self.delete)

    def populate_ui(self, configs: Iterable[KrakenWithdrawalConfig]):
        self.configs = list(configs)
        for config in self.configs:
            self.ui.list.addItem(config.coin)

    def get_config(self) -> dict[str, KrakenWithdrawalConfig]:
        return {c.coin: c for c in self.configs}

    def update_row(self, row: int) -> None:
        self.ui.list.item(row).setText(self.configs[row].coin)

    def add(self) -> None:
        new = KrakenWithdrawalConfig(coin="New", target="New", fee_limit_percent=0.0)
        self.configs.append(new)
        self.ui.list.addItem(new.coin)

    def edit(self) -> None:
        row = self.ui.list.currentRow()
        if row < 0:
            return
        self.edit_window = KrakenWithdrawalEditWindow()
        self.edit_window_controller = KrakenWithdrawalEditWindowController(
            self, self.edit_window, self.configs[row], row
        )
        self.edit_window_controller.populate_ui()
        self.edit_window.show()

    def delete(self) -> None:
        row = self.ui.list.currentRow()
        self.ui.list.takeItem(row)
        del self.configs[row]


class KrakenWithdrawalEditWindowController:
    def __init__(
        self,
        parent: KrakenWithdrawalPaneController,
        ui: KrakenWithdrawalEditWindow,
        spec: KrakenWithdrawalConfig,
        row: int,
    ):
        self.parent = parent
        self.ui = ui
        self.spec = spec
        self.row = row

        self.ui.save.clicked.connect(self.save)
        self.ui.cancel.clicked.connect(self.cancel)

    def populate_ui(self) -> None:
        self.ui.coin.setText(self.spec.coin)
        self.ui.target.setText(self.spec.target)
        self.ui.fee_limit.setText(str(self.spec.fee_limit_percent))

    def _parse_values(self) -> None:
        self.spec.coin = self.ui.coin.text()
        self.spec.target = self.ui.target.text()

        try:
            self.spec.fee_limit_percent = float(self.ui.fee_limit.text())
        except ValueError as e:
            raise RuntimeError(
                f"Cannot parse fee limit {self.ui.fee_limit.text()}. Make sure it is a decimal number."
            ) from e

    def save(self) -> None:
        try:
            self._parse_values()
        except RuntimeError as e:
            handle_exception_with_dialog(e)
            return

        self.parent.update_row(self.row)
        self.ui.close()

    def cancel(self) -> None:
        self.ui.close()


class TriggerPaneController:
    def __init__(self, ui: TriggerPane):
        self.ui = ui
        self.specs: list[TriggerSpec] = []

        ui.add.clicked.connect(self.add)
        ui.edit.clicked.connect(self.edit)
        ui.delete.clicked.connect(self.delete)

    def add(self) -> None:
        new_spec = TriggerSpec(
            name="New Trigger", asset_pair=AssetPair("", ""), cooldown_minutes=1
        )
        self.specs.append(new_spec)
        self.ui.list.addItem(new_spec.name)

    def edit(self) -> None:
        row = self.ui.list.currentRow()
        if row < 0:
            return
        self.edit_window = TriggerEditWindow()
        self.edit_window_controller = TriggerEditWindowController(
            self, self.edit_window, self.specs[row], row
        )
        self.edit_window_controller.populate_ui()
        self.edit_window.show()

    def delete(self) -> None:
        row = self.ui.list.currentRow()
        self.ui.list.takeItem(row)
        del self.specs[row]

    def populate_ui(self, specs: list[TriggerSpec]):
        self.specs = specs
        for spec in specs:
            self.ui.list.addItem(spec.name)

    def update_row(self, row: int) -> None:
        self.ui.list.item(row).setText(self.specs[row].name)

    def get_config(self) -> list[TriggerSpec]:
        return self.specs


class SingleTriggerEditController:
    def __init__(self, ui: SingleTriggerEdit, spec: TriggerSpec):
        self.ui = ui
        self.spec = spec

        self.set_spec()

    def set_spec(self) -> None:
        self.ui.name.setText(self.spec.name)
        self.ui.coin.setText(self.spec.asset_pair.coin)
        self.ui.fiat.setText(self.spec.asset_pair.fiat)
        self.ui.cooldown_minutes.setText(str(self.spec.cooldown_minutes))
        if self.spec.volume_fiat:
            self.ui.volume_fiat.setText(str(self.spec.volume_fiat))
            self.ui.volume_fiat_type.setCurrentText("absolute")
        elif self.spec.percentage_fiat:
            self.ui.volume_fiat.setText(str(self.spec.percentage_fiat))
            self.ui.volume_fiat_type.setCurrentText("percent")
        if self.spec.delay_minutes:
            self.ui.delay_minutes.setText(str(self.spec.delay_minutes))
        if self.spec.fear_and_greed_index_below:
            self.ui.fear_and_greed_index_below.setText(
                str(self.spec.fear_and_greed_index_below)
            )
        if self.spec.drop_percentage:
            self.ui.drop_percentage.setText(str(self.spec.drop_percentage))
        if self.spec.start is not None:
            self.ui.start.setDateTime(self.spec.start)

    def get_spec(self) -> None:
        self.spec.name = self.ui.name.text()
        self.spec.asset_pair.coin = self.ui.coin.text()
        self.spec.asset_pair.fiat = self.ui.fiat.text()
        try:
            self.spec.cooldown_minutes = int(self.ui.cooldown_minutes.text())
        except ValueError as e:
            raise RuntimeError(
                f"Cannot parse cooldown value {self.ui.cooldown_minutes.text()}. Make sure it is a decimal number."
            ) from e

        try:
            volume_fiat = float(self.ui.volume_fiat.text())
        except ValueError as e:
            raise RuntimeError(
                f"Cannot parse volume fiat {self.ui.volume_fiat.text()}. Make sure it is a decimal number."
            ) from e
        if self.ui.volume_fiat_type.currentText() == "absolute":
            self.spec.volume_fiat = volume_fiat
            self.spec.percentage_fiat = None
        else:
            self.spec.volume_fiat = None
            self.spec.percentage_fiat = volume_fiat

        if self.ui.delay_minutes.text():
            try:
                self.spec.delay_minutes = int(self.ui.delay_minutes.text())
            except ValueError as e:
                raise RuntimeError(
                    f"Cannot parse delay value {self.ui.delay_minutes.text()}. Make sure it is an integer number."
                ) from e
        else:
            self.spec.delay_minutes = None

        if self.ui.fear_and_greed_index_below.text():
            try:
                self.spec.fear_and_greed_index_below = int(
                    self.ui.fear_and_greed_index_below.text()
                )
            except ValueError as e:
                raise RuntimeError(
                    f"Cannot parse Fear & Greed value {self.ui.fear_and_greed_index_below.text()}. Make sure it is an integer number."
                ) from e
        else:
            self.spec.fear_and_greed_index_below = None

        if self.ui.drop_percentage.text():
            self.spec.drop_percentage = float(self.ui.drop_percentage.text())
        else:
            self.spec.drop_percentage = None

        self.spec.start = self.ui.start.dateTime().toPython()


class TriggerEditWindowController:
    def __init__(
        self,
        parent: TriggerPaneController,
        ui: TriggerEditWindow,
        spec: TriggerSpec,
        row: int,
    ):
        self.parent = parent
        self.ui = ui
        self.spec = spec
        self.row = row

        self.ui.save.clicked.connect(self.save)
        self.ui.cancel.clicked.connect(self.cancel)

        self.edit_controller = SingleTriggerEditController(
            self.ui.single_trigger_edit, self.spec
        )

    def populate_ui(self) -> None:
        self.edit_controller.set_spec()

    def _parse_values(self) -> None:
        self.edit_controller.get_spec()

    def save(self) -> None:
        try:
            self._parse_values()
        except RuntimeError as e:
            handle_exception_with_dialog(e)
            return

        self.parent.update_row(self.row)
        self.ui.close()

    def cancel(self) -> None:
        self.ui.close()
