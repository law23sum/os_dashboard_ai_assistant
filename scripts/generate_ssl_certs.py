#!/usr/bin/env python3
"""
Generate self-signed SSL certificates for local development.
These certificates allow HTTPS connections to the local server.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CERTS_DIR = REPO_ROOT / "certs"
CERT_FILE = CERTS_DIR / "cert.pem"
KEY_FILE = CERTS_DIR / "key.pem"

def generate_certificates():
    """Generate self-signed SSL certificates for local development."""
    # Create certs directory if it doesn't exist
    CERTS_DIR.mkdir(exist_ok=True)
    
    # Check if certificates already exist
    if CERT_FILE.exists() and KEY_FILE.exists():
        print(f"✅ SSL certificates already exist at:")
        print(f"   Certificate: {CERT_FILE}")
        print(f"   Private Key: {KEY_FILE}")
        print("\nTo regenerate, delete these files and run this script again.")
        return 0
    
    print("🔐 Generating self-signed SSL certificates for local development...")
    print(f"   Output directory: {CERTS_DIR}")
    
    # Generate certificate using openssl
    try:
        subprocess.run(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:4096",
                "-keyout",
                str(KEY_FILE),
                "-out",
                str(CERT_FILE),
                "-days",
                "365",
                "-nodes",
                "-subj",
                "/C=US/ST=State/L=City/O=OS Dashboard/CN=localhost",
            ],
            check=True,
            capture_output=True,
        )
        
        print(f"✅ SSL certificates generated successfully!")
        print(f"   Certificate: {CERT_FILE}")
        print(f"   Private Key: {KEY_FILE}")
        print("\n⚠️  Note: These are self-signed certificates for local development.")
        print("   Your browser will show a security warning. Click 'Advanced' and")
        print("   'Proceed to localhost' to continue.")
        print("\n🔒 The server will now use HTTPS when these certificates are present.")
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating certificates: {e}")
        print("\nMake sure OpenSSL is installed:")
        print("  macOS: Already installed")
        print("  Linux: sudo apt-get install openssl")
        print("  Windows: Install from https://slproweb.com/products/Win32OpenSSL.html")
        return 1
    except FileNotFoundError:
        print("❌ OpenSSL not found. Please install OpenSSL to generate certificates.")
        print("\nInstallation:")
        print("  macOS: Already installed")
        print("  Linux: sudo apt-get install openssl")
        print("  Windows: Install from https://slproweb.com/products/Win32OpenSSL.html")
        return 1

if __name__ == "__main__":
    sys.exit(generate_certificates())


