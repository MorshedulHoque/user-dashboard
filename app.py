from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Database and secret key configurations
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'linkedin_commenter_draft'

mysql = MySQL(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account and check_password_hash(account['password'], password):
            session['email'] = email
            session['full_name'] = account['full_name']
            session['user_id'] = account['Id']  # Store user ID in session
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid login attempt.', 'danger')
    return render_template('login.html')

@app.route('/get_comments/<int:user_id>', methods=['GET'])
def get_comments(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT post_text, generated_comment, emotion, created_at FROM comments_history WHERE user_id = %s ORDER BY created_at DESC',
                   (user_id,))
    comments = cursor.fetchall()
    return jsonify(comments), 200

@app.route('/get_comments_top5/<int:user_id>', methods=['GET'])
def get_comments_top5(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT post_text, generated_comment, emotion, created_at FROM comments_history WHERE user_id = %s ORDER BY created_at DESC LIMIT 5', 
                   (user_id,))
    comments = cursor.fetchall()
    return jsonify(comments), 200

@app.route('/get_comment_count/<int:user_id>', methods=['GET'])
def get_comment_count(user_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Count total comments generated by the specific user
        cursor.execute('SELECT COUNT(*) AS total_comments FROM comments_history WHERE user_id = %s', (user_id,))
        result = cursor.fetchone()
        cursor.close()
        
        total_comments = result['total_comments'] if result else 0
        return jsonify({"total_comments": total_comments}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_request_count/<int:user_id>', methods=['GET'])
def get_request_count(user_id):
    today = datetime.date.today()
    
    try:
        with mysql.connection.cursor(MySQLdb.cursors.DictCursor) as cursor:
            # Fetch the latest request count for the current day
            cursor.execute('SELECT request_count FROM daily_usage WHERE user_id = %s AND date = %s', (user_id, today))
            usage = cursor.fetchone()

            if usage:
                return jsonify({"request_count": usage['request_count']}), 200
            else:
                # If no usage data for today, return 0 request count
                return jsonify({"request_count": 0}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']

        # Fetch user's full name
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT full_name FROM user WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        # Fetch request count
        today = datetime.date.today()
        cursor.execute('SELECT request_count FROM daily_usage WHERE user_id = %s AND date = %s', (user_id, today))
        daily_usage = cursor.fetchone()

        # Fetch total comments
        cursor.execute("SELECT COUNT(*) AS total_comments FROM comments_history WHERE user_id = %s", (user_id,))
        comments_count = cursor.fetchone()

        cursor.close()

        # Extract the necessary information
        full_name = user['full_name'] if user else "Guest"
        request_count = daily_usage['request_count'] if daily_usage else 0
        total_comments = comments_count['total_comments'] if comments_count else 0

        # Pass the information to the dashboard template
        return render_template('dashboard.html', user_id=user_id, full_name=full_name, request_count=request_count, total_comments=total_comments, active_page='dashboard')

    # Redirect to login if not logged in
    return redirect('/login')

@app.route("/table")
def table():
    if 'user_id' in session:
        user_id = session['user_id']
        return render_template('table.html', user_id=user_id, active_page='table')
    return redirect('/login')  # Redirect if not logged in

@app.route("/billing")
def billing():
    return render_template("billing.html", active_page='billing')

@app.route("/notifications")
def notifications():
    return render_template("notifications.html", active_page='notifications')

@app.route("/profile", methods=['GET', 'POST'])
def profile():
    # Ensure user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        # Get form data
        new_name = request.form['name']
        new_password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Flag to check if the profile was updated
        profile_updated = False

        # Update user name
        if new_name and new_name != session['full_name']:  # Only update if the name has changed
            cursor.execute('UPDATE user SET full_name = %s WHERE Id = %s', (new_name, user_id))
            profile_updated = True  # Mark that the profile was updated
        
        # Update password if provided and confirmed
        if new_password:
            if new_password == confirm_password:
                hashed_password = generate_password_hash(new_password)
                cursor.execute('UPDATE user SET password = %s WHERE Id = %s', (hashed_password, user_id))
                profile_updated = True  # Mark that the profile was updated
            else:
                flash('Passwords do not match!', 'danger')
                return render_template('profile.html', current_user={'full_name': session['full_name']})

        mysql.connection.commit()

        # Flash message if the profile was updated
        if profile_updated:
            flash('Profile updated successfully!', 'success')
            session['full_name'] = new_name  # Update session data if name changed

    # Fetch current user info
    cursor.execute('SELECT full_name FROM user WHERE Id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()

    # Pass user info to the template
    return render_template('profile.html', current_user=user, active_page='profile')


@app.route('/signout')
def signout():
    session.clear()  # Clear the session data
    return redirect('/login')  # Redirect to login page

@app.route("/")
def home():
    if 'email' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
