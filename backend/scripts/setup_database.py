"""Run database migrations and seed data."""
import asyncio
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and print output."""
    print(f"\n{'='*60}")
    print(f"📌 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(e.stdout)
        print(e.stderr)
        return False


def main():
    """Main setup function."""
    print("\n" + "="*60)
    print("🚀 KARIGAR DATABASE SETUP")
    print("="*60)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)
    
    print(f"\n📂 Working directory: {os.getcwd()}")
    
    # Step 1: Create migration
    print("\n" + "="*60)
    print("STEP 1: Creating database migration")
    print("="*60)
    
    if not run_command(
        "alembic revision --autogenerate -m \"Initial schema with all models\"",
        "Generate migration"
    ):
        print("\n⚠️  Migration generation failed. This might be okay if migrations already exist.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Step 2: Run migration
    print("\n" + "="*60)
    print("STEP 2: Running database migration")
    print("="*60)
    
    if not run_command(
        "alembic upgrade head",
        "Apply migrations"
    ):
        print("\n❌ Migration failed. Please check your database connection and try again.")
        return
    
    # Step 3: Seed data
    print("\n" + "="*60)
    print("STEP 3: Seeding database with demo data")
    print("="*60)
    
    response = input("\nDo you want to seed the database with demo data? (y/n): ")
    if response.lower() == 'y':
        if not run_command(
            f"{sys.executable} scripts/seed_data.py",
            "Seed database"
        ):
            print("\n❌ Seeding failed. Database schema is created but no demo data was added.")
            return
    
    print("\n" + "="*60)
    print("✅ DATABASE SETUP COMPLETE!")
    print("="*60)
    print("\n📝 Next steps:")
    print("   1. Start Redis: redis-server")
    print("   2. Start backend: uvicorn app.main:app --reload")
    print("   3. Access API docs: http://localhost:8000/docs")
    print("\n🔑 Test accounts (if seeded):")
    print("   Customer: customer@test.com / Test@123")
    print("   Provider: provider@test.com / Test@123")
    print("   Admin: admin@test.com / Admin@123")


if __name__ == "__main__":
    main()
