<div align="center">

# 🧠 Mind Nest
### AI-Powered Study Hub

*A Django MVT Web Application with Integrated AI Assistant & Quiz Engine*

![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_AI-2.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Railway](https://img.shields.io/badge/Deployed_on-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)
![Cloudinary](https://img.shields.io/badge/Cloudinary-Media_Storage-3448C5?style=for-the-badge&logo=cloudinary&logoColor=white)

**🌐 Live Demo:** https://web-mindnest-e8c67.up.railway.app/

</div>

---

## 📖 Overview

**Mind Nest** is a full-featured web application that helps students organize their study materials, manage tasks, take notes, save learning resources, and test themselves — all powered by a **personal AI Assistant** that works exclusively on the user's own data (notes, tasks, resources, and uploaded documents).

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Authentication** | Register, Login, Logout, Profile with avatar, Password Reset via email |
| 📊 **Dashboard** | Stats overview, Charts (Chart.js), Recent activity, Upcoming tasks, Quiz stats |
| ✅ **Study Planner** | Create tasks with priority, due date, status tracking & AJAX toggle |
| 📝 **Notes** | Full CRUD with categories, tags, pin, search & PDF export |
| 📁 **Resources** | Save learning links with types, favorites & live search |
| 🤖 **AI Assistant** | Personal AI that answers based on YOUR data only |
| 📄 **Document Upload** | Upload PDF, DOCX, TXT files for AI analysis |
| 🧩 **AI Quiz Engine** | Generate, take, and track quizzes from your notes/documents |
| 🖼️ **Profile Avatars** | Upload profile pictures stored on Cloudinary CDN |
| 🌙 **Dark Mode** | Toggle between light and dark themes |
| 📱 **Responsive** | Works on all screen sizes |
| 🔢 **Pagination** | All list pages paginated |

---

## 🧩 Quiz Feature

The Quiz Engine lets you **generate, take, and track quizzes** built entirely from your own study data.

### How it works

```
Your Notes / Documents
        ↓
  Gemini AI generates questions
        ↓
  Review & save the quiz
        ↓
  Take the quiz (one question at a time)
        ↓
  See results + review incorrect answers
```

### Quiz Capabilities

| Capability | Detail |
|-----------|--------|
| **AI Generation** | Gemini 2.5 Flash generates questions from your notes/documents |
| **Question Types** | Multiple Choice (4 options) · True / False |
| **Difficulty** | Easy · Medium · Hard |
| **Timer** | Optional countdown timer with auto-submit |
| **Progress** | One question at a time with dot navigator & progress bar |
| **Results** | Score ring, correct/incorrect/skipped review, explanations |
| **History** | All attempts saved — best score, average score, time taken |
| **Security** | Server-side scoring, ownership checks, atomic transactions |

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

**Storage & Media**
- Cloudinary — Profile avatars & uploaded images (CDN)
- WhiteNoise — Static files serving in production

**Email**
- Resend — Transactional email (password reset)

**Libraries**
- `reportlab` — PDF Export
- `PyPDF2` — PDF text extraction
- `python-docx` — DOCX text extraction
- `django-anymail` — Email service integration
- `dj-database-url` — Database URL parsing

**Deployment**
- Railway (PostgreSQL + Web Service)

---

## 🗄️ Database Design — 16 Tables

| Table | Description |
|-------|-------------|
| `auth_user` | Django built-in user |
| `accounts_profile` | One-to-One with User (avatar, bio, phone) |
| `notes_category` | User's note categories |
| `notes_tag` | User's note tags |
| `notes_note` | Notes with M2M tags |
| `planner_task` | Study tasks |
| `resources_resourcetype` | Resource type lookup |
| `resources_resource` | Learning resources |
| `ai_conversation` | AI chat conversations |
| `ai_message` | Messages in each conversation |
| `ai_uploadeddocument` | User uploaded documents |
| `quizzes_quiz` | Quiz metadata |
| `quizzes_question` | Questions per quiz |
| `quizzes_answer` | Answers per question |
| `quizzes_quizattempt` | Attempt record per user |
| `quizzes_attemptanswer` | Per-question answer in each attempt |

![ERD](ERD.png)

---

## 📸 Screenshots

<table>
  <tr>
    <td><img src="screenshots/Login page.png" alt="Login" width="400"/></td>
    <td><img src="screenshots/Register page.png" alt="Register" width="400"/></td>
  </tr>
  <tr>
    <td><img src="screenshots/Dashboard.png" alt="Dashboard" width="400"/></td>
    <td><img src="screenshots/Study Planner.png" alt="Planner" width="400"/></td>
  </tr>
  <tr>
    <td><img src="screenshots/Notes page.png" alt="Notes" width="400"/></td>
    <td><img src="screenshots/Resources page.png" alt="Resources" width="400"/></td>
  </tr>
  <tr>
    <td><img src="screenshots/AI Assistant.png" alt="AI Assistant" width="400"/></td>
    <td><img src="screenshots/Quizzes page.png" alt="Quizzes" width="400"/></td>
  </tr>
  <tr>
    <td><img src="screenshots/Profile page.png" alt="Profile" width="400"/></td>
    <td><img src="screenshots/Reset password.png" alt="Reset Password" width="400"/></td>
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

## ⚙️ Production Environment Variables (Railway)

| Variable | Description |
|----------|-------------|
| `DJANGO_SETTINGS_MODULE` | `mind_nest.settings_production` |
| `SECRET_KEY` | Django secret key |
| `DATABASE_URL` | PostgreSQL connection URL |
| `AI_API_KEY` | Google Gemini API key |
| `CLOUDINARY_URL` | Cloudinary connection URL |
| `RESEND_API_KEY` | Resend email service API key |

---

## 📁 Project Structure

```
Mind_Nest/
├── mind_nest/              # Project settings & URLs
│   ├── settings.py              # Development settings
│   ├── settings_production.py   # Production settings (Railway)
│   └── cloudinary_storage.py    # Custom Cloudinary storage backend
├── accounts/               # Authentication & Profile
├── dashboard/              # Dashboard & Statistics & Charts
├── planner/                # Study Planner & Tasks
├── notes/                  # Notes, Categories, Tags, PDF Export
├── resources/              # Learning Resources
├── ai_assistant/           # Gemini AI Chat + Document Upload
│   └── gemini.py           # Shared Gemini client
├── quizzes/                # AI Quiz Engine
│   ├── models.py           # Quiz, Question, Answer, Attempt models
│   ├── views.py            # Generate, Save, Take, Submit, Results
│   └── urls.py             # Quiz URL patterns
├── templates/              # HTML Templates
├── static/                 # CSS, JS, Images (source)
├── staticfiles/            # Collected static files (production)
├── media/                  # User Uploaded Files (development)
├── screenshots/            # Application Screenshots
├── BackUp_DB/              # PostgreSQL Database Backup
├── ERD.png                 # Entity Relationship Diagram
├── railway.json            # Railway deployment config
├── Procfile                # Fallback deployment config
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

---

<div align="center">
Made with ❤️ using Django & Google Gemini AI
</div>
