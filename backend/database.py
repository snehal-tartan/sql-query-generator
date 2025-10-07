import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Global variables for database connection
engine = None
MYSQL_HOST = None
MYSQL_USER = None
MYSQL_PASSWORD = None
MYSQL_DATABASE = None
MYSQL_PORT = None
DATABASE_URL = None

def load_from_env():
    """Load database connection from environment variables"""
    global engine, DATABASE_URL, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_PORT
    
    # Try to get MYSQL_URL from environment (for production)
    mysql_url = os.getenv("MYSQL_URL")
    if mysql_url:
        # Convert mysql:// to mysql+mysqlconnector:// for SQLAlchemy
        if mysql_url.startswith("mysql://"):
            mysql_url = mysql_url.replace("mysql://", "mysql+mysqlconnector://")
        
        DATABASE_URL = mysql_url
        engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
        return True
    
    # Try to get individual environment variables (for local development)
    env_host = os.getenv("MYSQL_HOST")
    env_user = os.getenv("MYSQL_USER")
    env_password = os.getenv("MYSQL_PASSWORD")
    env_database = os.getenv("MYSQL_DATABASE")
    env_port = os.getenv("MYSQL_PORT", "3306")
    
    if all([env_host, env_user, env_password, env_database]):
        MYSQL_HOST = env_host
        MYSQL_USER = env_user
        MYSQL_PASSWORD = env_password
        MYSQL_DATABASE = env_database
        MYSQL_PORT = int(env_port)
        
        DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{quote_plus(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
        return True
    
    return False

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
    # Try to load from environment variables if not already connected
    if engine is None:
        load_from_env()
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


