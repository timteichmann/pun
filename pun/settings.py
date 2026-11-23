"""
Settings of pun: storage and the settings dialog.

Copyright (C) 2024 Tim Teichmann

This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                             QFormLayout, QLabel, QLineEdit, QMessageBox,
                             QVBoxLayout)

# relative import when installed, plain import when run as pun/pun.py
if __package__:
    from .terminal import PLACEHOLDER, automatic_terminal, installed_terminals, launch_argv
else:
    from terminal import PLACEHOLDER, automatic_terminal, installed_terminals, launch_argv

DEFAULTS = {
    # empty: detect automatically
    "terminal": "",
    "command": "sudo pacman -Syu",
    "keep_open": True,
    "click_to_update": True,
}

def load():
    """Returns the stored settings, with defaults for missing ones."""
    store = QSettings("pun", "pun")
    return {key: store.value(key, default, type=type(default))
            for key, default in DEFAULTS.items()}

def save(settings):
    store = QSettings("pun", "pun")
    for key, value in settings.items():
        store.setValue(key, value)
    store.sync()

class SettingsDialog(QDialog):
    AUTOMATIC = "Automatic"

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("pun Settings")
        self.settings = dict(settings)

        self.terminal = QComboBox()
        self.terminal.setEditable(True)
        auto = automatic_terminal()
        self.terminal.addItem("%s (%s)" % (self.AUTOMATIC, auto or "none found"), "")
        for name in installed_terminals():
            self.terminal.addItem(name, name)
        index = self.terminal.findData(settings["terminal"])
        if index >= 0:
            self.terminal.setCurrentIndex(index)
        else:
            self.terminal.setEditText(settings["terminal"])

        terminal_hint = QLabel("Choose a terminal or enter a command line with %s "
                               "where the update command goes, e.g.\n"
                               "myterm --run %s" % (PLACEHOLDER, PLACEHOLDER))
        terminal_hint.setEnabled(False)

        self.command = QLineEdit(settings["command"])
        self.command.setPlaceholderText(DEFAULTS["command"])

        self.keep_open = QCheckBox("Keep the terminal open after the update")
        self.keep_open.setChecked(settings["keep_open"])

        self.click_to_update = QCheckBox("Clicking the tray icon starts the update")
        self.click_to_update.setChecked(settings["click_to_update"])

        form = QFormLayout()
        form.addRow("Terminal:", self.terminal)
        form.addRow("", terminal_hint)
        form.addRow("Update command:", self.command)
        form.addRow("", self.keep_open)
        form.addRow("", self.click_to_update)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                   | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setMinimumWidth(420)

    def selected_terminal(self):
        text = self.terminal.currentText().strip()
        index = self.terminal.findText(text)
        if index >= 0:
            return self.terminal.itemData(index)
        return text

    def accept(self):
        settings = {
            "terminal": self.selected_terminal(),
            "command": self.command.text().strip() or DEFAULTS["command"],
            "keep_open": self.keep_open.isChecked(),
            "click_to_update": self.click_to_update.isChecked(),
        }
        try:
            launch_argv(settings)
        except ValueError as error:
            QMessageBox.warning(self, "pun Settings", str(error))
            return
        self.settings = settings
        super().accept()
