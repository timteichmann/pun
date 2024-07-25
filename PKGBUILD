# Maintainer: Tim Teichmann <onlineaccounts@mailbox.org>
pkgname=pun
pkgver=1.0
pkgrel=1
pkgdesc="Checks for pacman package updates and shows the status in the system tray"
arch=('any')
url="https://github.com/timteichmann/pun/"
license=('GPL-3.0-or-later')
depends=('pacman-contrib' 'python' 'python-pyqt6' 'python-watchdog')
makedepends=('python-setuptools')
source=("https://github.com/timteichmann/$pkgname/archive/refs/tags/$pkgver.tar.gz")
sha256sums=('455513f9dd16e27cae3b580ccd0d70918bb7701ad530bd53ee8dd5935b1654bc')

build() {
	cd "$pkgname-$pkgver"
	python setup.py build
}

package() {
	cd "$pkgname-$pkgver"
	python setup.py install --root="$pkgdir" --optimize=1
}
