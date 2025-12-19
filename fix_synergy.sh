#!/bin/bash
# Quick fix for Synergy.app permissions - run this in Terminal

sudo chown -R $(id -un):admin /Applications/Synergy.app && \
sudo xattr -dr com.apple.quarantine /Applications/Synergy.app && \
sudo xattr -dr com.apple.macl /Applications/Synergy.app && \
sudo xattr -dr com.apple.provenance /Applications/Synergy.app && \
sudo chflags -R nouchg,noschg /Applications/Synergy.app && \
sudo chmod -R u+w /Applications/Synergy.app && \
echo "✅ Permissions fixed! You can now delete Synergy.app"







