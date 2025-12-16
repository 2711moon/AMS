#config.py
from datetime import timedelta
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    WTF_CSRF_ENABLED = True

    # 🔐 Secure session settings
    SESSION_COOKIE_SECURE = False         # Only send over HTTPS
    SESSION_COOKIE_HTTPONLY = True       # JS can't access it
    SESSION_COOKIE_SAMESITE = 'Lax'      # Prevent CSRF via cross-site requests
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)  # Session expires after 30 mins
