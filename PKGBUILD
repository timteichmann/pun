# Maintainer: Tim Teichmann <teichmann.dev@mailbox.org>
#
# Builds the committed HEAD of the git repository this PKGBUILD is in:
#   git clone https://github.com/timteichmann/pun.git && cd pun && makepkg -si
pkgname=pun
# the version is maintained in pyproject.toml only
pkgver=$(sed -n 's/^version = "\(.*\)"$/\1/p' "$startdir/pyproject.toml")
pkgrel=1
pkgdesc="Checks for pacman package updates and shows the status in the system tray"
arch=('any')
url="https://github.com/timteichmann/pun/"
license=('GPL-3.0-or-later')
depends=('pacman-contrib' 'python' 'python-pyqt6')
makedepends=('git' 'python-build' 'python-installer' 'python-setuptools' 'python-wheel')
# not named "pun": makepkg keeps its clone next to this PKGBUILD, where pun/
# is the Python package
source=("pun-repo::git+file://$startdir")
sha256sums=('SKIP')

build() {
	cd pun-repo
	python -m build --wheel --no-isolation
}

package() {
	cd pun-repo
	python -m installer --destdir="$pkgdir" dist/*.whl
	install -Dm644 pun.desktop "$pkgdir/usr/share/applications/pun.desktop"
	install -Dm644 pun/icons/pun_green.png "$pkgdir/usr/share/pixmaps/pun.png"
}
