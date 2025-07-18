from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import pandas as pd

class ResponseGenerator:
    def __init__(self):
        # Using Google Gemini Pro model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.3,
            convert_system_message_to_human=True
        )
        self.setup_prompt()
    
    def setup_prompt(self):
        """Setup the response generation prompt"""
        template = """
        You are a helpful assistant for a school database system. 
        Generate a natural, conversational response based on the query results.
        
        Original Question: {question}
        SQL Query Used: {sql_query}
        Query Results: {results}
        
        Context from previous conversation:
        {context}
        
        Guidelines:
        1. Provide a clear, friendly response in plain English
        2. If results are empty, explain that no data was found
        3. If there are many results, summarize key insights
        4. Include relevant numbers and statistics
        5. Suggest follow-up questions if appropriate
        6. Be conversational and helpful
        7. If the data shows interesting patterns, mention them
        
        Response:
        """
        
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["question", "sql_query", "results", "context"]
        )
    
    def generate_response(self, question: str, sql_query: str, results, context: str = "") -> str:
        """Generate natural language response from query results"""
        
        # Format results for better presentation
        if isinstance(results, pd.DataFrame):
            if results.empty:
                results_text = "No data found."
            elif len(results) > 10:
                results_text = f"Found {len(results)} records. Here are the first 10:\n{results.head(10).to_string(index=False)}"
            else:
                results_text = results.to_string(index=False)
        else:
            results_text = str(results)
        
        try:
            response = self.llm.invoke(
                self.prompt.format(
                    question=question,
                    sql_query=sql_query,
                    results=results_text,
                    context=context
                )
            )
            
            return response.content
        except Exception as e:
            # Fallback response if Gemini fails
            return f"I found some results for your question '{question}'. Here's what I discovered: {results_text}"
