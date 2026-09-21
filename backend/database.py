import mysql.connector
from mysql.connector import Error
import logging

# Configure logger
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, host="localhost", user="triage_app", password=None, database="SOCTriage"):
        if password is None:
            raise ValueError("Configuration Error: Database password must be explicitly provided via environment variables.")
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "raise_on_warnings": True
        }

    def get_connection(self):
        """Establish and return a database connection using least-privilege credentials."""
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def extract_triage_batch(self, limit=50):
        """
        Step 2: Database Extraction (The Perception Layer).
        Retrieves a batch of network connection logs from the 3NF database schema.
        """
        connection = None
        cursor = None
        logs = []
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Extract a batch of raw logs for triage processing
            query = """
                SELECT UID, Timestamp, Source_IP, Source_Port, Dest_IP, Dest_Port, Protocol, Conn_State, Service_Name
                FROM Network_Connections
                LIMIT %s;
            """
            cursor.execute(query, (limit,))
            logs = cursor.fetchall()
            logger.info(f"Successfully extracted {len(logs)} network connection records for evaluation.")
            
        except Error as e:
            logger.error(f"Failed to query network connection logs: {e}")
            # Raise exception so the calling pipeline can decide to trigger a fallback/mock
            raise
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
                logger.info("Database connection closed gracefully.")
                
        return logs
