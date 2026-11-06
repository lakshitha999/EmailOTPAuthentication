# Email OTP Authentication

A full-stack Email OTP Authentication application.

## Tech Stack
| Layer    | Technology          |
|----------|---------------------|
| Frontend | React 18 + Vite 5   |
| Backend  | Python 3 + Flask    |
| Database | SQLite              |
| Email    | Gmail SMTP          |

## Project Structure
```
EmailOTPAuthentication/
├── frontend/                  # React + Vite app
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── src/
│       ├── main.jsx           # App entry point
│       ├── App.jsx            # Router + routes
│       ├── components/
│       │   ├── AlertMessage.jsx
│       │   ├── OTPInput.jsx
│       │   └── CountdownTimer.jsx
│       ├── pages/
│       │   ├── LoginPage.jsx
│       │   ├── OTPPage.jsx
│       │   └── SuccessPage.jsx
│       ├── services/
│       │   └── api.js         # Axios API client
│       └── styles/
│           ├── global.css
│           ├── auth.css
│           ├── otp.css
│           └── success.css
└── backend/                   # Flask API (coming soon)
    └── README.md
```

## Getting Started

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

### Backend (coming soon)
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
