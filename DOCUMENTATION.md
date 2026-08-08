# Mind Nest — Project Documentation

> Complete technical documentation for the development team

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Project Structure](#2-project-structure)
3. [Database Design](#3-database-design)
4. [Apps & Features](#4-apps--features)
5. [URL Structure](#5-url-structure)
6. [Templates Guide](#6-templates-guide)
7. [Static Files](#7-static-files)
8. [AI Integration](#8-ai-integration)
9. [Environment Variables](#9-environment-variables)
10. [How to Run](#10-how-to-run)

---

## 1. Project Overview

**Mind Nest** is a Django MVT web application that helps students organize their study life.

| Item | Detail |
|------|--------|
| Framework | Django 5.2 (MVT only) |
| Database | PostgreSQL 18 |
| AI | Google Gemini 2.5 Flash |
| Frontend | HTML + CSS + Bootstrap 5 + JavaScript |
| Python | 3.10 |

### How Django MVT Works

```
Browser Request
      ↓
   URLs.py          ← finds the right view
      ↓
   Views.py         ← gets data from models, sends to template
      ↓
   Models.py        ← talks to PostgreSQL database
      ↓
   Templates (.html) ← renders the final HTML page
      ↓
Browser Response
```

---

## 2. Project Structure

```
Mind_Nest/
│
├── mind_nest/              ← Main project folder
│   ├── settings.py         ← All project settings
│   ├── urls.py             ← Main URL router
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/               ← APP 1: Authentication & Profile
│   ├── models.py           ← Profile model
│   ├── views.py            ← register, login, logout, profile, change_password
│   ├── forms.py            ← RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm
│   ├── urls.py             ← /accounts/...
│   ├── signals.py          ← Auto-create Profile when User is created
│   └── admin.py
│
├── dashboard/              ← APP 2: Dashboard
│   ├── views.py            ← index view with all stats + chart data
│   └── urls.py             ← /dashboard/
│
├── planner/                ← APP 3: Study Planner
│   ├── models.py           ← Task model
│   ├── views.py            ← task_list, task_create, task_edit, task_delete, task_toggle
│   ├── forms.py            ← TaskForm
│   └── urls.py             ← /planner/...
│
├── notes/                  ← APP 4: Notes
│   ├── models.py           ← Note, Category, Tag models
│   ├── views.py            ← CRUD + pin + PDF export + category CRUD
│   ├── forms.py            ← NoteForm, CategoryForm
│   └── urls.py             ← /notes/...
│
├── resources/              ← APP 5: Resources
│   ├── models.py           ← Resource, ResourceType models
│   ├── views.py            ← CRUD + favorite toggle
│   ├── forms.py            ← ResourceForm
│   └── urls.py             ← /resources/...
│
├── ai_assistant/           ← APP 6: AI Chat
│   ├── models.py           ← AIConversation, AIMessage models
│   ├── views.py            ← chat, new_conversation, send_message, delete_conversation
│   └── urls.py             ← /ai/...
│
├── templates/              ← All HTML files
│   ├── base.html           ← Main layout (sidebar + navbar)
│   ├── includes/
│   │   └── pagination.html ← Reusable pagination component
│   ├── accounts/           ← login, register, profile, change_password, password_reset
│   ├── dashboard/          ← index.html
│   ├── planner/            ← task_list.html
│   ├── notes/              ← note_list.html, note_detail.html
│   ├── resources/          ← resource_list.html
│   └── ai_assistant/       ← chat.html
│
├── static/
│   ├── css/main.css        ← All custom styles
│   ├── js/main.js          ← Dark mode, sidebar toggle, alerts
│   └── images/logo.png     ← App logo
│
├── media/                  ← User uploaded files (avatars)
├── screenshots/            ← App screenshots
├── BackUp_DB/              ← PostgreSQL backup
├── ERD.png                 ← Database diagram
├── .env                    ← Secret keys (NOT on GitHub)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 3. Database Design

### Tables & Relationships

```
auth_user (Django built-in)
    │
    ├──(1:1)── accounts_profile
    │           - avatar, bio, phone
    │
    ├──(1:N)── notes_category
    │           - name, color
    │           └──(1:N)── notes_note
    │                       - title, content, is_pinned
    │                       └──(M:N)── notes_tag
    │
    ├──(1:N)── notes_tag
    │           - name
    │
    ├──(1:N)── planner_task
    │           - title, description, priority, status, due_date, is_completed
    │
    ├──(1:N)── resources_resource
    │           - title, description, link, is_favorite
    │           └──(N:1)── resources_resourcetype
    │                       - name, icon
    │
    └──(1:N)── ai_conversation
                - title
                └──(1:N)── ai_message
                            - role (user/assistant), content
```

### Model Details

#### accounts/models.py — Profile
```python
class Profile(models.Model):
    user       = OneToOneField(User)   # linked to Django User
    avatar     = ImageField()          # profile picture
    bio        = TextField()
    phone      = CharField()
```

#### planner/models.py — Task
```python
class Task(models.Model):
    # Priority choices: low / medium / high
    # Status choices: todo / in_progress / done
    user         = ForeignKey(User)
    title        = CharField()
    description  = TextField()
    priority     = CharField(choices=Priority.choices)
    status       = CharField(choices=Status.choices)
    due_date     = DateField()
    is_completed = BooleanField()
```

#### notes/models.py — Note, Category, Tag
```python
class Category(models.Model):
    user  = ForeignKey(User)
    name  = CharField()
    color = CharField()     # hex color like #6366f1

class Tag(models.Model):
    user = ForeignKey(User)
    name = CharField()

class Note(models.Model):
    user      = ForeignKey(User)
    category  = ForeignKey(Category)    # optional
    tags      = ManyToManyField(Tag)    # multiple tags
    title     = CharField()
    content   = TextField()
    is_pinned = BooleanField()
```

#### resources/models.py — Resource, ResourceType
```python
class ResourceType(models.Model):
    name = CharField()    # Video, Article, Course, Book, Tool, GitHub, Other
    icon = CharField()    # Bootstrap icon class

class Resource(models.Model):
    user          = ForeignKey(User)
    resource_type = ForeignKey(ResourceType)
    title         = CharField()
    description   = TextField()
    link          = URLField()
    is_favorite   = BooleanField()
```

#### ai_assistant/models.py — AIConversation, AIMessage
```python
class AIConversation(models.Model):
    user  = ForeignKey(User)
    title = CharField()     # auto-set from first message

class AIMessage(models.Model):
    conversation = ForeignKey(AIConversation)
    role         = CharField()    # 'user' or 'assistant'
    content      = TextField()
```

---

## 4. Apps & Features

### accounts app

| View | URL | What it does |
|------|-----|--------------|
| `register_view` | `/accounts/register/` | Create new account |
| `login_view` | `/accounts/login/` | Login with username/password |
| `logout_view` | `/accounts/logout/` | Logout (POST only) |
| `profile_view` | `/accounts/profile/` | View & edit profile |
| `change_password_view` | `/accounts/change-password/` | Change password |
| Built-in | `/accounts/password-reset/` | Forgot password flow |

**signals.py** — When a new User is created, a Profile is automatically created:
```python
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
```

---

### dashboard app

The dashboard view collects data from ALL apps and passes it to the template:

```python
def index(request):
    # Stats
    total_tasks     = Task.objects.filter(user=user).count()
    total_notes     = Note.objects.filter(user=user).count()
    total_resources = Resource.objects.filter(user=user).count()

    # Chart data (JSON for Chart.js)
    priority_data = { 'labels': [...], 'data': [...], 'colors': [...] }
```

**Charts used:** Chart.js (CDN)
- Doughnut chart — Tasks by priority
- Bar chart — Tasks by status
- Doughnut chart — Content overview

---

### planner app

| View | URL | Method | What it does |
|------|-----|--------|--------------|
| `task_list` | `/planner/` | GET | Show all tasks with filter |
| `task_create` | `/planner/create/` | POST | Create new task |
| `task_edit` | `/planner/<pk>/edit/` | POST | Edit task |
| `task_delete` | `/planner/<pk>/delete/` | POST | Delete task |
| `task_toggle` | `/planner/<pk>/toggle/` | POST | Toggle complete (AJAX) |

**AJAX toggle** — When checkbox is clicked, JavaScript sends a fetch request:
```javascript
fetch(`/planner/${pk}/toggle/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': csrfToken }
})
```

---

### notes app

| View | URL | What it does |
|------|-----|--------------|
| `note_list` | `/notes/` | List all notes with sidebar filters |
| `note_detail` | `/notes/<pk>/` | View single note |
| `note_create` | `/notes/create/` | Create note (POST) |
| `note_edit` | `/notes/<pk>/edit/` | Edit note |
| `note_delete` | `/notes/<pk>/delete/` | Delete note |
| `note_toggle_pin` | `/notes/<pk>/pin/` | Pin/unpin note |
| `export_note_pdf` | `/notes/<pk>/export-pdf/` | Download single note as PDF |
| `export_all_notes_pdf` | `/notes/export-all-pdf/` | Download all notes as PDF |
| `category_create` | `/notes/category/create/` | Create category |
| `category_delete` | `/notes/category/<pk>/delete/` | Delete category |

**PDF Export** uses `reportlab` library:
```python
from reportlab.platypus import SimpleDocTemplate, Paragraph
# Builds PDF in memory and returns as HttpResponse
```

**Tags** are saved using a helper function:
```python
def save_tags(note, tags_input, user):
    # splits "python, django, web" into separate Tag objects
    for name in tags_input.split(','):
        tag, _ = Tag.objects.get_or_create(user=user, name=name.strip())
        note.tags.add(tag)
```

---

### resources app

| View | URL | What it does |
|------|-----|--------------|
| `resource_list` | `/resources/` | List resources with filter |
| `resource_create` | `/resources/create/` | Add resource |
| `resource_edit` | `/resources/<pk>/edit/` | Edit resource |
| `resource_delete` | `/resources/<pk>/delete/` | Delete resource |
| `resource_toggle_favorite` | `/resources/<pk>/favorite/` | Toggle favorite (AJAX) |

**ResourceTypes** are seeded automatically via migration:
Video, Article, Course, Book, Tool, GitHub, Other

---

### ai_assistant app

| View | URL | What it does |
|------|-----|--------------|
| `chat` | `/ai/` | Main chat page |
| `new_conversation` | `/ai/new/` | Create new conversation |
| `send_message` | `/ai/<conv_id>/send/` | Send message (AJAX → Gemini) |
| `delete_conversation` | `/ai/<conv_id>/delete/` | Delete conversation |

**How Gemini API works:**
```python
# 1. Build conversation history
contents = []
for msg in history:
    role = 'user' if msg.role == 'user' else 'model'
    contents.append(Content(role=role, parts=[Part(text=msg.content)]))

# 2. Add new message
contents.append(Content(role='user', parts=[Part(text=user_message)]))

# 3. Call API
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=contents,
    config=GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
)
```

---

## 5. URL Structure

```
/                           → redirect to /dashboard/
/admin/                     → Django Admin

/accounts/register/         → Register
/accounts/login/            → Login
/accounts/logout/           → Logout
/accounts/profile/          → Profile
/accounts/change-password/  → Change Password
/accounts/password-reset/   → Forgot Password

/dashboard/                 → Dashboard home

/planner/                   → Task list
/planner/create/            → Create task
/planner/<pk>/edit/         → Edit task
/planner/<pk>/delete/       → Delete task
/planner/<pk>/toggle/       → Toggle complete (AJAX)

/notes/                     → Note list
/notes/<pk>/                → Note detail
/notes/create/              → Create note
/notes/<pk>/edit/           → Edit note
/notes/<pk>/delete/         → Delete note
/notes/<pk>/pin/            → Pin/Unpin
/notes/<pk>/export-pdf/     → Export PDF
/notes/export-all-pdf/      → Export all PDF
/notes/category/create/     → Create category
/notes/category/<pk>/delete/ → Delete category

/resources/                 → Resource list
/resources/create/          → Add resource
/resources/<pk>/edit/       → Edit resource
/resources/<pk>/delete/     → Delete resource
/resources/<pk>/favorite/   → Toggle favorite (AJAX)

/ai/                        → AI Chat
/ai/new/                    → New conversation
/ai/<id>/send/              → Send message (AJAX)
/ai/<id>/delete/            → Delete conversation
```

---

## 6. Templates Guide

### base.html — Main Layout

All pages (except auth) extend `base.html`:

```html
{% extends 'base.html' %}

{% block title %}Page Title{% endblock %}
{% block nav_dashboard %}active{% endblock %}  ← highlights sidebar link

{% block content %}
  <!-- your page content here -->
{% endblock %}
```

**Auth pages** use `auth_content` block instead:
```html
{% block auth_content %}
  <!-- login/register form here -->
{% endblock auth_content %}
```

### Pagination

Add to any page that uses paginated data:
```html
{% include 'includes/pagination.html' with page_obj=tasks %}
```

---

## 7. Static Files

| File | Purpose |
|------|---------|
| `static/css/main.css` | All custom styles, CSS variables, dark mode, responsive |
| `static/js/main.js` | Dark mode toggle, sidebar toggle, auto-dismiss alerts, active links |
| `static/images/logo.png` | App logo |

### CSS Variables (main colors)
```css
--primary:       #6366f1;   /* Indigo */
--secondary:     #a855f7;   /* Purple */
--gradient:      linear-gradient(135deg, #6366f1, #a855f7);
--surface:       #ffffff;   /* Card background */
--bg:            #f1f5f9;   /* Page background */
```

---

## 8. AI Integration

**Library:** `google-genai` (official Google package)

**Setup in views.py:**
```python
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv('AI_API_KEY'))
```

**Model used:** `gemini-2.5-flash`

**System Prompt:**
```
You are Mind Nest AI, a helpful study assistant.
You help students with their studies, explain concepts,
summarize notes, generate quiz questions, and answer programming questions.
Be concise, friendly, and educational.
```

**API Key:** Stored in `.env` file as `AI_API_KEY` — never hardcoded.

---

## 9. Environment Variables

Create a `.env` file in the project root (never commit this file):

```env
SECRET_KEY=your-django-secret-key
DEBUG=True

DB_NAME=mind_nest_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

AI_API_KEY=your-gemini-api-key

EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 10. How to Run

```bash
# 1. Clone
git clone https://github.com/Mohamed3taa/Mind_Nest.git
cd Mind_Nest

# 2. Virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install packages
pip install -r requirements.txt

# 4. Create .env file (see section 9)

# 5. Create PostgreSQL database named: mind_nest_db

# 6. Run migrations
python manage.py migrate

# 7. Create admin user
python manage.py createsuperuser

# 8. Run server
python manage.py runserver
```

Open: `http://127.0.0.1:8000`

---

*Mind Nest — ITI Django Web Development Course — 2026*
