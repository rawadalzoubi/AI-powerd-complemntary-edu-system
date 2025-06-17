import mysql.connector  # type: ignore
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class MySQLLoader:
    """Loads documents from MySQL database."""

    def __init__(self, config: Dict[str, str]):
        """
        Initialize the MySQL loader.

        Args:
            config: Dictionary containing MySQL connection parameters
                   (host, user, password, database)
        """
        self.config = config
        self.connection = None
        self._connect()

    def _connect(self):
        """Establish connection to MySQL database."""
        try:
            self.connection = mysql.connector.connect(**self.config)
            logger.info("Connected to MySQL database")
        except mysql.connector.Error as e:
            logger.error(f"Error connecting to MySQL: {str(e)}")
            raise

    def process(self, data: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Process method required by the pipeline.
        Loads documents from MySQL database.

        Args:
            data: Optional input data (not used in this loader)

        Returns:
            List of documents with their content and metadata
        """
        return self.load_documents()

    def load_documents(self) -> List[Dict[str, Any]]:
        """
        Load documents from the MySQL database.

        Returns:
            List of documents with their content and metadata
        """
        if not self.connection:
            self._connect()

        try:
            cursor = self.connection.cursor(dictionary=True)

            # Query to get documents
            query = """
    SELECT id, title, content_type, created_at, updated_at, file  # <-- أضف اسم عمود الملف هنا
    FROM eduapi_lessoncontent
    WHERE content_type = 'PDF' AND file IS NOT NULL -- قد ترغب في فلترة ملفات PDF فقط إذا كان PDFParser مخصصًا لها
"""

            cursor.execute(query)
            eduapi_lessoncontent = cursor.fetchall()

            cursor.close()

            logger.info(
                f"Loaded {len(eduapi_lessoncontent)} documents from MySQL")
            return eduapi_lessoncontent

        except mysql.connector.Error as e:
            logger.error(f"Error loading documents from MySQL: {str(e)}")
            raise
        finally:
            if cursor:
                cursor.close()

