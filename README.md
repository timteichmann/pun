# pun – p(acman) u(pdate) n(otifier)

pun shows a small icon in the system tray that tells you whether package
updates are available for Arch Linux.

| Icon   | Meaning                                         |
|--------|-------------------------------------------------|
| green  | the system is up to date                        |
| red    | updates are available (the tooltip says how many) |
| orange | checking for updates                            |
| grey   | the last check failed                           |

pun uses `checkupdates` from `pacman-contrib`, so it never touches the
system's sync databases. It checks every 10 minutes, on demand via the
*Refresh* menu entry, and a few seconds after pacman has installed, upgraded
or removed packages.

## Requirements

- Python 3.9 or newer
- PyQt6 (`python-pyqt6`)
- `checkupdates` (`pacman-contrib`)
- a desktop environment or panel with a system tray

## Installation

Clone the repository and build and install the package with the included
`PKGBUILD`:

    git clone https://github.com/timteichmann/pun.git
    cd pun
    makepkg -si

makepkg builds the latest commit of the clone. To update, pull and build
again:

    git pull
    makepkg -si

If the version has not changed since the last build, add `-f` to rebuild
anyway.

To start pun when you log in, copy its desktop entry to your autostart
folder:

    cp /usr/share/applications/pun.desktop ~/.config/autostart/

## License

GPL-3.0-or-later, see [LICENSE](LICENSE).
