# Maintainer: Tim Teichmann <onlineaccounts@mailbox.org>
pkgname=pun
pkgver=<x.y>
pkgrel=1
pkgdesc="Checks for pacman package updates and shows the status in the system tray"
arch=('any')
url="https://github.com/timteichmann/pun/"
license=('GPLv3')
depends=('pacman-contrib' 'python-pyqt6' 'python-watchdog')
makedepends=('python-setuptools')
source=("https://github.com/timteichmann/$pkgname/archive/refs/tags/$pkgver.tar.gz")
sha256sums=('<sha256sum x.y.tar.gz>')

build() {
	cd "$pkgname-$pkgver"
	python setup.py build
}

package() {
	cd "$pkgname-$pkgver"
	python setup.py install --root="$pkgdir" --optimize=1
}
