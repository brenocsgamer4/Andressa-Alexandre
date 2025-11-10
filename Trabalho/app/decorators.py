from functools import wraps
from flask_login import current_user
from flask import flash, redirect, url_for

def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor, faça login para acessar esta página.', 'info')
            return redirect(url_for('main.login'))
        
        if current_user.role != 'Admin':
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('main.home'))
        
        return f(*args, **kwargs)
    return decorated_function