import mysql.connector
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    """Set up the MySQL database and create necessary tables."""
    # Load environment variables
    load_dotenv()
    
    # Get database configuration
    config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE", "homework_helper")
    }
    
    # Validate configuration
    if not all([config["user"], config["password"]]):
        raise ValueError("MySQL user and password must be provided in environment variables")
    
    try:
        # Connect to MySQL server (without database)
        conn = mysql.connector.connect(
            host=config["host"],
            user=config["user"],
            password=config["password"]
        )
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config['database']}")
        logger.info(f"Database '{config['database']}' created or already exists")
        
        # Switch to the database
        cursor.execute(f"USE {config['database']}")
        
        # Create documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_name VARCHAR(255) NOT NULL,
                content LONGBLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        logger.info("Documents table created or already exists")
        
        # Commit changes and close connection
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Database setup completed successfully")
        
    except mysql.connector.Error as e:
        logger.error(f"Error setting up database: {str(e)}")
        raise

if __name__ == "__main__":
    setup_database() 