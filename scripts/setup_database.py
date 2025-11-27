"""Setup database tables."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage import db
from src.utils import logger

if __name__ == "__main__":
    logger.info("Setting up database tables...")
    try:
        db.create_tables()
        logger.info("✓ Database tables created successfully")
    except Exception as e:
        logger.error(f"✗ Database setup failed: {e}", exc_info=True)
        sys.exit(1)


