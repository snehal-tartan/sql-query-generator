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

# Global variable to cache schema DDL
_cached_schema_ddl = None

def load_from_env():
    """Load database connection from environment variables"""
    global engine, DATABASE_URL, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_PORT
    
    # Try to get MYSQL_PUBLIC_URL from environment (for Railway - highest priority)
    mysql_public_url = os.getenv("MYSQL_PUBLIC_URL")
    if mysql_public_url:
        # Convert mysql:// to mysql+mysqlconnector:// for SQLAlchemy
        if mysql_public_url.startswith("mysql://"):
            mysql_public_url = mysql_public_url.replace("mysql://", "mysql+mysqlconnector://")
        
        DATABASE_URL = mysql_public_url
        engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
        _fetch_and_cache_schema()  # Cache schema after connection
        return True
    
    # Try to get MYSQL_URL from environment (for production)
    mysql_url = os.getenv("MYSQL_URL")
    if mysql_url:
        # Convert mysql:// to mysql+mysqlconnector:// for SQLAlchemy
        if mysql_url.startswith("mysql://"):
            mysql_url = mysql_url.replace("mysql://", "mysql+mysqlconnector://")
        
        DATABASE_URL = mysql_url
        engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
        _fetch_and_cache_schema()  # Cache schema after connection
        return True
    
    # Try to get individual environment variables (for local development)
    env_host = os.getenv("MYSQL_HOST")
    env_user = os.getenv("MYSQL_USER")
    env_password = os.getenv("MYSQL_PASSWORD")
    env_database = os.getenv("MYSQL_DATABASE")
    env_port = os.getenv("MYSQL_PORT", "41854")
    
    if all([env_host, env_user, env_password, env_database]):
        MYSQL_HOST = env_host
        MYSQL_USER = env_user
        MYSQL_PASSWORD = env_password
        MYSQL_DATABASE = env_database
        MYSQL_PORT = int(env_port)
        
        DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{quote_plus(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
        _fetch_and_cache_schema()  # Cache schema after connection
        return True
    
    return False

def set_database_credentials(host, user, password, database, port=41854):
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
    
    # Cache schema immediately after connection
    _fetch_and_cache_schema()
    
    return engine

def _fetch_and_cache_schema():
    """Fetch schema DDL from database and cache it (internal use only)"""
    global _cached_schema_ddl
    
    if engine is None:
        print("[WARNING] Cannot fetch schema: engine is None")
        return
    
    try:
        from langchain_community.utilities import SQLDatabase
        
        # Create LangChain SQLDatabase instance
        db = SQLDatabase(engine)
        
        # Fetch schema DDL
        _cached_schema_ddl = db.get_table_info()
        
        print(f"[INFO] Schema cached successfully ({len(_cached_schema_ddl)} characters)")
        print(f"[DEBUG] Schema preview: {_cached_schema_ddl[:200]}...")
        
    except Exception as e:
        print(f"[ERROR] Failed to cache schema: {e}")
        _cached_schema_ddl = None

def get_cached_schema():
    """Get the cached schema DDL"""
    global _cached_schema_ddl
    
    # If schema not cached yet, try to fetch it
    if _cached_schema_ddl is None:
        print("[INFO] Schema not cached, fetching now...")
        _fetch_and_cache_schema()
    
    return _cached_schema_ddl

def refresh_schema_cache():
    """Manually refresh the cached schema (call this after schema changes)"""
    global _cached_schema_ddl
    
    print("[INFO] Refreshing schema cache...")
    _cached_schema_ddl = None
    _fetch_and_cache_schema()
    
    return _cached_schema_ddl is not None

def get_engine():
    """Get the current database engine"""
    return engine

def is_connected():
    """Check if database is connected"""
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