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

# after a failed check, retry after this many seconds; the delay doubles with
# every further failure up to REFRESH_INTERVAL and resets after a success
RETRY_DELAY = 15

# keep showing the checking icon for this many failures in a row before
# showing the error icon, e.g. while the network comes up after boot
QUIET_FAILURES = 2

# icon sizes to provide; the pixel art is scaled by whole numbers and centred,
# so it stays sharp at every size
ICON_SIZES = [16, 20, 22, 24, 32, 40, 44, 48, 64, 96, 128, 256]

import sys
import datetime

from PyQt6.QtCore import QFileSystemWatcher, QProcess, QTimer, Qt, pyqtSlot
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction, QColor, QIcon, QImage, QPainter, QPixmap

# relative import when installed, plain import when run as pun/pun.py
if __package__:
    from . import sprites
else:
    import sprites

def make_icon(canvas, state):
    """Turns a sprite canvas into a QIcon with sharp pixmaps of all sizes."""
    pixels = sprites.to_rgba(canvas, state)
    image = QImage(sprites.SIZE, sprites.SIZE, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    for y, row in enumerate(pixels):
        for x, rgba in enumerate(row):
            if rgba[3]:
                image.setPixelColor(x, y, QColor(*rgba))

    icon = QIcon()
    for size in ICON_SIZES:
        scale = max(1, size // sprites.SIZE)
        scaled = image.scaled(sprites.SIZE * scale, sprites.SIZE * scale,
                              Qt.AspectRatioMode.IgnoreAspectRatio,
                              Qt.TransformationMode.FastTransformation)
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        offset = (size - scaled.width()) // 2
        painter.drawImage(offset, offset, scaled)
        painter.end()
        icon.addPixmap(pixmap)
    return icon

class UpdateableTrayIcon(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        self.frames = []
        self.durations = []
        self.frame = 0
        # shows the next frame of the current animation
        self.animation_timer = QTimer(self)
        self.animation_timer.setSingleShot(True)
        self.animation_timer.timeout.connect(self.next_frame)
        # set icon to updating at start
        self.state_updating()

    def animate(self, state, count=0):
        canvases, self.durations = sprites.animation(state, count)
        self.frames = [make_icon(canvas, state) for canvas in canvases]
        self.frame = -1
        self.animation_timer.stop()
        self.next_frame()
        self.setVisible(True)

    @pyqtSlot()
    def next_frame(self):
        self.frame = (self.frame + 1) % len(self.frames)
        self.setIcon(self.frames[self.frame])
        if len(self.frames) > 1:
            self.animation_timer.start(self.durations[self.frame])

    def state_up_to_date(self):
        self.animate("up_to_date")

    def state_updating(self):
        self.animate("checking")

    def state_updates_available(self, count):
        self.animate("updates", count)

    def state_error(self):
        self.animate("error")

class PacmanUpdateNotifier(QApplication):
    def __init__(self, args):
        super().__init__(args)
        # number of refreshes
        self.n_refresh = 0
        # number of failed checks in a row
        self.failures = 0

        # timer for regular refreshes (runs in the Qt event loop)
        self.timer = QTimer(self)
        self.timer.setInterval(REFRESH_INTERVAL * 1000)
        self.timer.timeout.connect(self.update)

        # timer for retrying sooner after a failed check
        self.retry_timer = QTimer(self)
        self.retry_timer.setSingleShot(True)
        self.retry_timer.timeout.connect(self.update)

        # tray icon
        self.tray = UpdateableTrayIcon()
        self.tray.setToolTip("Initializing...")
        self.tray.state_updating()

        # menu
        self.menu = QMenu()
        # add default actions
        self.update_action = QAction("Refresh")
        self.menu.addAction(self.update_action)
        self.update_action.triggered.connect(self.update)

        self.menu.addSeparator()

        self.quit_action = QAction("Quit")
        self.menu.addAction(self.quit_action)
        self.quit_action.triggered.connect(self.terminate)

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
        # stop the refresh timer and the animation
        self.timer.stop()
        self.retry_timer.stop()
        self.tray.animation_timer.stop()
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

        # this check replaces a scheduled retry
        self.retry_timer.stop()
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
            self.failures = 0
            count = len(output.splitlines())
            if count > 0:
                self.tray.state_updates_available(count)
                self.tray.setToolTip("%i update%s available (%s)" % (count, "" if count == 1 else "s", now))
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
        self.failures += 1
        delay = min(RETRY_DELAY * 2 ** (self.failures - 1), REFRESH_INTERVAL)
        self.retry_timer.start(delay * 1000)
        if self.failures <= QUIET_FAILURES:
            # likely transient (e.g. no network yet), keep the checking icon
            self.tray.setToolTip("Refresh failed, retrying in %i s (%s)" % (delay, now))
        else:
            self.tray.state_error()
            self.tray.setToolTip("Last refresh failed, retrying in %i s (%s)" % (delay, now))
        self.check_done()

    def check_done(self):
        self.update_action.setText("Refresh")
        if self.refresh_pending:
            self.refresh_pending = False
            self.update()

def main():
    pun = PacmanUpdateNotifier(sys.argv)
    sys.exit(pun.exec())

if __name__ == "__main__":
    main()
