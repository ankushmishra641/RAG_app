import streamlit as st
import os
import sys
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Check if running with streamlit
def check_streamlit_context():
    """Check if app is running in proper Streamlit context"""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        return ctx is not None
    except:
        return False

# Early check before any imports
if not check_streamlit_context():
    print("❌ ERROR: This app must be run with Streamlit!")
    print("💡 Correct command: streamlit run main.py")
    print("❌ Don't use: python main.py")
    sys.exit(1)

# Import modules with error handling
try:
    from database.connection import DatabaseManager
    from rag.schema_analyzer import SchemaAnalyzer
    from rag.sql_generator import SQLGenerator
    from rag.memory_manager import ConversationMemory
    from rag.response_generator import ResponseGenerator
    from security.auth import SecurityManager
except ImportError as e:
    st.error(f"❌ Import Error: {e}")
    st.error("Please make sure all files are in the correct directories and contain the proper code.")
    st.stop()

# Page config
st.set_page_config(
    page_title="School Database Assistant",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark mode compatible CSS
st.markdown("""
<style>
    /* Main header */
    .main-header {
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 2rem;
        color: var(--text-color);
    }
    
    /* Chat messages with dark mode support */
    .chat-container {
        margin: 1rem 0;
    }
    
    .user-chat {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 0.5rem 0 0.5rem 2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .assistant-chat {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 0.5rem 2rem 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .chat-label {
        font-weight: bold;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        opacity: 0.9;
    }
    
    .chat-text {
        font-size: 1rem;
        line-height: 1.5;
        margin: 0;
    }
    
    /* Alternative chat boxes for different themes */
    .chat-box-user {
        background-color: #2E86C1;
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 2px solid #3498DB;
    }
    
    .chat-box-assistant {
        background-color: #28B463;
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 2px solid #2ECC71;
    }
    
    /* Streamlit native chat styling enhancement */
    .stChatMessage {
        background-color: transparent !important;
    }
    
    /* Welcome card */
    .welcome-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Sidebar enhancements */
    .sidebar-badge {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        text-align: center;
        margin: 0.5rem 0;
        font-weight: bold;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Hide Streamlit elements */
    .stDeployButton {display: none;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}
    
    /* Ensure text is always visible */
    .element-container {
        color: var(--text-color);
    }
</style>
""", unsafe_allow_html=True)

class SchoolDatabaseApp:
    def __init__(self):
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize all components with better error handling"""
        try:
            # Initialize session state with proper checks
            if 'initialized' not in st.session_state:
                with st.spinner("Initializing your school database assistant..."):
                    # Test environment variables first
                    self.check_environment()
                    
                    # Initialize components
                    st.session_state.db_manager = DatabaseManager()
                    st.session_state.schema_analyzer = SchemaAnalyzer(st.session_state.db_manager)
                    st.session_state.sql_generator = SQLGenerator(st.session_state.schema_analyzer)
                    st.session_state.memory = ConversationMemory()
                    st.session_state.response_generator = ResponseGenerator()
                    st.session_state.security = SecurityManager()
                    st.session_state.conversation_history = []
                    st.session_state.session_id = st.session_state.memory.create_session()
                    st.session_state.show_technical = False
                    st.session_state.chat_style = "streamlit_native"  # Default to native chat
                    st.session_state.initialized = True
                
                st.success("✅ Your assistant is ready! Ask me anything about the school database.")
        
        except Exception as e:
            st.error(f"❌ Failed to initialize application: {e}")
            with st.expander("🔧 Troubleshooting Help"):
                st.markdown("""
                **Common Issues:**
                
                1. **Google API Key Issues:**
                   - Get your FREE API key from: https://makersuite.google.com/app/apikey
                   - Make sure it's set in .env file as GOOGLE_API_KEY
                
                2. **Database Connection Issues:**
                   - Check if MySQL server is running
                   - Verify credentials in .env file
                """)
            st.stop()
    
    def check_environment(self):
        """Check environment configuration for Gemini"""
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = {
            'GOOGLE_API_KEY': 'Google Gemini API key (FREE)',
            'MYSQL_HOST': 'MySQL server host',
            'MYSQL_USER': 'MySQL username',
            'MYSQL_PASSWORD': 'MySQL password',
            'MYSQL_DATABASE': 'MySQL database name'
        }
        
        missing_vars = []
        for var, description in required_vars.items():
            if not os.getenv(var):
                missing_vars.append(f"{var} ({description})")
        
        if missing_vars:
            st.error("❌ Missing environment variables:")
            for var in missing_vars:
                st.error(f"  • {var}")
            
            if 'GOOGLE_API_KEY' in str(missing_vars):
                st.info("🆓 Get your FREE Google API key from: https://makersuite.google.com/app/apikey")
            
            raise ValueError("Missing required environment variables")
    
    def render_sidebar(self):
        """Render sidebar with information and controls"""
        with st.sidebar:
            st.title("🏫 School Assistant")
            
            # Status badge
            st.markdown('<div class="sidebar-badge">🆓 FREE AI Assistant</div>', unsafe_allow_html=True)
            
            # Chat style selector
            st.markdown("### 🎨 Chat Style")
            chat_style = st.selectbox(
                "Choose chat appearance:",
                ["streamlit_native", "gradient_bubbles", "colored_boxes"],
                format_func=lambda x: {
                    "streamlit_native": "💬 Streamlit Native",
                    "gradient_bubbles": "🎨 Gradient Bubbles", 
                    "colored_boxes": "📦 Colored Boxes"
                }[x],
                index=0
            )
            st.session_state.chat_style = chat_style
            
            # Quick stats
            st.markdown("### 📊 Quick Info")
            if st.button("📈 Database Overview"):
                self.show_database_stats()
            
            # Developer mode
            st.markdown("### 🛠️ Developer Mode")
            show_tech = st.toggle("Show Technical Details", value=st.session_state.get('show_technical', False))
            st.session_state.show_technical = show_tech
            
            if show_tech:
                st.info("🔧 Technical details enabled")
                if st.button("🔍 View Database Schema"):
                    self.show_schema_info()
            else:
                st.info("💬 Clean mode active")
            
            # Session controls
            st.markdown("### 🔄 Session")
            if hasattr(st.session_state, 'conversation_history'):
                st.caption(f"Messages: {len(st.session_state.conversation_history)}")
            
            if st.button("🗑️ Clear History"):
                if hasattr(st.session_state, 'conversation_history'):
                    st.session_state.conversation_history = []
                if hasattr(st.session_state, 'memory'):
                    st.session_state.session_id = st.session_state.memory.create_session()
                st.rerun()
            
            # Example questions
            st.markdown("### 💡 Try These Questions")
            example_questions = [
                "How many students are in the school?",
                "Show me all available classes",
                "Which students have scholarships?",
                "What subjects are taught here?",
                "Who are the top performing students?"
            ]
            
            for i, question in enumerate(example_questions):
                if st.button(question, key=f"example_{i}"):
                    st.session_state.pending_question = question
                    st.rerun()
    
    def show_schema_info(self):
        """Display database schema information"""
        st.markdown("### 📋 Database Schema")
        
        try:
            tabs = st.tabs(["Tables", "Relationships", "Sample Data"])
            
            with tabs[0]:
                schema_info = st.session_state.schema_analyzer.schema_info
                for table in schema_info['TABLE_NAME'].unique():
                    with st.expander(f"Table: {table}"):
                        table_cols = schema_info[schema_info['TABLE_NAME'] == table]
                        st.dataframe(table_cols[['COLUMN_NAME', 'DATA_TYPE', 'IS_NULLABLE', 'COLUMN_KEY']])
            
            with tabs[1]:
                fk_info = st.session_state.schema_analyzer.foreign_keys
                if not fk_info.empty:
                    st.dataframe(fk_info)
                else:
                    st.info("No foreign key relationships found")
            
            with tabs[2]:
                selected_table = st.selectbox("Select table for sample data:", 
                                            schema_info['TABLE_NAME'].unique())
                if selected_table:
                    sample_data = st.session_state.db_manager.get_sample_data(selected_table, 10)
                    st.dataframe(sample_data)
        except Exception as e:
            st.error(f"Error displaying schema info: {e}")
    
    def show_database_stats(self):
        """Show database statistics"""
        st.markdown("### 📈 School Database Overview")
        
        try:
            # Get record counts
            tables = ['students', 'classes', 'sections', 'subjects', 'marks', 'parents', 'bankdetails', 'scholarships']
            counts = []
            
            for table in tables:
                try:
                    count_query = f"SELECT COUNT(*) as count FROM {table}"
                    result = st.session_state.db_manager.execute_query(count_query)
                    counts.append(result.iloc[0]['count'])
                except:
                    counts.append(0)
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("👨‍🎓 Students", counts[0])
            with col2:
                st.metric("📚 Classes", counts[1])
            with col3:
                st.metric("📖 Subjects", counts[3])
            with col4:
                st.metric("📝 Marks", counts[4])
            
        except Exception as e:
            st.error(f"Error displaying database statistics: {e}")
    
    def process_question(self, question: str):
        """Process user question and generate response"""
        try:
            with st.spinner("🤔 Let me check the database for you..."):
                # Generate SQL query
                sql_result = st.session_state.sql_generator.generate_sql(question)
                
                # Validate query
                if not st.session_state.sql_generator.validate_sql(sql_result.query):
                    return {
                        'response': "I apologize, but I couldn't generate a safe query for your question. Could you please rephrase it?",
                        'error': True
                    }
                
                # Execute query
                query_results = st.session_state.db_manager.execute_query(sql_result.query)
                
                # Get conversation context
                context = st.session_state.memory.get_context_for_question(
                    st.session_state.session_id, question
                )
                
                # Generate natural language response
                response = st.session_state.response_generator.generate_response(
                    question, sql_result.query, query_results, context
                )
                
                # Store in memory
                st.session_state.memory.add_exchange(
                    st.session_state.session_id,
                    question,
                    sql_result.query,
                    query_results,
                    response
                )
                
                # Add to conversation history
                st.session_state.conversation_history.append({
                    'timestamp': datetime.now(),
                    'question': question,
                    'response': response,
                    'sql_query': sql_result.query,
                    'results': query_results,
                    'confidence': sql_result.confidence,
                    'error': False
                })
                
                return {
                    'response': response,
                    'error': False
                }
        
        except Exception as e:
            error_response = "I encountered an issue while processing your question. Please try rephrasing it or ask something else."
            
            if hasattr(st.session_state, 'conversation_history'):
                st.session_state.conversation_history.append({
                    'timestamp': datetime.now(),
                    'question': question,
                    'response': error_response,
                    'sql_query': f"Error: {str(e)}",
                    'results': None,
                    'confidence': 0.0,
                    'error': True
                })
            
            return {
                'response': error_response,
                'error': True
            }
    
    def render_chat_message(self, exchange, index):
        """Render a single chat message based on selected style"""
        chat_style = st.session_state.get('chat_style', 'streamlit_native')
        
        if chat_style == "streamlit_native":
            # Use Streamlit's native chat elements
            with st.chat_message("user"):
                st.write(exchange["question"])
            
            with st.chat_message("assistant"):
                st.write(exchange["response"])
                
        elif chat_style == "gradient_bubbles":
            # Custom gradient bubble style
            st.markdown(f"""
            <div class="chat-container">
                <div class="user-chat">
                    <div class="chat-label">You</div>
                    <div class="chat-text">{exchange["question"]}</div>
                </div>
                <div class="assistant-chat">
                    <div class="chat-label">Assistant</div>
                    <div class="chat-text">{exchange["response"]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        elif chat_style == "colored_boxes":
            # Colored box style
            st.markdown(f"""
            <div class="chat-box-user">
                <strong>🧑 You:</strong><br>
                {exchange["question"]}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="chat-box-assistant">
                <strong>🤖 Assistant:</strong><br>
                {exchange["response"]}
            </div>
            """, unsafe_allow_html=True)
        
        # Technical details (if enabled)
        if st.session_state.get('show_technical', False):
            with st.expander(f"🔧 Technical Details (Confidence: {exchange['confidence']:.1f})"):
                st.markdown("**SQL Query Generated:**")
                st.code(exchange['sql_query'], language='sql')
                
                if isinstance(exchange['results'], pd.DataFrame) and not exchange['results'].empty:
                    st.markdown("**Raw Database Results:**")
                    st.dataframe(exchange['results'], use_container_width=True)
    
    def render_chat_interface(self):
        """Render the main chat interface"""
        st.markdown('<h1 class="main-header">🏫 School Database Assistant</h1>', unsafe_allow_html=True)
        
        # Welcome message for new users
        if not st.session_state.get('conversation_history', []):
            st.markdown("""
            <div class="welcome-card">
                <h3>👋 Welcome to Your School Database Assistant!</h3>
                <p>Ask me anything about students, classes, grades, or any school data.<br>
                I'll provide clear answers in plain English!</p>
                <p style="opacity: 0.8; font-size: 0.9rem;">
                💡 Try: "How many students are in grade 10?" or "Who are the top students in Math?"
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Handle pending question from sidebar
        if hasattr(st.session_state, 'pending_question'):
            question = st.session_state.pending_question
            del st.session_state.pending_question
            result = self.process_question(question)
            if result:
                st.rerun()
        
        # Chat input
        question = st.chat_input("💬 Ask me anything about the school database...")
        
        if question:
            result = self.process_question(question)
            if result:
                st.rerun()
        
        # Display conversation history
        if hasattr(st.session_state, 'conversation_history') and st.session_state.conversation_history:
            st.markdown("---")
            
            for i, exchange in enumerate(reversed(st.session_state.conversation_history)):
                self.render_chat_message(exchange, i)
                
                # Add divider between conversations
                if i < len(st.session_state.conversation_history) - 1:
                    st.markdown("---")
    
    def run(self):
        """Run the Streamlit application"""
        self.render_sidebar()
        self.render_chat_interface()

def main():
    """Main application entry point"""
    app = SchoolDatabaseApp()
    app.run()

if __name__ == "__main__":
    main()