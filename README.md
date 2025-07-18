# 🏫 School Database RAG Application

A **Retrieval-Augmented Generation (RAG)** application that allows users to query a school database using natural language and receive plain English responses.

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+
- MySQL Server
- Google API Key (free)

### **Installation**

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/school-rag-app.git
cd school-rag-app
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Setup database**
```bash
# Create database
mysql -u root -p -e "CREATE DATABASE school_db;"

# Import sample data
mysql -u root -p school_db < database/school_db.sql
```

5. **Get free Google API key**
- Visit: https://makersuite.google.com/app/apikey
- Create API key and add to `.env` file

## 🏃 **Running the Application**

```bash
streamlit run main.py
```

Visit `http://localhost:8501` in your browser.

## 🧪 **Testing the Application**

### **Basic Test Questions**
```
"How many students are in the database?"
"Show me all available classes"
"Which students have scholarships?"
"What subjects are taught here?"
"Find students with marks above 90"
```

### **Run Tests**
```bash
# Run all tests
python -m pytest tests/

# Test database connection
python -c "from database.connection import DatabaseManager; DatabaseManager()"
```

## ⚙️ **Configuration**

Update `.env` file:
```env
GOOGLE_API_KEY=your_google_api_key_here
MYSQL_HOST=localhost
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=school_db
```

## 🎨 **Features**

- 💬 **Natural Language Queries**: Ask questions in plain English
- 🆓 **Free AI**: Powered by Google Gemini (no subscription required)
- 🌙 **Dark Mode**: Multiple chat interface styles
- 🧠 **Memory**: Contextual follow-up questions
- 🔒 **Secure**: SQL injection prevention

## 🔧 **Troubleshooting**

**Database Connection Issues:**
```bash
# Check MySQL is running
sudo systemctl status mysql  # Linux
net start mysql              # Windows
```

**Import Errors:**
```bash
pip install -r requirements.txt
```

**API Key Issues:**
- Verify key at https://makersuite.google.com/app/apikey
- Check `.env` file formatting

## 📊 **Tech Stack**

- **Frontend**: Streamlit
- **AI**: LangChain + Google Gemini
- **Database**: MySQL
- **Language**: Python 3.8+

---

**Built for educational data accessibility** 🎓
