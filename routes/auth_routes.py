# routes/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.user_model import UserModel
import bcrypt

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('auth_bp.register'))

        UserModel.create_user(full_name, email, password)
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('auth_bp.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = UserModel.find_by_email(email)

        if user:
            user_id, full_name, user_email, hashed_pw = user
            if bcrypt.checkpw(password.encode('utf-8'), hashed_pw.encode('utf-8')):
                session['user_id'] = user_id
                session['user_name'] = full_name
                flash("Login successful!", "success")
                return redirect(url_for('index'))
            else:
                flash("Invalid password.", "danger")
        else:
            flash("User not found.", "danger")

    return render_template('login.html')



@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth_bp.login'))


# =======================
# SETTINGS API
# =======================
@auth_bp.route('/me', methods=['GET'])
def auth_me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    user = UserModel.get_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user[0],
        "full_name": user[1],
        "email": user[2]
    })


@auth_bp.route('/update_profile', methods=['POST'])
def update_profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    full_name = request.json.get('full_name', '').strip()
    email = request.json.get('email', '').strip()
    if not full_name or not email:
        return jsonify({"error": "Full name and email are required"}), 400
    try:
        UserModel.update_profile(user_id, full_name, email)
        session['user_name'] = full_name
        return jsonify({"message": "Profile updated"})
    except Exception as e:
        return jsonify({"error": "Failed to update profile"}), 500


@auth_bp.route('/change_password', methods=['POST'])
def change_password():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.json or {}
    current_password = (data.get('current_password') or '').strip()
    new_password = (data.get('new_password') or '').strip()
    confirm_password = (data.get('confirm_password') or '').strip()
    if not current_password or not new_password or not confirm_password:
        return jsonify({"error": "All fields are required"}), 400
    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400
    if len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    try:
        if not UserModel.verify_password(user_id, current_password):
            return jsonify({"error": "Current password is incorrect"}), 400
        UserModel.update_password(user_id, new_password)
        return jsonify({"message": "Password changed"})
    except Exception:
        return jsonify({"error": "Failed to change password"}), 500
