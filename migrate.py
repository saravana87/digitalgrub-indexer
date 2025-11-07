"""
Database Migration Manager
Run migrations easily with: python migrate.py
"""
import sys
from pathlib import Path
from alembic import command
from alembic.config import Config
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_alembic_config():
    """Get Alembic configuration"""
    # Get the directory containing this script
    base_dir = Path(__file__).resolve().parent
    alembic_ini = base_dir / "alembic.ini"
    
    if not alembic_ini.exists():
        raise FileNotFoundError(f"alembic.ini not found at {alembic_ini}")
    
    config = Config(str(alembic_ini))
    return config


def run_migrations():
    """Run all pending migrations"""
    try:
        logger.info("Running database migrations...")
        config = get_alembic_config()
        command.upgrade(config, "head")
        logger.info("✓ Migrations completed successfully!")
        return True
    except SystemExit as e:
        # Alembic calls sys.exit(0) on success
        if e.code == 0:
            logger.info("✓ Migrations completed successfully!")
            return True
        else:
            logger.error(f"✗ Migration failed with exit code: {e.code}")
            return False
    except Exception as e:
        logger.error(f"✗ Migration failed: {str(e)}")
        return False


def show_current_revision():
    """Show current database revision"""
    try:
        config = get_alembic_config()
        command.current(config, verbose=True)
    except Exception as e:
        logger.error(f"Error: {str(e)}")


def show_migration_history():
    """Show migration history"""
    try:
        config = get_alembic_config()
        command.history(config, verbose=True)
    except Exception as e:
        logger.error(f"Error: {str(e)}")


def downgrade_one():
    """Downgrade one revision"""
    try:
        logger.info("Downgrading one revision...")
        config = get_alembic_config()
        command.downgrade(config, "-1")
        logger.info("✓ Downgrade completed!")
    except Exception as e:
        logger.error(f"✗ Downgrade failed: {str(e)}")


def create_migration(message: str):
    """Create a new migration"""
    try:
        logger.info(f"Creating new migration: {message}")
        config = get_alembic_config()
        command.revision(config, message=message, autogenerate=True)
        logger.info("✓ Migration file created!")
    except Exception as e:
        logger.error(f"✗ Failed to create migration: {str(e)}")


def show_help():
    """Show help message"""
    help_text = """
Database Migration Manager for DigitalGrub Indexer
================================================

Usage:
    python migrate.py [command]

Commands:
    upgrade         Run all pending migrations (default)
    current         Show current database revision
    history         Show migration history
    downgrade       Downgrade one revision
    create <msg>    Create a new migration with autogenerate
    help            Show this help message

Examples:
    python migrate.py                           # Run migrations
    python migrate.py upgrade                   # Run migrations
    python migrate.py current                   # Show current revision
    python migrate.py history                   # Show history
    python migrate.py create "add user table"   # Create new migration
    """
    print(help_text)


def main():
    """Main entry point"""
    if len(sys.argv) == 1 or sys.argv[1] == "upgrade":
        # Default action: run migrations
        run_migrations()
    
    elif sys.argv[1] == "current":
        show_current_revision()
    
    elif sys.argv[1] == "history":
        show_migration_history()
    
    elif sys.argv[1] == "downgrade":
        downgrade_one()
    
    elif sys.argv[1] == "create":
        if len(sys.argv) < 3:
            logger.error("Please provide a migration message")
            logger.info("Usage: python migrate.py create \"your message here\"")
            sys.exit(1)
        message = " ".join(sys.argv[2:])
        create_migration(message)
    
    elif sys.argv[1] in ["help", "-h", "--help"]:
        show_help()
    
    else:
        logger.error(f"Unknown command: {sys.argv[1]}")
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
