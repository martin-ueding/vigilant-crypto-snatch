import pprint
from typing import Dict
from typing import List

import yaml

from ...configuration import Configuration
from ...configuration import YamlConfiguration
from ...core import AssetPair
from ...historical import CryptoCompareConfig
from ...marketplace import KrakenConfig
from ...notifications import TelegramConfig
from ...triggers import TriggerSpec
from ..ui.configuration import ConfigurationTab
from ..ui.configuration import CryptoComparePanel
from ..ui.configuration import GeneralPanel
from ..ui.configuration import KrakenPane
from ..ui.configuration import MarketplacePane
from ..ui.configuration import TelegramPane
from ..ui.configuration import TriggerEditWindow
from ..ui.configuration import TriggerPane


class ConfigurationTabController:
    def __init__(self, ui: ConfigurationTab):
        self.ui = ui

        self.general_panel_controller = GeneralPanelController(ui.general_panel)
        self.crypto_compare_panel_controller = CryptoComparePanelController(
            ui.crypto_compare_panel
        )
        self.telegram_pane_controller = TelegramPaneController(ui.telegram_panel)
        self.marketplace_pane_controller = MarketplacePaneController(
            ui.marketplace_pane
        )
        self.trigger_pane_controller = TriggerPaneController(ui.trigger_pane)

        ui.save_button.clicked.connect(self.save)

        self.populate_ui()

    def save(self) -> None:
        config_dict = {}
        try:
            config_dict.update(self.general_panel_controller.get_config())
            config_dict[
                "crypto_compare"
            ] = self.crypto_compare_panel_controller.get_config().to_primitives()
            config_dict[
                "telegram"
            ] = self.telegram_pane_controller.get_config().to_primitives()
            config_dict["triggers"] = [
                x.to_primitives() for x in self.trigger_pane_controller.get_config()
            ]
        except RuntimeError as e:
            print(e)
            return
        pprint.pprint(config_dict)
        with open("gui-generated-config.yml", "w") as f:
            yaml.dump(config_dict, f)

    def populate_ui(self) -> None:
        try:
            config = YamlConfiguration()
        except RuntimeError as e:
            print(e)
            return
        self.general_panel_controller.populate_ui(config.get_polling_interval())
        self.crypto_compare_panel_controller.populate_ui(
            config.get_crypto_compare_config()
        )
        self.telegram_pane_controller.populate_ui(config.get_telegram_config())
        self.marketplace_pane_controller.populate_ui(config)
        self.trigger_pane_controller.populate_ui(config.get_trigger_config())


class GeneralPanelController:
    def __init__(self, general_panel: GeneralPanel):
        self.ui = general_panel

    def get_config(self) -> Dict:
        text = self.ui.poll_interval_edit.text()
        try:
            sleep = int(text)
        except ValueError as e:
            raise RuntimeError(
                f"Cannot parse input {text}. Make sure that it is an integer."
            ) from e
        return {"sleep": sleep}

    def populate_ui(self, polling_inverval: int) -> None:
        self.ui.poll_interval_edit.setText(str(polling_inverval))


class CryptoComparePanelController:
    def __init__(self, ui: CryptoComparePanel):
        self.ui = ui

    def get_config(self) -> CryptoCompareConfig:
        api_key = self.ui.api_key_line_edit.text()
        return CryptoCompareConfig(api_key)

    def populate_ui(self, config: CryptoCompareConfig) -> None:
        self.ui.api_key_line_edit.setText(config.api_key)


class TelegramPaneController:
    def __init__(self, ui: TelegramPane):
        self.ui = ui

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


class MarketplacePaneController:
    def __init__(self, ui: MarketplacePane):
        self.ui = ui

        self.kraken_pane_controller = KrakenPaneController(self.ui.kraken_pane)

    def populate_ui(self, config: Configuration):
        self.kraken_pane_controller.populate_ui(config.get_kraken_config())


class KrakenPaneController:
    def __init__(self, ui: KrakenPane):
        self.ui = ui

    def populate_ui(self, config: KrakenConfig):
        self.ui.api_key.setText(config.key)
        self.ui.api_secret.setText(config.secret)
        self.ui.prefer_fee.setChecked(config.prefer_fee_in_base_currency)


class TriggerPaneController:
    def __init__(self, ui: TriggerPane):
        self.ui = ui
        self.specs: List[TriggerSpec] = []

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
        print("Edit")
        row = self.ui.list.currentRow()
        if row < 0:
            return
        self.edit_window = TriggerEditWindow()
        self.edit_window_controller = TriggerEditWindowController(
            self, self.edit_window, self.specs[row], row
        )
        self.edit_window_controller.populate_ui()
        self.edit_window.show()
        print("Done")

    def delete(self) -> None:
        print("Delete")
        row = self.ui.list.currentRow()
        print(row)
        self.ui.list.takeItem(row)
        del self.specs[row]

    def populate_ui(self, specs: List[TriggerSpec]):
        self.specs = specs
        for spec in specs:
            self.ui.list.addItem(spec.name)

    def update_row(self, row: int) -> None:
        self.ui.list.item(row).setText(self.specs[row].name)

    def get_config(self) -> List[TriggerSpec]:
        return self.specs


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

    def populate_ui(self) -> None:
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

    def save(self) -> None:
        self.spec.name = self.ui.name.text()
        self.spec.asset_pair.coin = self.ui.coin.text()
        self.spec.asset_pair.fiat = self.ui.fiat.text()
        self.spec.cooldown_minutes = int(self.ui.cooldown_minutes.text())

        if self.ui.volume_fiat_type.currentText() == "absolute":
            self.spec.volume_fiat = float(self.ui.volume_fiat.text())
            self.spec.percentage_fiat = None
        else:
            self.spec.volume_fiat = None
            self.spec.percentage_fiat = float(self.ui.volume_fiat.text())

        if self.ui.delay_minutes.text():
            self.spec.delay_minutes = int(self.ui.delay_minutes.text())
        else:
            self.spec.delay_minutes = None

        if self.ui.fear_and_greed_index_below.text():
            self.spec.fear_and_greed_index_below = int(
                self.ui.fear_and_greed_index_below.text()
            )
        else:
            self.spec.fear_and_greed_index_below = None

        print(self.spec)
        self.parent.update_row(self.row)
        self.ui.close()

    def cancel(self) -> None:
        self.ui.close()
