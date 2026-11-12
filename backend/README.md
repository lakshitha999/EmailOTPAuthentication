The Email OTP Authentication System is a web-based application that provides secure user authentication through email verification.

Instead of using a traditional password-based login, users can enter their email address and receive a One-Time Password (OTP) to verify their identity.

The project is designed with a React frontend and a Python Flask backend, with SQLite used for data storage.

Project Objectives

Provide simple and secure email-based login.

Verify users through a 6-digit OTP.

Send OTPs to registered email addresses using Gmail SMTP.

Ensure OTP expiration for security.

Prevent repeated OTP requests through rate limiting.

Provide a user-friendly authentication experience.

Technology Stack

Frontend

React.js

Vite

JavaScript

HTML

CSS

Backend

Python

Flask

Flask REST API

Database

SQLite

SQLAlchemy

Email Service

Gmail SMTP

Main Features

Email Login: Users enter their email address to initiate authentication.

OTP Generation: A unique 6-digit OTP is generated.

Email Verification: OTP is sent to the user's email address.

OTP Validation: Users submit the received OTP for verification.

OTP Expiration: OTPs are valid only for a limited period.

Resend OTP: Users can request a new OTP.

Rate Limiting: Restricts excessive OTP requests to improve security.

Application Workflow

User opens the login page.

User enters their email address.

Frontend sends an API request to the Flask backend.

Backend generates an OTP.

OTP is sent to the user's email through Gmail SMTP.

User enters the received OTP.

Backend validates the OTP and checks its expiration.

If the OTP is valid, authentication is successful.

If the OTP is invalid or expired, an appropriate error message is displayed.

Backend Structure

The backend is planned with a modular architecture:

app.py: Main Flask application entry point.

config.py: Application and email configuration.

models.py: Database models and SQLite schema.

routes/auth.py: Authentication API endpoints.

services/otp_service.py: OTP generation, storage, expiry, and rate limiting.

services/email_service.py: Gmail SMTP email functionality.

requirements.txt: Python dependencies.

.env.example: Example environment configuration.

API Endpoints

Method

Endpoint

Purpose

POST

/api/send-otp

Generate and send OTP

POST

/api/verify-otp

Verify the submitted OTP

POST

/api/resend-otp

Resend a new OTP

Project Status

Current Status: Frontend and backend development in progress.

The backend is planned using Python Flask. API integration, database connectivity, and email OTP authentication are part of the implementation plan.

Future Enhancements

User session management.

Secure OTP storage using hashing.

Improved authentication security.

Login success and failure handling.

Responsive UI for mobile and desktop devices.

Project: Email OTP Authentication System

Purpose: Secure passwordless authentication through email verification.