import uuid
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, flash


def generate_salt() -> str:
    """Génère un salt unique"""
    return uuid.uuid4().hex


def hash_password(password: str, salt: str) -> str:
    """Hashage sécurisé du mot de passe"""
    return hashlib.sha256(f"{password}{salt}".encode("UTF-8")).hexdigest()


def generate_reset_token() -> str:
    """Génère un token unique pour la réinitialisation de mot de passe"""
    return uuid.uuid4().hex


def get_token_expiry() -> datetime:
    return datetime.utcnow() + timedelta(hours=1)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter pour accéder à cette page.',
                  'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('Accès non autorisé.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    return True


def validate_email(email: str) -> bool:
    """Valide le format de l'email"""
    if not email or '@' not in email or '.' not in email:
        return False
    return True


def validate_phone(phone: str) -> bool:
    if not phone or len(phone) < 10:
        return False
    return True


def sanitize_input(value: str) -> str:
    """Nettoie les entrées utilisateur"""
    if not value:
        return ""
    return value.strip()
