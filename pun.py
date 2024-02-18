#!/usr/bin/env python3

"""
pun - p(acman) u(pdate) n(otifier)
----------------------------------
Checks for pacman package updates and shows the status in the system tray.
    Intended to be used in Arch Linux (main target) and remixes (but without
    active support).

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

Dependencies: python-pyqt6, python-watchdog, pacman-contrib
"""

# Settings:
MONITOR_PATHS = ["/usr", "/etc/pacman.d"]

REFRESH_INTERVAL = 600

ICON_UP_TO_DATE = "icons/pun_green.png"
ICON_UPDATING = "icons/pun_orange.png"
ICON_UPDATES_AVAILABLE = "icons/pun_red.png"

import os
import sys
import subprocess
import time
import datetime

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from threading import Timer

class PerpetualTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class WatchDog(FileSystemEventHandler):
    def __init__(self, callback):
        # maximum frequency / minimum interval
        self.interval = datetime.timedelta(seconds=30)
        self.last_event = datetime.datetime.now() - self.interval
        self.callback = callback

    def on_modified(self, event):
        this_event = datetime.datetime.now()
        # make sure that we have a minium interval of 30s
        if this_event - self.last_event < self.interval:
            return
        else:
            self.last_event = this_event
            self.callback()

class UpdateableTrayIcon(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        # set icon to updating at start
        self.state_updating()

    def update_icon(self, new_icon):
        icon = QIcon(os.path.join(os.path.dirname(__file__), new_icon))
        self.setIcon(icon)
        self.setVisible(True)

    def state_up_to_date(self):
        self.update_icon(ICON_UP_TO_DATE)

    def state_updating(self):
        self.update_icon(ICON_UPDATING)

    def state_updates_available(self):
        self.update_icon(ICON_UPDATES_AVAILABLE)

class PacmanUpdateNotifier(QApplication):
    def __init__(self, args):
        super().__init__(args)
        # number of refreshes
        self.n_refresh = 0

        # create an asynchronous timer for regular refreshes
        self.timer = PerpetualTimer(REFRESH_INTERVAL, self.update)

        # tray icon
        self.tray = UpdateableTrayIcon()
        self.tray.setToolTip("Initializing...")
        self.tray.state_updating()

        # menu
        self.menu = QMenu()
        # add default actions
        self.quit_action = QAction("Exit")
        self.menu.addAction(self.quit_action)
        self.quit_action.triggered.connect(self.terminate)

        self.update_action = QAction("Refresh")
        self.menu.addAction(self.update_action)
        self.update_action.triggered.connect(self.update)

        self.tray.setContextMenu(self.menu)

        # monitor changes in specified directories
        self.watchdog = WatchDog(self.update)
        self.observer = Observer()
        for path in MONITOR_PATHS:
            self.observer.schedule(self.watchdog, path=path, recursive=False)
        self.observer.start()

        # begin with initial refresh
        self.update()

        self.timer.start()

    def terminate(self):
        # stop the perpetual timer
        self.timer.cancel()
        # stop the watchdog
        self.observer.stop()
        self.quit()

    def update(self):
        self.n_refresh += 1
        self.tray.setToolTip("Refreshing...")
        self.update_action.setText("Refreshing...")
        self.tray.state_updating()

        shell_cmd = "checkupdates | wc -l"
        process = subprocess.Popen(
            shell_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        output = process.communicate()[0].decode("utf-8").rstrip()
        try:
            output = int(output)
            if output > 0:
                self.tray.state_updates_available()
                self.tray.setToolTip("Available update: %i (%s)" % (output, datetime.datetime.now().strftime("%H:%M:%S")))
            else:
                self.tray.state_up_to_date()
                self.tray.setToolTip("Up to date (%s)" % (datetime.datetime.now().strftime("%H:%M:%S")))
        except:
            self.tray.state_updating()
            self.tray.setToolTip("Last refresh failed (%s)" % (datetime.datetime.now().strftime("%H:%M:%S")))

        self.update_action.setText("Refresh")

if __name__ == "__main__":
    pun = PacmanUpdateNotifier(sys.argv)
    sys.exit(pun.exec())
