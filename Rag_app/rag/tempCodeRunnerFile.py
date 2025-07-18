from typing import Dict, List, Any
import json

class SchemaAnalyzer:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.schema_info = None
        self.foreign_keys = None
        self.analyze_schema()
    
    def analyze_schema(self):
        """Analyze database schema and relationships"""
        self.schema_info = self.db_manager.get_schema_info()
        self.foreign_keys = self.db_manager.get_foreign_keys()
    
    def get_schema_description(self) -> str:
        """Generate natural language description of schema"""
        tables = self.schema_info['TABLE_NAME'].unique()
        
        description = "School Database Schema Description:\n\n"
        
        for table in tables:
            table_columns = self.schema_info[self.schema_info['TABLE_NAME'] == table]
            description += f"Table: {table}\n"
            description += "Columns:\n"
            
            for _, col in table_columns.iterrows():
                nullable = "Optional" if col['IS_NULLABLE'] == 'YES' else "Required"
                key_info = f" ({col['COLUMN_KEY']})" if col['COLUMN_KEY'] else ""
                description += f"  - {col['COLUMN_NAME']}: {col['DATA_TYPE']}{key_info} - {nullable}\n"
            
            # Add relationships
            table_fks = self.foreign_keys[self.foreign_keys['TABLE_NAME'] == table]
            if not table_fks.empty:
                description += "Relationships:\n"
                for _, fk in table_fks.iterrows():
                    description += f"  - {fk['COLUMN_NAME']} references {fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']}\n"
            
            description += "\n"
        
        return description
    
    def get_table_info_for_llm(self) -> Dict[str, Any]:
        """Get structured table information for LLM"""
        tables_info = {}
        
        for table in self.schema_info['TABLE_NAME'].unique():
            table_columns = self.schema_info[self.schema_info['TABLE_NAME'] == table]
            
            columns = []
            for _, col in table_columns.iterrows():
                columns.append({
                    'name': col['COLUMN_NAME'],
                    'type': col['DATA_TYPE'],
                    'nullable': col['IS_NULLABLE'] == 'YES',
                    'key': col['COLUMN_KEY'],
                    'default': col['COLUMN_DEFAULT']
                })
            
            # Get relationships
            table_fks = self.foreign_keys[self.foreign_keys['TABLE_NAME'] == table]
            relationships = []
            for _, fk in table_fks.iterrows():
                relationships.append({
                    'column': fk['COLUMN_NAME'],
                    'references_table': fk['REFERENCED_TABLE_NAME'],
                    'references_column': fk['REFERENCED_COLUMN_NAME']
                })
            
            tables_info[table] = {
                'columns': columns,
                'relationships': relationships
            }
        
        return tables_info