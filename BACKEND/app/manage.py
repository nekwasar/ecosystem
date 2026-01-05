import argparse
import getpass
import sys
import os

# Add current directory to path to allow imports when running as a script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database import SessionLocal
    from models.user import AdminUser
    from auth import get_password_hash
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Ensure you are running this from the app directory or the project root with the correct python path.")
    sys.exit(1)

def create_admin(username, email, superuser=True):
    """Create a new admin user with secure password input"""
    db = SessionLocal()
    try:
        # Check if user exists
        existing = db.query(AdminUser).filter((AdminUser.username == username) | (AdminUser.email == email)).first()
        if existing:
            print(f"❌ Error: User with username '{username}' or email '{email}' already exists.")
            return

        password = getpass.getpass(f"Enter New Password for {username}: ")
        if not password:
            print("❌ Error: Password cannot be empty.")
            return
            
        confirm = getpass.getpass("Confirm Password: ")
        
        if password != confirm:
            print("❌ Error: Passwords do not match.")
            return

        hashed = get_password_hash(password)
        new_admin = AdminUser(
            username=username,
            email=email,
            hashed_password=hashed,
            is_active=True,
            is_superuser=superuser
        )
        db.add(new_admin)
        db.commit()
        print(f"✅ Success: Admin user '{username}' (Superuser: {superuser}) created successfully!")
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

def reset_password(username):
    """Reset the password for an existing admin user"""
    db = SessionLocal()
    try:
        user = db.query(AdminUser).filter(AdminUser.username == username).first()
        if not user:
            print(f"❌ Error: User '{username}' not found.")
            return

        password = getpass.getpass(f"Enter New Password for {username}: ")
        if not password:
            print("❌ Error: Password cannot be empty.")
            return
            
        confirm = getpass.getpass("Confirm Password: ")
        
        if password != confirm:
            print("❌ Error: Passwords do not match.")
            return

        user.hashed_password = get_password_hash(password)
        db.commit()
        print(f"✅ Success: Password for '{username}' has been reset.")
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

def list_users():
    """List all admin users"""
    db = SessionLocal()
    try:
        users = db.query(AdminUser).all()
        print(f"\n{'ID':<5} | {'Username':<20} | {'Email':<30} | {'Superuser':<10} | {'Status':<10}")
        print("-" * 85)
        for u in users:
            status = "Active" if u.is_active else "Inactive"
            print(f"{u.id:<5} | {u.username:<20} | {u.email:<30} | {str(u.is_superuser):<10} | {status:<10}")
        print("\n")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🚀 NekwasaR Admin Management Terminal Tool")
    subparsers = parser.add_subparsers(dest="command", help="Manage admin users securely")

    # Command: create-admin
    create_parser = subparsers.add_parser("create-admin", help="Create a new admin user")
    create_parser.add_argument("--username", required=True, help="Username for the new admin")
    create_parser.add_argument("--email", required=True, help="Email address")
    create_parser.add_argument("--no-super", action="store_false", dest="superuser", help="Create as a standard admin (not superuser)")

    # Command: reset-password
    reset_parser = subparsers.add_parser("reset-password", help="Force reset an admin's password")
    reset_parser.add_argument("--username", required=True, help="Username of the admin")

    # Command: list
    subparsers.add_parser("list", help="List all registered admin users")

    args = parser.parse_args()

    if args.command == "create-admin":
        create_admin(args.username, args.email, getattr(args, 'superuser', True))
    elif args.command == "reset-password":
        reset_password(args.username)
    elif args.command == "list":
        list_users()
    else:
        parser.print_help()
