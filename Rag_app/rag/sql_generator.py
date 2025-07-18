from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Optional
import re
import json
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SQLQuery(BaseModel):
    query: str = Field(description="The SQL query to execute")
    explanation: str = Field(description="Human-readable explanation of what the query does")
    confidence: float = Field(description="Confidence score from 0.0 to 1.0")

class SQLGenerator:
    def __init__(self, schema_analyzer):
        self.schema_analyzer = schema_analyzer
        # Using FREE Gemini 1.5 Flash - fastest free model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",  # FREE and fastest
            temperature=0.1,
            convert_system_message_to_human=True
        )
        self.output_parser = PydanticOutputParser(pydantic_object=SQLQuery)
        self.setup_chain()
    
    def setup_chain(self):
        """Setup the SQL generation chain"""
        
        template = """
        You are an expert SQL query generator for a school database. 
        
        Database Schema:
        {schema_description}
        
        Table Relationships:
        {table_info}
        
        User Question: {question}
        
        Generate a MySQL query that answers the user's question. Follow these guidelines:
        1. Use proper JOIN statements when accessing multiple tables
        2. Use appropriate WHERE clauses for filtering
        3. Use meaningful column aliases for readability
        4. Always use LIMIT clause for large result sets (default 100)
        5. Handle NULL values appropriately
        6. Use aggregate functions (COUNT, SUM, AVG) when appropriate
        7. Format the query for readability
        
        Only generate SELECT queries. Do not generate INSERT, UPDATE, or DELETE queries.
        
        Respond in this exact JSON format:
        {{
            "query": "your SQL query here",
            "explanation": "explanation of what the query does",
            "confidence": 0.8
        }}
        """
        
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["schema_description", "table_info", "question"]
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def generate_sql(self, question: str) -> SQLQuery:
        """Generate SQL query from natural language question"""
        schema_description = self.schema_analyzer.get_schema_description()
        table_info = json.dumps(self.schema_analyzer.get_table_info_for_llm(), indent=2)
        
        try:
            result = self.chain.run(
                schema_description=schema_description,
                table_info=table_info,
                question=question
            )
            
            # Try to parse JSON response
            try:
                # Clean the response to extract JSON
                cleaned_result = result.strip()
                if "```json" in cleaned_result:
                    cleaned_result = cleaned_result.split("```json")[1].split("```")[0]
                elif "```" in cleaned_result:
                    cleaned_result = cleaned_result.split("```")[1].split("```")[0]
                
                parsed = json.loads(cleaned_result)
                return SQLQuery(
                    query=parsed.get("query", "SELECT * FROM classes LIMIT 10"),
                    explanation=parsed.get("explanation", "Generated SQL query"),
                    confidence=float(parsed.get("confidence", 0.8))
                )
            except:
                # Fallback if JSON parsing fails
                return self.create_fallback_query(question)
                
        except Exception as e:
            return self.create_fallback_query(question, str(e))
    
    def create_fallback_query(self, question: str, error: str = "") -> SQLQuery:
        """Create a simple fallback query when AI generation fails"""
        question_lower = question.lower()
        
        # Simple pattern matching for common queries
        if "class" in question_lower and "all" in question_lower:
            return SQLQuery(
                query="SELECT class_id, class_name FROM classes LIMIT 100",
                explanation=f"Showing all classes from the database",
                confidence=0.7
            )
        elif "student" in question_lower and "count" in question_lower:
            return SQLQuery(
                query="SELECT COUNT(*) as total_students FROM students",
                explanation=f"Counting total number of students",
                confidence=0.7
            )
        elif "student" in question_lower and "all" in question_lower:
            return SQLQuery(
                query="SELECT roll_no, first_name, last_name, age FROM students LIMIT 100",
                explanation=f"Showing all students in the database",
                confidence=0.7
            )
        else:
            return SQLQuery(
                query="SELECT 'Error: Could not generate query' as error_message",
                explanation=f"Failed to generate query for: {question}. Error: {error}",
                confidence=0.0
            )
    
    def validate_sql(self, query: str) -> bool:
        """Basic SQL validation"""
        # Remove comments and normalize
        clean_query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        clean_query = clean_query.strip().upper()
        
        # Check for dangerous operations
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        for keyword in dangerous_keywords:
            if keyword in clean_query:
                return False
        
        # Must start with SELECT
        if not clean_query.startswith('SELECT'):
            return False
        
        return True