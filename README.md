# pun – p(acman) u(pdate) n(otifier)

pun shows a small icon in the system tray that tells you whether package
updates are available for Arch Linux. The icon is the Package Muncher, an
animated pixel-art creature that eats packages:

| Icon                                       | Meaning                                    |
|--------------------------------------------|--------------------------------------------|
| orange, chomping through a row of parcels  | checking for updates                       |
| red, drooling at a parcel with a number    | updates are available; the number says how many ("!!" for 100 or more) |
| green, resting with a full belly           | the system is up to date                   |
| grey, choking on a parcel                  | the last check failed                      |

pun uses `checkupdates` from `pacman-contrib`, so it never touches the
system's sync databases. It checks every 10 minutes, on demand via the
*Refresh* menu entry, and a few seconds after pacman has installed, upgraded
or removed packages. After a failed check, for example while the network is
not up yet after boot, it retries after 15 seconds, doubling the delay with
every further failure, and only shows the grey icon if the first two retries
fail too.

## Updating the system

Click the tray icon, or choose *Update System* from its menu, to open a
terminal running `sudo pacman -Syu`. Some trays open the menu on every click;
there only the menu entry works. Once pacman is done, pun checks again on its
own.

In *Settings...* you can choose:

- the terminal: *Automatic* uses `xdg-terminal-exec` if installed, otherwise
  `$TERMINAL`, otherwise the first installed terminal pun knows. You can also
  enter a terminal with extra arguments, e.g. `konsole --profile Updates`, or
  any command line with `{cmd}` where the update command goes, e.g.
  `myterm --run {cmd}`.
- the update command, e.g. `paru` to include AUR packages
- whether the terminal stays open after the update
- whether clicking the tray icon starts the update

The settings are stored in `~/.config/pun/pun.conf`.

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
