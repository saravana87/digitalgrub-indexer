"""
Setup Database - Install PgVector extension and run migrations
Run this once after setting up your PostgreSQL database
"""
import psycopg2
from config import settings
import logging
from migrate import run_migrations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def install_pgvector():
    """Install PgVector extension in PostgreSQL"""
    try:
        logger.info("Connecting to PostgreSQL...")
        conn = psycopg2.connect(
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        logger.info("Installing PgVector extension...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        logger.info("✓ PgVector extension installed successfully!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to install PgVector: {str(e)}")
        logger.info("\nPlease ensure:")
        logger.info("1. PostgreSQL server is running")
        logger.info("2. PgVector is installed on your PostgreSQL server")
        logger.info("3. Your database credentials in .env are correct")
        logger.info("4. You have superuser privileges to install extensions")
        return False


def main():
    """Main setup process"""
    print("=" * 60)
    print("DigitalGrub Indexer - Database Setup")
    print("=" * 60)
    print()
    
    # Step 1: Install PgVector
    print("Step 1: Installing PgVector Extension")
    print("-" * 60)
    if not install_pgvector():
        print("\n⚠️  PgVector installation failed!")
        print("You may need to install it manually:")
        print("SQL> CREATE EXTENSION IF NOT EXISTS vector;")
        
        response = input("\nContinue with migrations anyway? (yes/no): ")
        if response.lower() != 'yes':
            print("Setup cancelled.")
            return
    
    print()
    
    # Step 2: Run migrations
    print("Step 2: Running Database Migrations")
    print("-" * 60)
    
    try:
        run_migrations()
        print()
        print("=" * 60)
        print("✓ Database setup completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Run: python example_index.py     # Index your data")
        print("2. Run: python example_query.py     # Generate content")
    except SystemExit as e:
        if e.code == 0:
            print()
            print("=" * 60)
            print("✓ Database setup completed successfully!")
            print("=" * 60)
            print()
            print("Next steps:")
            print("1. Run: python example_index.py     # Index your data")
            print("2. Run: python example_query.py     # Generate content")
        else:
            print()
            print("=" * 60)
            print("✗ Setup failed during migrations")
            print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ Setup failed: {str(e)}")
        print("=" * 60)


if __name__ == "__main__":
    main()
