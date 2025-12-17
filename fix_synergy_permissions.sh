#!/bin/bash
# Script to fix Synergy.app permissions and allow deletion

echo "Fixing Synergy.app permissions..."
echo "You may be prompted for your password."

# Change ownership to current user
sudo chown -R $(id -un):admin /Applications/Synergy.app

# Remove extended attributes
sudo xattr -dr com.apple.quarantine /Applications/Synergy.app
sudo xattr -dr com.apple.macl /Applications/Synergy.app
sudo xattr -dr com.apple.provenance /Applications/Synergy.app

# Unlock any locked files
sudo chflags -R nouchg,noschg /Applications/Synergy.app

# Ensure write permissions
sudo chmod -R u+w /Applications/Synergy.app

echo "Done! You should now be able to delete Synergy.app"





