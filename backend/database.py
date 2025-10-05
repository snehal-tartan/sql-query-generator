import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# Global variables for database connection
engine = None
MYSQL_HOST = None
MYSQL_USER = None
MYSQL_PASSWORD = None
MYSQL_DATABASE = None
MYSQL_PORT = None
DATABASE_URL = None

def set_database_credentials(host, user, password, database, port=3306):
    """Set database credentials and create engine"""
    global engine, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_PORT, DATABASE_URL
    
    MYSQL_HOST = host
    MYSQL_USER = user
    MYSQL_PASSWORD = password
    MYSQL_DATABASE = database
    MYSQL_PORT = port
    
    # Database URL with URL-encoded password
    DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{quote_plus(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    
    # Create the SQLAlchemy engine
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
    
    return engine

def get_engine():
    """Get the current database engine"""
    return engine

def is_connected():
    """Check if database is connected"""
    return engine is not None

def test_connection():
    """Test the database connection"""
    if engine is None:
        return False
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT DATABASE()"))
        return True
    except Exception:
        return False

def get_schema():
    """Retrieves database schema information"""
    if engine is None:
        return {}
    
    try:
        query = """
        SELECT table_name, column_name, data_type, is_nullable, column_key
        FROM information_schema.columns
        WHERE table_schema = :database
        ORDER BY table_name, ordinal_position
        """
        
        with engine.connect() as connection:
            result = connection.execute(text(query), {"database": MYSQL_DATABASE})
            schema_info = result.fetchall()
            
            schema_dict = {}
            for table, column, dtype, nullable, key in schema_info:
                if table not in schema_dict:
                    schema_dict[table] = []
                
                col_desc = f"{column} ({dtype})"
                if key == 'PRI':
                    col_desc += " [PRIMARY KEY]"
                elif key == 'UNI':
                    col_desc += " [UNIQUE]"
                elif key == 'MUL':
                    col_desc += " [INDEX]"
                
                if nullable == 'NO':
                    col_desc += " [NOT NULL]"
                
                schema_dict[table].append(col_desc)
        
        return schema_dict
        
    except Exception:
        return {}

def get_table_info(table_name):
    """Get detailed information about a specific table"""
    if engine is None:
        return []
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text(f"DESCRIBE {table_name}"))
            return result.fetchall()
    except Exception:
        return []


