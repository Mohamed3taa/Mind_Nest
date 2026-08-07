# Mind Nest 🧠

> AI-Powered Study Hub — A Django MVT Web Application with Integrated AI Assistant

## Overview

Mind Nest is a web application that helps students organize their study materials, tasks, and notes while integrating an AI assistant to improve productivity.

## Technologies

- Python 3.10
- Django 5.2
- PostgreSQL
- HTML / CSS / JavaScript

## Features

- Authentication (Register, Login, Logout, Profile)
- Dashboard with study summary
- Study Planner (Tasks with priority & due date)
- Notes (CRUD + Categories + Search)
- Resources (Links & learning materials)
- AI Assistant integration
- Dark Mode
- Responsive Design

## Setup

1. Clone the repository
```bash
git clone https://github.com/Mohamed3taa/Mind_Nest.git
cd Mind_Nest
```

2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Setup database
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. Run the server
```bash
python manage.py runserver
```

## Project Structure

```
Mind_Nest/
├── mind_nest/          # Main project settings
├── accounts/           # Authentication & Profile
├── dashboard/          # Dashboard & Summary
├── planner/            # Study Planner & Tasks
├── notes/              # Notes & Categories
├── resources/          # Learning Resources
├── ai_assistant/       # AI Integration
├── templates/          # HTML Templates
├── static/             # CSS, JS, Images
└── media/              # User Uploaded Files
```

## Team

- Mohamed Ataa
- Sarah Yasser

## License

ITI Django Web Development Course Project — 2026
