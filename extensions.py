# extensions.py

from flask_wtf import CSRFProtect
from flask import request, jsonify, redirect, url_for, session
from flask_wtf.csrf import CSRFError

csrf = CSRFProtect()

def format_inr(value):
    """Format number into Indian currency style with rupee symbol."""
    if value is None or value == "":
        return "—"
    try:
        # Ensure float
        value = float(str(value).replace(",", ""))
        # Split integer and decimal
        integer, dot, fraction = f"{value:.2f}".partition(".")
        # Indian number system formatting
        last3 = integer[-3:]
        rest = integer[:-3]
        if rest:
            rest = ",".join(
                [rest[max(i - 2, 0):i] for i in range(len(rest), 0, -2)][::-1]
            )
            formatted = rest + "," + last3
        else:
            formatted = last3
        return f"₹{formatted}.{fraction}"
    except Exception:
        return str(value)


def init_extensions(app):
    csrf.init_app(app)

    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)

    @app.before_request
    def enforce_session():
        allowed_routes = ['auth.login', 'static', 'main.landing'] 
        if 'user_id' not in session and request.endpoint not in allowed_routes:
            return redirect(url_for('auth.login'))

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        if request.content_type == "application/json":
            return jsonify({"error": f"CSRF Error: {e.description}"}), 400
        return f"CSRF Error: {e.description}", 400
    
    app.jinja_env.filters["inr"] = format_inr
    