import json
import pandas as pd
from io import StringIO
from typing import Dict, List, Tuple, Optional, Any
from .sql_schema_extractor import SQLServerSchemaExtractor, create_extractor_from_params, test_connection_params

class SchemaValidator:
    """Enhanced schema validator for uploaded files and SQL Server connections."""
    
    ALLOWED_EXTENSIONS = {'json', 'csv', 'sql', 'txt'}
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
    
    @classmethod
    def is_valid_file(cls, filename):
        """Check if file has valid extension."""
        if not filename or '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in cls.ALLOWED_EXTENSIONS
    
    @classmethod
    def process_file(cls, file):
        """
        Process uploaded schema file.
        Returns: (success, message_or_context)
        """
        try:
            # Check filename
            if not file.filename:
                return False, "No file selected"
            
            if not cls.is_valid_file(file.filename):
                return False, "Invalid file type. Use: .json, .csv, .sql, .txt"
            
            # Read file
            content = file.read().decode('utf-8')
            
            # Check size
            if len(content.encode('utf-8')) > cls.MAX_FILE_SIZE:
                return False, "File too large (max 2MB)"
            
            # Check if empty
            if not content.strip():
                return False, "File is empty"
            
            # Get file extension
            ext = file.filename.rsplit('.', 1)[1].lower()
            
            # Generate context based on file type
            context = cls._generate_context(content, ext)
            return True, context
            
        except UnicodeDecodeError:
            return False, "File encoding error. Use UTF-8"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    @classmethod
    def process_sql_server_schema(cls, server: str, database: str, 
                                 tables: List[str], schema_name: str = 'dbo',
                                 username: str = None, password: str = None,
                                 use_windows_auth: bool = True,
                                 include_sample_data: bool = False) -> Tuple[bool, str]:
        """
        Extract schema from SQL Server database.
        
        Args:
            server: SQL Server instance
            database: Database name
            tables: List of table names to extract
            schema_name: Database schema name (default: 'dbo')
            username: SQL Server username (if not using Windows auth)
            password: SQL Server password (if not using Windows auth)
            use_windows_auth: Use Windows authentication
            include_sample_data: Include sample data in context
            
        Returns:
            (success, context_or_error_message)
        """
        try:
            # Test connection first
            success, message = test_connection_params(
                server=server,
                database=database,
                username=username,
                password=password,
                use_windows_auth=use_windows_auth
            )
            
            if not success:
                return False, f"Database connection failed: {message}"
            
            # Create extractor
            extractor = create_extractor_from_params(
                server=server,
                database=database,
                username=username,
                password=password,
                use_windows_auth=use_windows_auth
            )
            
            if not extractor.connect():
                return False, "Failed to connect to database"
            
            try:
                # Validate tables exist
                available_tables = extractor.get_tables(schema_name)
                
                if not tables:
                    # If no specific tables requested, get all available
                    if not available_tables:
                        return False, "No tables found in the database"
                    tables = available_tables[:10]  # Limit to first 10 tables
                else:
                    # Validate requested tables exist
                    missing_tables = []
                    for table in tables:
                        if '.' in table:
                            # Fully qualified name
                            if table not in available_tables:
                                missing_tables.append(table)
                        else:
                            # Just table name, check with schema
                            full_name = f"{schema_name}.{table}"
                            if full_name not in available_tables and table not in available_tables:
                                missing_tables.append(table)
                    
                    if missing_tables:
                        return False, f"Tables not found: {', '.join(missing_tables)}"
                
                # Generate schema context
                context = extractor.generate_schema_context(
                    table_names=tables,
                    schema_name=schema_name,
                    include_sample_data=include_sample_data
                )
                
                return True, context
                
            finally:
                extractor.disconnect()
                
        except Exception as e:
            return False, f"SQL Server schema extraction failed: {str(e)}"
    
    @classmethod
    def get_sql_server_tables(cls, server: str, database: str, 
                             schema_name: str = 'dbo',
                             username: str = None, password: str = None,
                             use_windows_auth: bool = True) -> Tuple[bool, List[str]]:
        """
        Get list of available tables from SQL Server.
        
        Returns:
            (success, list_of_tables_or_error_message)
        """
        try:
            # Test connection
            success, message = test_connection_params(
                server=server,
                database=database,
                username=username,
                password=password,
                use_windows_auth=use_windows_auth
            )
            
            if not success:
                return False, [f"Connection failed: {message}"]
            
            # Get tables
            extractor = create_extractor_from_params(
                server=server,
                database=database,
                username=username,
                password=password,
                use_windows_auth=use_windows_auth
            )
            
            if extractor.connect():
                try:
                    tables = extractor.get_tables(schema_name)
                    return True, tables
                finally:
                    extractor.disconnect()
            else:
                return False, ["Failed to connect to database"]
                
        except Exception as e:
            return False, [f"Error: {str(e)}"]
    @classmethod
    def _generate_context(cls, content, file_type):
        """Generate simple context based on file type."""
        
        if file_type == 'json':
            try:
                # Try to format JSON nicely
                parsed = json.loads(content)
                formatted = json.dumps(parsed, indent=2)
                return f"Use this JSON structure as reference:\n\n{formatted}\n\nGenerate data following this structure."
            except:
                return f"Use this JSON as reference:\n\n{content}\n\nGenerate data following this structure."
        
        elif file_type == 'csv':
            try:
                # Get column names from CSV
                df = pd.read_csv(StringIO(content), nrows=3)
                columns = list(df.columns)
                sample = df.head(2).to_string(index=False)
                return f"Use these CSV columns: {', '.join(columns)}\n\nSample data:\n{sample}\n\nGenerate data with these columns."
            except:
                # Fallback: just use first line as headers
                lines = content.strip().split('\n')
                headers = lines[0] if lines else ""
                return f"Use these CSV columns: {headers}\n\nGenerate data with these columns."
        
        elif file_type == 'sql':
            return f"Use this SQL schema:\n\n{content}\n\nGenerate data that matches this database structure."
        
        elif file_type == 'txt':
            return f"Follow these specifications:\n\n{content}\n\nGenerate data according to these requirements."
        
        else:
            return f"Use this schema:\n\n{content}\n\nGenerate appropriate data."

# Enhanced helper functions for SQL Server integration
def get_sql_server_schema(server: str, database: str, tables: List[str],
                         schema_name: str = 'dbo', username: str = None, 
                         password: str = None, use_windows_auth: bool = True,
                         include_sample_data: bool = False) -> Tuple[bool, str]:
    """Get SQL Server schema context."""
    return SchemaValidator.process_sql_server_schema(
        server=server,
        database=database,
        tables=tables,
        schema_name=schema_name,
        username=username,
        password=password,
        use_windows_auth=use_windows_auth,
        include_sample_data=include_sample_data
    )

def list_sql_server_tables(server: str, database: str, schema_name: str = 'dbo',
                          username: str = None, password: str = None,
                          use_windows_auth: bool = True) -> Tuple[bool, List[str]]:
    """List available SQL Server tables."""
    return SchemaValidator.get_sql_server_tables(
        server=server,
        database=database,
        schema_name=schema_name,
        username=username,
        password=password,
        use_windows_auth=use_windows_auth
    )

# Simple helper functions
def validate_schema_file(file):
    """Simple validation function."""
    return SchemaValidator.process_file(file)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return SchemaValidator.is_valid_file(filename)
