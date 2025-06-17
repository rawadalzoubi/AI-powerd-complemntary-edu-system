import mysql.connector
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_sample_documents():
    """Add sample documents to the database for testing."""
    # Load environment variables
    load_dotenv()
    
    # Get database configuration
    config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE", "homework_helper")
    }
    
    # Sample documents
    sample_documents = [
        {
            "file_name": "sample1.txt",
            "content": """
            Artificial Intelligence (AI) is a broad field of computer science focused on creating intelligent machines that can perform tasks that typically require human intelligence. 
            These tasks include learning, reasoning, problem-solving, perception, and language understanding.
            
            Machine Learning is a subset of AI that focuses on developing systems that can learn from and make decisions based on data. 
            It uses algorithms to build mathematical models based on sample data, known as training data, to make predictions or decisions without being explicitly programmed to do so.
            
            Deep Learning is a subset of machine learning that uses neural networks with many layers (hence "deep") to analyze various factors of data. 
            It's particularly effective for tasks like image recognition, natural language processing, and speech recognition.
            """
        },
        {
            "file_name": "sample2.txt",
            "content": """
            Python is a high-level, interpreted programming language known for its simplicity and readability. 
            It was created by Guido van Rossum and first released in 1991.
            
            Key features of Python include:
            1. Easy to learn and use
            2. Extensive standard library
            3. Cross-platform compatibility
            4. Strong community support
            5. Great for data science and machine learning
            
            Python is widely used in various fields such as:
            - Web development
            - Data analysis
            - Artificial Intelligence
            - Scientific computing
            - Automation
            """
        },
        {
            "file_name": "sample3.txt",
            "content": """
            Database Management Systems (DBMS) are software systems that manage databases. 
            They provide an interface for users to interact with the database and ensure data integrity and security.
            
            MySQL is one of the most popular open-source relational database management systems. 
            It's known for its reliability, performance, and ease of use.
            
            Key features of MySQL include:
            1. ACID compliance
            2. High performance
            3. Scalability
            4. Security features
            5. Cross-platform support
            
            Common uses of MySQL:
            - Web applications
            - Data warehousing
            - E-commerce
            - Logging applications
            """
        }
    ]
    
    try:
        # Connect to database
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Insert sample documents
        for doc in sample_documents:
            cursor.execute("""
                INSERT INTO documents (file_name, content)
                VALUES (%s, %s)
            """, (doc["file_name"], doc["content"].encode()))
        
        # Commit changes
        conn.commit()
        logger.info(f"Added {len(sample_documents)} sample documents to the database")
        
    except mysql.connector.Error as e:
        logger.error(f"Error adding sample documents: {str(e)}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    add_sample_documents() 