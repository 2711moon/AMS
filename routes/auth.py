#routes/auth.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from forms import LoginForm
from extensions import csrf
from models import users_collection


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        identifier = request.form['identifier'].strip().lower()
        password = request.form['passcode']

        user = users_collection.find_one({'username': {'$regex': f'^{identifier}$', '$options': 'i'}})

        if user and check_password_hash(user['password'], password):
            session.permanent = True  # 🔐 Enables expiry
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['role'] = user.get('role', 'user')
            flash('Login successful.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    # 🔐 Prevent caching of login page
    response = make_response(render_template('login.html', form=form))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')

    response = make_response(redirect(url_for('auth.login')))
    response.set_cookie('theme', '', expires=0)  # Example: clearing a custom cookie
    return response

from flask import jsonify

@auth_bp.route('/api/change_password', methods=['POST'])

def api_change_password():
    if 'username' not in session:
        return jsonify(error="Unauthorized"), 401

    data = request.get_json(silent=True)
    if not data:
        return jsonify(error="Missing JSON body"), 400

    current_pw = data.get("current_password", "").strip()
    new_pw = data.get("new_password", "").strip()
    confirm_pw = data.get("confirm_password", "").strip()

    if not current_pw or not new_pw or not confirm_pw:
        return jsonify(error="All fields are required."), 400

    username = session['username']
    user = users_collection.find_one({'username': {'$regex': f'^{username}$', '$options': 'i'}})

    if not user or not check_password_hash(user["password"], current_pw):
        return jsonify(error="Current password is incorrect."), 400

    if new_pw != confirm_pw:
        return jsonify(error="New passwords do not match."), 400

    hashed = generate_password_hash(new_pw)
    users_collection.update_one({"_id": user["_id"]}, {"$set": {"password": hashed}})
    return jsonify(message="Password updated successfully."), 200



