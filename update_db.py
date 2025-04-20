from app import app, db
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_database():
    try:
        # Drop all tables and recreate them
        with app.app_context():
            logger.info("Dropping all tables...")
            db.drop_all()
            
            logger.info("Creating all tables...")
            db.create_all()
            
            logger.info("Database schema updated successfully!")
            
            # Re-create admin user after database reset
            from routes import create_admin_user
            create_admin_user()
            logger.info("Admin user recreated successfully!")
            
    except Exception as e:
        logger.error(f"Error updating database: {e}")
        raise

if __name__ == "__main__":
    update_database()