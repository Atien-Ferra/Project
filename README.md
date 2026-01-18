# Focus Flow 📚🚀

**Focus Flow** is a high-performance study productivity platform designed to help students maximize their focus and academic achievement. It combines intelligent question generation, gamified progress tracking, and professional-grade time management tools into one seamless experience.

![Dashboard Preview](https://img.shields.io/badge/Status-Complete-success)
![University Project](https://img.shields.io/badge/University-Modul-blue)
![Tech Stack](https://img.shields.io/badge/Stack-Flask%20%7C%20MongoDB%20%7C%20Bootstrap-orange)

---

## Key Features

### AI-Powered Quiz Generation
Transform any study material into a customizable quiz. Upload PDFs, Word documents (.docx), or plain text files, and our system uses local LLMs (via LM Studio) to extract core concepts and generate multiple-choice questions automatically.

### Professional Focus Timer
Stay in the zone using our integrated Pomodoro timer. Choose between:
- **Pomodoro Mode**: 25 minutes of deep focus
- **Short Break**: 5 minutes to recharge
- **Long Break**: 15 minutes of deep rest after multiple focus sessions

### Smart Task Management
Organize your study day with our responsive task system. Link your focus sessions directly to specific tasks to track exactly where your time goes.

### Gamified Motivation
- **Streaks**: Maintain your daily momentum to grow your streak.
- **Rewards**: Earn 14+ unique badges (Bronze, Silver, Gold) based on tasks completed, quizzes taken, and session consistency.
- **Points**: Earn focus points for every successful study session and quiz completed.

### Comprehensive Dashboard
A bird's-eye view of your productivity:
- Real-time progress tracking percentages
- Habit consistency monitoring
- Notification system for task reminders and achievement alerts

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.10+, Flask |
| **Database** | MongoDB (NoSQL) |
| **Authentication** | Flask-Login with Scrypt hashing & PEPPER |
| **Frontend** | HTML5, CSS3, Bootstrap 5, jQuery |
| **Security** | Flask-Limiter (Rate Balancing), Flask-Talisman (Headers) |
| **AI Integration** | OpenAI-compatible API (LM Studio) |

---

## Team & Roles

| Contributor | Roles & Responsibilities |
|-------------|--------------------------|
| **Atien / Frenkli** | Full-Stack Development, Database Architecture, AI Integration, UI/UX Design |

---

## Getting Started

### Prerequisites
- **Python**: Version 3.10 or higher
- **MongoDB**: Local instance or Atlas URI
- **LM Studio**: Required for the Quiz Generation feature (running local model)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/focusflow.git
   cd focusflow
   ```

2. **Set up Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Mac/Linux
   # .venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your_secret_key
   MONGODB_URI=your_mongodb_connection_string
   PASSWORD_PEPPER=your_secure_pepper_string
   LMSTUDIO_BASE_URL=http://localhost:1234/v1
   ```

5. **Run the Application**
   ```bash
   flask run
   ```
   *The app will be available at http://127.0.0.1:5000*

---

## Project Structure

```text
focusflow/
├── routes/          # Modularized Flask blueprints (Auth, Dashboard, Quiz)
├── services/        # Business logic (AI Generation, Streaks, Rewards)
├── Static/          # CSS, Modular JS, Assets
├── Templates/       # HTML Jinja2 templates
└── app.py           # Application entry point
```

---

## License
This project was developed for academic purposes at Modul University Vienna.