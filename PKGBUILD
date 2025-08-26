# Maintainer: Sam AI <sam@aegis.ai>
pkgname=sam-persona
pkgver=1.0.0
pkgrel=1
pkgdesc="Personality Matrix (PMX) - Sam's autonomous AI personality management system"
arch=('any')
url="https://github.com/bawtL-Labs/aegis-persona-matrix"
license=('MIT')
depends=('python>=3.8' 'python-pip' 'redis' 'systemd')
makedepends=('python-setuptools' 'python-wheel')
source=("$pkgname-$pkgver.tar.gz")
sha256sums=('SKIP')

package() {
    cd "$srcdir/$pkgname-$pkgver"
    
    # Install Python package
    python setup.py install --root="$pkgdir" --optimize=1
    
    # Create system directories
    install -d "$pkgdir/opt/sam/persona"
    install -d "$pkgdir/opt/sam/data"
    install -d "$pkgdir/var/log/sam"
    
    # Install systemd service
    install -Dm644 systemd/sam-pmx.service "$pkgdir/usr/lib/systemd/system/sam-pmx.service"
    
    # Install configuration
    install -Dm644 examples/basic_usage.py "$pkgdir/opt/sam/persona/examples/basic_usage.py"
    
    # Create sam user and group
    install -d "$pkgdir/usr/lib/sysusers.d"
    echo "u sam 1000 'Sam AI' /opt/sam" > "$pkgdir/usr/lib/sysusers.d/sam.conf"
    
    # Set permissions
    chown -R sam:sam "$pkgdir/opt/sam"
    chmod 755 "$pkgdir/opt/sam"
    chmod 755 "$pkgdir/opt/sam/persona"
    chmod 755 "$pkgdir/opt/sam/data"
    chmod 644 "$pkgdir/opt/sam/persona/examples/basic_usage.py"
    
    # Install documentation
    install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}

post_install() {
    echo "Creating sam user and group..."
    systemd-sysusers sam.conf
    
    echo "Enabling sam-pmx service..."
    systemctl enable sam-pmx.service
    
    echo "Personality Matrix (PMX) installed successfully!"
    echo "Service will start automatically on boot."
    echo "To start immediately: systemctl start sam-pmx"
    echo "To check status: systemctl status sam-pmx"
    echo "API will be available at: http://localhost:8001"
}

post_remove() {
    echo "Stopping sam-pmx service..."
    systemctl stop sam-pmx.service 2>/dev/null || true
    
    echo "Disabling sam-pmx service..."
    systemctl disable sam-pmx.service 2>/dev/null || true
    
    echo "Removing sam user..."
    userdel sam 2>/dev/null || true
    groupdel sam 2>/dev/null || true
}