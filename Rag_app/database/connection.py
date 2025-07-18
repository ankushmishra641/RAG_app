import os
import pymysql
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import logging
from urllib.parse import quote_plus

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.host = os.getenv('MYSQL_HOST', 'localhost')
        self.port = int(os.getenv('MYSQL_PORT', 3306))
        self.user = os.getenv('MYSQL_USER')
        self.password = os.getenv('MYSQL_PASSWORD')
        self.database = os.getenv('MYSQL_DATABASE', 'school_db')
        self.engine = None
        self.connect()
    
    def connect(self):
        """Establish database connection with proper password encoding"""
        try:
            # URL-encode the password to handle special characters
            encoded_password = quote_plus(self.password) if self.password else ""
            encoded_user = quote_plus(self.user) if self.user else ""
            
            connection_string = f"mysql+pymysql://{encoded_user}:{encoded_password}@{self.host}:{self.port}/{self.database}"
            self.engine = create_engine(connection_string, echo=False)
            
            # Test the connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logging.info("Database connection established successfully")
            print("✅ Database connection successful!")
            
        except Exception as e:
            error_msg = f"Database connection failed: {e}"
            logging.error(error_msg)
            print(f"❌ {error_msg}")
            print("\n🔧 Please check:")
            print("1. MySQL server is running")
            print("2. Database credentials in .env file are correct")
            print("3. Database 'school_db' exists")
            print("4. User has proper permissions")
            raise
    
    def execute_query(self, query: str, params=None):
        """Execute SQL query safely"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), params or {})
                if result.returns_rows:
                    return pd.DataFrame(result.fetchall(), columns=result.keys())
                else:
                    return {"message": "Query executed successfully", "rowcount": result.rowcount}
        except SQLAlchemyError as e:
            logging.error(f"Query execution failed: {e}")
            raise
    
    def get_schema_info(self):
        """Get comprehensive database schema information"""
        schema_query = """
        SELECT 
            TABLE_NAME,
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            COLUMN_DEFAULT,
            COLUMN_KEY,
            EXTRA
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = :database_name
        ORDER BY TABLE_NAME, ORDINAL_POSITION
        """
        return self.execute_query(schema_query, {"database_name": self.database})
    
    def get_foreign_keys(self):
        """Get foreign key relationships"""
        fk_query = """
        SELECT 
            TABLE_NAME,
            COLUMN_NAME,
            CONSTRAINT_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = :database_name
        AND REFERENCED_TABLE_NAME IS NOT NULL
        """
        return self.execute_query(fk_query, {"database_name": self.database})
    
    def get_sample_data(self, table_name: str, limit: int = 5):
        """Get sample data from a table"""
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.execute_query(query)