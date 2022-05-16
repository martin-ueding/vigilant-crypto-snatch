from typing import Dict

from ..ui.configuration import ConfigurationTab
from ..ui.configuration import GeneralPanel


class ConfigurationTabController:
    def __init__(self, widget: ConfigurationTab):
        self.widget = widget
        self.general_panel_controller = GeneralPanelController(
            self.widget.general_panel
        )

        self.widget.save_button.clicked.connect(self.save)

    def save(self) -> None:
        config_dict = {}
        try:
            config_dict.update(self.general_panel_controller.get_config())
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
