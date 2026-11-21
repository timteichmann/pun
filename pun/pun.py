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
"""

# Settings:
# directories whose contents change when packages are installed, upgraded or
# removed (local package database) or when the mirror list is replaced
MONITOR_PATHS = ["/var/lib/pacman/local", "/etc/pacman.d"]

# refresh this many seconds after the last change in MONITOR_PATHS, so that a
# running pacman transaction is finished before checking again
MONITOR_DELAY = 5

REFRESH_INTERVAL = 600

ICON_UP_TO_DATE = "icons/pun_green.png"
ICON_UPDATING = "icons/pun_orange.png"
ICON_UPDATES_AVAILABLE = "icons/pun_red.png"
ICON_ERROR = "icons/pun_grey.png"

import os
import sys
import time
import datetime

from PyQt6.QtCore import QFileSystemWatcher, QProcess, QTimer, pyqtSlot
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction

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

    def state_error(self):
        self.update_icon(ICON_ERROR)

class PacmanUpdateNotifier(QApplication):
    def __init__(self, args):
        super().__init__(args)
        # number of refreshes
        self.n_refresh = 0

        # timer for regular refreshes (runs in the Qt event loop)
        self.timer = QTimer(self)
        self.timer.setInterval(REFRESH_INTERVAL * 1000)
        self.timer.timeout.connect(self.update)

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

        # monitor changes in specified directories; every change restarts the
        # delay timer, so the refresh happens once the changes have stopped
        self.monitor_timer = QTimer(self)
        self.monitor_timer.setSingleShot(True)
        self.monitor_timer.setInterval(MONITOR_DELAY * 1000)
        self.monitor_timer.timeout.connect(self.update)
        self.watcher = QFileSystemWatcher(MONITOR_PATHS, self)
        self.watcher.directoryChanged.connect(lambda path: self.monitor_timer.start())

        # checkupdates runs asynchronously so the event loop stays responsive
        self.process = QProcess(self)
        self.process.finished.connect(self.check_finished)
        self.process.errorOccurred.connect(self.check_error)
        # set when a refresh is requested while a check is already running
        self.refresh_pending = False

        # begin with initial refresh once the event loop is running
        QTimer.singleShot(0, self.update)

        self.timer.start()

    def terminate(self):
        # stop the refresh timer
        self.timer.stop()
        # stop watching for changes
        self.monitor_timer.stop()
        self.watcher.directoryChanged.disconnect()
        # abort a running check without scheduling another one
        self.refresh_pending = False
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.kill()
            self.process.waitForFinished(1000)
        self.quit()

    @pyqtSlot()
    def update(self):
        # never run two checks at once; refresh again after the current one
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.refresh_pending = True
            return

        self.n_refresh += 1
        self.tray.setToolTip("Refreshing...")
        self.update_action.setText("Refreshing...")
        self.tray.state_updating()

        self.process.start("checkupdates", [])

    def check_finished(self, exit_code, exit_status):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        output = bytes(self.process.readAllStandardOutput()).decode("utf-8", "replace")

        # checkupdates exit codes: 0 = updates available, 2 = no updates,
        # anything else = failure
        if exit_status == QProcess.ExitStatus.NormalExit and exit_code in (0, 2):
            count = len(output.splitlines())
            if count > 0:
                self.tray.state_updates_available()
                self.tray.setToolTip("Available update: %i (%s)" % (count, now))
            else:
                self.tray.state_up_to_date()
                self.tray.setToolTip("Up to date (%s)" % now)
        else:
            self.check_failed()
            return

        self.check_done()

    def check_error(self, error):
        # a crashed process also emits finished(); only a failed start doesn't
        if error == QProcess.ProcessError.FailedToStart:
            self.check_failed()

    def check_failed(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.tray.state_error()
        self.tray.setToolTip("Last refresh failed (%s)" % now)
        self.check_done()

    def check_done(self):
        self.update_action.setText("Refresh")
        if self.refresh_pending:
            self.refresh_pending = False
            self.update()

if __name__ == "__main__":
    pun = PacmanUpdateNotifier(sys.argv)
    sys.exit(pun.exec())
