#!/usr/bin/env python3
"""Script to create the initial admin account."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend_api.routers.auth import init_auth_tables, create_user, UserCreate
from backend_api.db import db_session

def main():
    """Create admin account."""
    print("Initializing authentication tables...")
    init_auth_tables()
    
    print("\nCreating admin account...")
    print("=" * 50)
    
    # Default admin credentials
    admin_data = UserCreate(
        username="admin",
        email="admin@osdashboard.local",
        password="admin123",  # CHANGE THIS IN PRODUCTION!
        full_name="System Administrator"
    )
    
    try:
        admin_user = create_user(admin_data, is_admin=True)
        print(f"✅ Admin account created successfully!")
        print("\n" + "=" * 50)
        print("ADMIN CREDENTIALS:")
        print("=" * 50)
        print(f"Username: {admin_user['username']}")
        print(f"Email: {admin_user['email']}")
        print(f"Password: admin123")
        print(f"User ID: {admin_user['id']}")
        print("\n⚠️  IMPORTANT: Change the default password immediately!")
        print("=" * 50)
        
        # Also create a dummy/test user for testing
        print("\nCreating dummy test user...")
        dummy_data = UserCreate(
            username="testuser",
            email="test@osdashboard.local",
            password="test123",
            full_name="Test User"
        )
        
        dummy_user = create_user(dummy_data, is_admin=False)
        
        # Mark as dummy user
        with db_session() as conn:
            import json
            metadata = json.dumps({"is_dummy": True, "is_test": True})
            conn.execute(
                "UPDATE users SET metadata = ? WHERE id = ?",
                (metadata, dummy_user["id"])
            )
            conn.commit()
        
        print(f"✅ Test user created: {dummy_user['username']}")
        print("=" * 50)
        
    except Exception as e:
        if "already exists" in str(e):
            print("⚠️  Admin account already exists. Skipping creation.")
        else:
            print(f"❌ Error creating admin account: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
