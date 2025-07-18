from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import json

class ConversationMemory:
    def __init__(self):
        self.conversations: Dict[str, List[Dict]] = {}
        self.current_session: Optional[str] = None
    
    def create_session(self) -> str:
        """Create a new conversation session"""
        session_id = str(uuid.uuid4())
        self.conversations[session_id] = []
        self.current_session = session_id
        return session_id
    
    def add_exchange(self, session_id: str, question: str, sql_query: str, result: Any, explanation: str):
        """Add a question-answer exchange to memory"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        exchange = {
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'sql_query': sql_query,
            'result': str(result) if not isinstance(result, str) else result,
            'explanation': explanation
        }
        
        self.conversations[session_id].append(exchange)
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation history for context"""
        if session_id not in self.conversations:
            return []
        
        return self.conversations[session_id][-limit:]
    
    def get_context_for_question(self, session_id: str, current_question: str) -> str:
        """Get relevant context from conversation history"""
        history = self.get_conversation_history(session_id, 5)
        
        if not history:
            return ""
        
        context = "Previous conversation context:\n"
        for exchange in history[-3:]:  # Last 3 exchanges
            context += f"Q: {exchange['question']}\n"
            context += f"A: {exchange['explanation']}\n\n"
        
        return context