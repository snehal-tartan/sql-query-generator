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
    
    # Try to get MYSQL_PUBLIC_URL from environment (for Railway - highest priority)
    mysql_public_url = os.getenv("MYSQL_PUBLIC_URL")
    if mysql_public_url:
        # Convert mysql:// to mysql+mysqlconnector:// for SQLAlchemy
        if mysql_public_url.startswith("mysql://"):
            mysql_public_url = mysql_public_url.replace("mysql://", "mysql+mysqlconnector://")
        
        DATABASE_URL = mysql_public_url
        engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
        return True
    
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
    env_port = os.getenv("MYSQL_PORT", "41854")
    
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
    
    return engine

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


def get_schema():
    """Retrieves comprehensive database schema information including relationships"""
    if engine is None:
        return {}
    
    try:
        # Query 1: Get table and column information
        columns_query = """
        SELECT 
            c.table_name,
            c.column_name,
            c.data_type,
            c.column_type,
            c.is_nullable,
            c.column_key,
            c.column_default,
            c.extra,
            c.column_comment
        FROM information_schema.columns c
        WHERE c.table_schema = :database
        ORDER BY c.table_name, c.ordinal_position
        """
        
        # Query 2: Get foreign key relationships
        fk_query = """
        SELECT 
            kcu.table_name,
            kcu.column_name,
            kcu.referenced_table_name,
            kcu.referenced_column_name,
            kcu.constraint_name
        FROM information_schema.key_column_usage kcu
        WHERE kcu.table_schema = :database
          AND kcu.referenced_table_name IS NOT NULL
        ORDER BY kcu.table_name, kcu.column_name
        """
        
        # Query 3: Get table comments/descriptions
        table_query = """
        SELECT 
            table_name,
            table_comment,
            table_rows,
            create_time
        FROM information_schema.tables
        WHERE table_schema = :database
          AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """
        
        # Query 4: Get indexes
        index_query = """
        SELECT 
            table_name,
            index_name,
            column_name,
            non_unique,
            seq_in_index
        FROM information_schema.statistics
        WHERE table_schema = :database
          AND index_name != 'PRIMARY'
        ORDER BY table_name, index_name, seq_in_index
        """

        with engine.connect() as connection:
            # Fetch all data
            columns_result = connection.execute(text(columns_query), {"database": MYSQL_DATABASE}).fetchall()
            fk_result = connection.execute(text(fk_query), {"database": MYSQL_DATABASE}).fetchall()
            table_result = connection.execute(text(table_query), {"database": MYSQL_DATABASE}).fetchall()
            index_result = connection.execute(text(index_query), {"database": MYSQL_DATABASE}).fetchall()
            
            # Build schema dictionary
            schema_dict = {
                'tables': {},
                'relationships': [],
                'table_metadata': {},
                'indexes': {}
            }
            
            # Process table metadata
            for table_name, comment, rows, created in table_result:
                schema_dict['table_metadata'][table_name] = {
                    'comment': comment or '',
                    'estimated_rows': rows or 0,
                    'created': str(created) if created else ''
                }
            
            # Process columns
            for table, column, dtype, col_type, nullable, key, default, extra, comment in columns_result:
                if table not in schema_dict['tables']:
                    schema_dict['tables'][table] = {
                        'columns': [],
                        'primary_keys': [],
                        'foreign_keys': []
                    }
                
                col_info = {
                    'name': column,
                    'type': col_type,  # Full type like VARCHAR(255) or ENUM(...)
                    'base_type': dtype,
                    'nullable': nullable == 'YES',
                    'default': default,
                    'extra': extra,  # auto_increment, etc.
                    'comment': comment or '',
                    'is_primary': key == 'PRI',
                    'is_unique': key == 'UNI',
                    'is_indexed': key == 'MUL'
                }
                
                schema_dict['tables'][table]['columns'].append(col_info)
                
                if key == 'PRI':
                    schema_dict['tables'][table]['primary_keys'].append(column)
            
            # Process foreign keys
            for table, column, ref_table, ref_column, constraint in fk_result:
                fk_info = {
                    'table': table,
                    'column': column,
                    'references_table': ref_table,
                    'references_column': ref_column,
                    'constraint_name': constraint
                }
                
                schema_dict['relationships'].append(fk_info)
                
                if table in schema_dict['tables']:
                    schema_dict['tables'][table]['foreign_keys'].append({
                        'column': column,
                        'references': f"{ref_table}.{ref_column}"
                    })
            
            # Process indexes
            for table, idx_name, column, non_unique, seq in index_result:
                if table not in schema_dict['indexes']:
                    schema_dict['indexes'][table] = {}
                
                if idx_name not in schema_dict['indexes'][table]:
                    schema_dict['indexes'][table][idx_name] = {
                        'columns': [],
                        'unique': non_unique == 0
                    }
                
                schema_dict['indexes'][table][idx_name]['columns'].append(column)
            
            # Print the schema_dict for debugging
            import json
            print("\n" + "="*80)
            print("SCHEMA_DICT OUTPUT:")
            print("="*80)
            print(json.dumps(schema_dict, indent=2, default=str))
            print("="*80 + "\n")
        
        return schema_dict
        
    except Exception as e:
        print(f"Error fetching schema: {e}")
        return {}

def format_schema_for_llm(schema_dict):
    """Converts schema dict to LLM-friendly markdown format"""
    if not schema_dict or 'tables' not in schema_dict:
        return "No schema available."
    
    output = ["# DATABASE SCHEMA\n"]
    
    # 1. Quick Relationship Overview (Most Important!)
    output.append("## TABLE RELATIONSHIPS\n")
    for rel in schema_dict.get('relationships', []):
        output.append(
            f"- `{rel['table']}.{rel['column']}` → "
            f"`{rel['references_table']}.{rel['references_column']}`"
        )
    output.append("\n---\n")
    
    # 2. Detailed Table Definitions
    for table_name, table_info in sorted(schema_dict['tables'].items()):
        output.append(f"\n## TABLE: `{table_name}`\n")
        
        # Metadata
        meta = schema_dict['table_metadata'].get(table_name, {})
        if meta.get('comment'):
            output.append(f"**Purpose:** {meta['comment']}\n")
        
        # Primary Key
        if table_info['primary_keys']:
            output.append(f"**Primary Key:** `{', '.join(table_info['primary_keys'])}`\n")
        
        # Foreign Keys
        if table_info['foreign_keys']:
            output.append("**Foreign Keys:**\n")
            for fk in table_info['foreign_keys']:
                output.append(f"  - `{fk['column']}` → `{fk['references']}`\n")
        
        # Columns
        output.append("\n**Columns:**\n")
        for col in table_info['columns']:
            # Build column definition
            col_def = f"- `{col['name']}` **{col['type']}**"
            
            # Add constraints
            tags = []
            if col['is_primary']:
                tags.append("PK")
            if not col['nullable']:
                tags.append("NOT NULL")
            if col['extra'] == 'auto_increment':
                tags.append("AUTO_INCREMENT")
            if col['is_unique']:
                tags.append("UNIQUE")
            
            if tags:
                col_def += f" `[{', '.join(tags)}]`"
            
            # Add comment if exists
            if col['comment']:
                col_def += f"  \n  *{col['comment']}*"
            
            output.append(col_def + "\n")
    
    return "".join(output)