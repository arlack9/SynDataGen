"""
SQL Server Schema Extractor for Online Mode Schema Integration
Connects to SQL Server and extracts table schemas for data generation.
"""

import pypyodbc as pyodbc  # Using pypyodbc for better installation compatibility
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ColumnInfo:
    """Information about a database column."""
    name: str
    data_type: str
    max_length: Optional[int]
    is_nullable: bool
    default_value: Optional[str]
    is_primary_key: bool = False
    is_foreign_key: bool = False
    reference_table: Optional[str] = None

@dataclass
class TableInfo:
    """Information about a database table."""
    name: str
    schema: str
    columns: List[ColumnInfo]
    row_count: Optional[int] = None

class SQLServerSchemaExtractor:
    """Extract schema information from SQL Server database."""
    
    def __init__(self, connection_string: str = None, **kwargs):
        """
        Initialize the schema extractor.
        
        Args:
            connection_string: Full ODBC connection string
            **kwargs: Individual connection parameters (server, database, username, password, etc.)
        """
        self.connection_string = connection_string
        if not connection_string and kwargs:
            self.connection_string = self._build_connection_string(**kwargs)
        
        self.connection = None
    
    def _build_connection_string(self, server: str, database: str, 
                               username: str = None, password: str = None,
                               trusted_connection: bool = True, 
                               driver: str = "ODBC Driver 17 for SQL Server") -> str:
        """Build ODBC connection string from parameters."""
        
        # Ensure server and database are not None
        if not server or not database:
            raise ValueError("Server and database are required")
        
        # Clean the parameters
        server = str(server).strip() if server else ""
        database = str(database).strip() if database else ""
        
        if not server or not database:
            raise ValueError("Server and database cannot be empty")
        
        if trusted_connection:
            # Windows Authentication
            conn_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"Trusted_Connection=yes;"
            )
        else:
            # SQL Server Authentication
            username = str(username).strip() if username else ""
            password = str(password).strip() if password else ""
            
            if not username or not password:
                raise ValueError("Username and password required for SQL Server authentication")
            
            conn_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
            )
        
        return conn_str
    
    def connect(self) -> bool:
        """Establish connection to SQL Server."""
        try:
            logger.info("Attempting to connect to SQL Server...")
            self.connection = pyodbc.connect(self.connection_string)
            logger.info("Successfully connected to SQL Server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SQL Server: {e}")
            return False
    
    def disconnect(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Disconnected from SQL Server")
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test the database connection."""
        try:
            if self.connect():
                cursor = self.connection.cursor()
                cursor.execute("SELECT @@VERSION")
                version = cursor.fetchone()[0]
                cursor.close()
                self.disconnect()
                return True, f"Connection successful. SQL Server version: {version[:100]}..."
            else:
                return False, "Failed to establish connection"
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
    
    def get_tables(self, schema_name: str = None) -> List[str]:
        """Get list of tables in the database."""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            
            if schema_name:
                query = """
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA = ?
                ORDER BY TABLE_NAME
                """
                cursor.execute(query, (schema_name,))
            else:
                query = """
                SELECT TABLE_SCHEMA + '.' + TABLE_NAME as FULL_NAME
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_SCHEMA, TABLE_NAME
                """
                cursor.execute(query)
            
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            
            logger.info(f"Found {len(tables)} tables")
            return tables
            
        except Exception as e:
            logger.error(f"Error getting tables: {e}")
            return []
    
    def get_table_schema(self, table_name: str, schema_name: str = 'dbo') -> Optional[TableInfo]:
        """Get detailed schema information for a specific table."""
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            cursor = self.connection.cursor()
            
            # Get column information
            column_query = """
            SELECT 
                c.COLUMN_NAME,
                c.DATA_TYPE,
                c.CHARACTER_MAXIMUM_LENGTH,
                c.IS_NULLABLE,
                c.COLUMN_DEFAULT,
                CASE WHEN pk.COLUMN_NAME IS NOT NULL THEN 1 ELSE 0 END as IS_PRIMARY_KEY
            FROM INFORMATION_SCHEMA.COLUMNS c
            LEFT JOIN (
                SELECT ku.TABLE_SCHEMA, ku.TABLE_NAME, ku.COLUMN_NAME
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS tc
                INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS ku
                    ON tc.CONSTRAINT_TYPE = 'PRIMARY KEY' 
                    AND tc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
            ) pk ON c.TABLE_SCHEMA = pk.TABLE_SCHEMA 
                AND c.TABLE_NAME = pk.TABLE_NAME 
                AND c.COLUMN_NAME = pk.COLUMN_NAME
            WHERE c.TABLE_NAME = ? AND c.TABLE_SCHEMA = ?
            ORDER BY c.ORDINAL_POSITION
            """
            
            cursor.execute(column_query, (table_name, schema_name))
            column_rows = cursor.fetchall()
            
            if not column_rows:
                cursor.close()
                return None
            
            # Build column info list
            columns = []
            for row in column_rows:
                col_info = ColumnInfo(
                    name=row[0],
                    data_type=row[1],
                    max_length=row[2],
                    is_nullable=(row[3] == 'YES'),
                    default_value=row[4],
                    is_primary_key=(row[5] == 1)
                )
                columns.append(col_info)
            
            # Get row count (optional, can be slow for large tables)
            try:
                count_query = f"SELECT COUNT(*) FROM [{schema_name}].[{table_name}]"
                cursor.execute(count_query)
                row_count = cursor.fetchone()[0]
            except:
                row_count = None
            
            cursor.close()
            
            table_info = TableInfo(
                name=table_name,
                schema=schema_name,
                columns=columns,
                row_count=row_count
            )
            
            logger.info(f"Retrieved schema for {schema_name}.{table_name} with {len(columns)} columns")
            return table_info
            
        except Exception as e:
            logger.error(f"Error getting table schema: {e}")
            return None
    
    def get_multiple_table_schemas(self, table_names: List[str], schema_name: str = 'dbo') -> Dict[str, TableInfo]:
        """Get schema information for multiple tables."""
        schemas = {}
        
        for table_name in table_names:
            # Handle fully qualified names
            if '.' in table_name:
                parts = table_name.split('.')
                schema = parts[0]
                table = parts[1]
            else:
                schema = schema_name
                table = table_name
            
            table_info = self.get_table_schema(table, schema)
            if table_info:
                schemas[f"{schema}.{table}"] = table_info
        
        return schemas
    
    def generate_schema_context(self, table_names: List[str], schema_name: str = 'dbo', 
                              include_sample_data: bool = False) -> str:
        """
        Generate a schema context string for LLM prompts.
        
        Args:
            table_names: List of table names to include
            schema_name: Database schema name
            include_sample_data: Whether to include sample data (can be slow)
        
        Returns:
            Formatted schema description for LLM context
        """
        schemas = self.get_multiple_table_schemas(table_names, schema_name)
        
        if not schemas:
            return "No valid table schemas found."
        
        context_parts = [
            "=== DATABASE SCHEMA INFORMATION ===",
            f"Database contains {len(schemas)} table(s):",
            ""
        ]
        
        for table_name, table_info in schemas.items():
            context_parts.append(f"TABLE: {table_name}")
            if table_info.row_count is not None:
                context_parts.append(f"  Rows: {table_info.row_count:,}")
            
            context_parts.append("  Columns:")
            
            for col in table_info.columns:
                col_desc = f"    - {col.name}: {col.data_type}"
                
                if col.max_length:
                    col_desc += f"({col.max_length})"
                
                if col.is_primary_key:
                    col_desc += " [PRIMARY KEY]"
                
                if not col.is_nullable:
                    col_desc += " [NOT NULL]"
                
                if col.default_value:
                    col_desc += f" [DEFAULT: {col.default_value}]"
                
                context_parts.append(col_desc)
            
            # Add sample data if requested
            if include_sample_data and self.connection:
                try:
                    cursor = self.connection.cursor()
                    sample_query = f"SELECT TOP 2 * FROM [{table_info.schema}].[{table_info.name}]"
                    cursor.execute(sample_query)
                    
                    # Get column names
                    columns = [description[0] for description in cursor.description]
                    
                    # Get sample rows
                    rows = cursor.fetchall()
                    cursor.close()
                    
                    if rows:
                        context_parts.append("  Sample Data:")
                        context_parts.append(f"    {' | '.join(columns)}")
                        context_parts.append("    " + "-" * (len(' | '.join(columns))))
                        
                        for row in rows:
                            row_str = ' | '.join([str(val) if val is not None else 'NULL' for val in row])
                            context_parts.append(f"    {row_str}")
                
                except Exception as e:
                    context_parts.append(f"    Sample data unavailable: {e}")
            
            context_parts.append("")
        
        context_parts.extend([
            "=== INSTRUCTIONS ===",
            "Generate synthetic data that matches the above schema structure.",
            "Ensure data types, constraints, and relationships are respected.",
            "Use realistic values appropriate for each column type and name.",
            ""
        ])
        
        return "\n".join(context_parts)

def create_extractor_from_params(server: str, database: str, 
                                username: str = None, password: str = None,
                                use_windows_auth: bool = True) -> SQLServerSchemaExtractor:
    """Convenience function to create schema extractor from individual parameters."""
    
    return SQLServerSchemaExtractor(
        server=server,
        database=database,
        username=username,
        password=password,
        trusted_connection=use_windows_auth
    )

# Example usage and testing functions
def test_connection_params(server: str, database: str, 
                          username: str = None, password: str = None,
                          use_windows_auth: bool = True) -> Tuple[bool, str]:
    """Test database connection with given parameters."""
    try:
        # Validate and clean parameters
        if not server or not database:
            return False, "Server and database are required"
        
        server = str(server).strip() if server else ""
        database = str(database).strip() if database else ""
        
        if not server or not database:
            return False, "Server and database cannot be empty"
        
        # Clean username and password
        if username is not None:
            username = str(username).strip()
            if not username:
                username = None
        
        if password is not None:
            password = str(password).strip()
            if not password:
                password = None
        
        extractor = create_extractor_from_params(
            server=server,
            database=database,
            username=username,
            password=password,
            use_windows_auth=use_windows_auth
        )
        
        return extractor.test_connection()
        
    except Exception as e:
        return False, f"Connection setup failed: {str(e)}"

if __name__ == "__main__":
    # Example usage
    print("SQL Server Schema Extractor")
    print("This module can be used to extract schema information from SQL Server databases.")
    print("Use create_extractor_from_params() to create an extractor instance.")
