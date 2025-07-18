import bcrypt
import uuid
from typing import Optional, Dict
from datetime import datetime
import streamlit as st

class SecurityManager:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_session(self, user_id: str) -> str:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
        return session_id
    
    def validate_session(self, session_id: str) -> bool:
        """Validate session"""
        if session_id not in self.sessions:
            return False
        
        # Update last activity
        self.sessions[session_id]['last_activity'] = datetime.now()
        return True
    
    def sanitize_query(self, query: str) -> str:
        """Basic query sanitization"""
        # Remove potentially dangerous characters/patterns
        dangerous_patterns = [';', '--', '/*', '*/', 'xp_', 'sp_']
        
        for pattern in dangerous_patterns:
            query = query.replace(pattern, '')
        
        return query.strip()