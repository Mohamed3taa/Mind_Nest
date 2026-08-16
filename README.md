<div align="center">

# 🧠 Mind Nest
### AI-Powered Study Hub

*A Django MVT Web Application with Integrated AI Assistant*

![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_AI-2.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Railway](https://img.shields.io/badge/Deployed_on-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)

**🌐 Live Demo:** [web-production-ce34e.up.railway.app](https://web-production-ce34e.up.railway.app)

</div>

---

## 📖 Overview

**Mind Nest** is a full-featured web application that helps students organize their study materials, manage tasks, take notes, and save learning resources — all powered by a **personal AI Assistant** that works exclusively on the user's own data (notes, tasks, resources, and uploaded documents).

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Authentication** | Register, Login, Logout, Profile, Password Reset |
| 📊 **Dashboard** | Stats overview, Charts (Chart.js), Recent activity, Upcoming tasks |
| ✅ **Study Planner** | Create tasks with priority, due date, status tracking & AJAX toggle |
| 📝 **Notes** | Full CRUD with categories, tags, pin, search & PDF export |
| 📁 **Resources** | Save learning links with types, favorites & live search |
| 🤖 **AI Assistant** | Personal AI that answers based on YOUR data only |
| 📄 **Document Upload** | Upload PDF, DOCX, TXT files for AI analysis |
| 🌙 **Dark Mode** | Toggle between light and dark themes |
| 📱 **Responsive** | Works on all screen sizes |
| 🔢 **Pagination** | All list pages paginated |

---

## 🤖 AI Assistant — How it Works

The AI Assistant uses **Google Gemini 2.5 Flash** and is designed as a **personal study assistant**, not a general chatbot.

**On every message, the AI automatically reads:**
- 📝 All your notes (title, content, category, tags)
- ✅ All your tasks (title, priority, status, due date)
- 📁 All your saved resources (title, description, link)
- 📄 All your uploaded documents (PDF, DOCX, TXT — text extracted automatically)

**If you ask about something not in your data:**
> *"I don't find this in your Mind Nest data. Please add related notes, resources, or upload a document first."*

**Supported document formats:** PDF · DOCX · TXT

**What you can ask:**
- "Summarize my notes about Python"
- "Generate quiz questions from my uploaded document"
- "Create flashcards from my Django notes"
- "What tasks are still pending?"
- "What resources do I have saved?"

---

## 🛠️ Technologies

**Backend**
- Python 3.10
- Django 5.2 (MVT Architecture)
- PostgreSQL 18

**Frontend**
- HTML5 / CSS3 / JavaScript
- Bootstrap 5.3
- Chart.js

**AI Integration**
- Google Gemini 2.5 Flash API (`google-genai`)

**Libraries**
- `reportlab` — PDF Export
- `PyPDF2` — PDF text extraction
- `python-docx` — DOCX text extraction
- `whitenoise` — Static files in production
- `dj-database-url` — Database URL parsing

**Deployment**
- Railway (PostgreSQL + Web Service)

---

## 🗄️ Database Design — 11 Tables

The project uses **11 related tables** with One-to-Many and Many-to-Many relationships.

| Table | Description |
|-------|-------------|
| `auth_user` | Django built-in user |
| `accounts_profile` | One-to-One with User |
| `notes_category` | User's note categories |
| `notes_tag` | User's note tags |
| `notes_note` | Notes with M2M tags |
| `planner_task` | Study tasks |
| `resources_resourcetype` | Resource type lookup |
| `resources_resource` | Learning resources |
| `ai_conversation` | AI chat conversations |
| `ai_message` | Messages in each conversation |
| `ai_uploadeddocument` | User uploaded documents |

![ERD](ERD.png)

---

## 📸 Screenshots

<table>
  <tr>
    <td><img src="screenshots/Login page.png" alt="Login" width="400"/></td>
    <td><img src="screenshots/Dashboard.png" alt="Dashboard" width="400"/></td>
  </tr>
  <tr>
    <td><img src="screenshots/Study Planner.png" alt="Planner" width="400"/></td>
    <td><img src="screenshots/Notes.png" alt="Notes" width="400"/></td>
  </tr>
  <tr>
    <td><img src="screenshots/Resources.png" alt="Resources" width="400"/></td>
    <td><img src="screenshots/AI Assistant.png" alt="AI" width="400"/></td>
  </tr>
</table>

---

## 🚀 Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/Mohamed3taa/Mind_Nest.git
cd Mind_Nest
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=mind_nest_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
AI_API_KEY=your-gemini-api-key
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 5. Setup database
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run the server
```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000` in your browser.

---

## 📁 Project Structure

```
Mind_Nest/
├── mind_nest/              # Project settings & URLs
│   ├── settings.py         # Development settings
│   └── settings_production.py  # Production settings (Railway)
├── accounts/               # Authentication & Profile
├── dashboard/              # Dashboard & Statistics & Charts
├── planner/                # Study Planner & Tasks
├── notes/                  # Notes, Categories, Tags, PDF Export
├── resources/              # Learning Resources
├── ai_assistant/           # Gemini AI Chat + Document Upload
├── templates/              # HTML Templates
├── static/                 # CSS, JS, Images
├── media/                  # User Uploaded Files
├── screenshots/            # Application Screenshots
├── BackUp_DB/              # PostgreSQL Database Backup
├── ERD.png                 # Entity Relationship Diagram
├── Procfile                # Railway deployment
├── requirements.txt
└── README.md
```

---

## 👥 Team

| Name | Role |
|------|------|
| Mohamed Ataa | Full Stack Developer |
| Sarah Yasser | Full Stack Developer |

---

## 📚 Course

**ITI — Django Web Development Course**
Submission Deadline: August 20, 2026

---

<div align="center">
Made with ❤️ using Django & Google Gemini AI
</div>
