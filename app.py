from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import os
from werkzeug.utils import secure_filename

# Get the absolute path to the project root
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(basedir, 'Templates', 'HTML'),
            static_folder=os.path.join(basedir, 'Static'))
app.secret_key = 'your-secret-key-here-change-in-production'
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'Static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class (example)
class User(UserMixin):
    def __init__(self, id, name):
        self.id = id
        self.name = name

# User loader
@login_manager.user_loader
def load_user(user_id):
    # Replace with your user loading logic
    return User(user_id, "Example User")

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Mock user data (replace with database in production)
users = {
    'test@example.com': {
        'name': 'John Doe',
        'password': 'password123',
        'streak': 7,
        'quizzes_taken': 12,
        'tasks_done': 45
    },
    'alice@example.com': {
        'name': 'Alice Smith',
        'password': 'alice2024',
        'streak': 14,
        'quizzes_taken': 25,
        'tasks_done': 89
    },
    'bob@example.com': {
        'name': 'Bob Johnson',
        'password': 'bobpass456',
        'streak': 3,
        'quizzes_taken': 5,
        'tasks_done': 18
    },
    'sarah@example.com': {
        'name': 'Sarah Williams',
        'password': 'sarah789',
        'streak': 21,
        'quizzes_taken': 42,
        'tasks_done': 156
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        # Mock authentication (replace with real authentication)
        if email in users and users[email]['password'] == password:
            user = User(id=email, name=users[email]['name'])
            login_user(user, remember=remember)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        terms = request.form.get('terms')
        
        # Validation
        if not all([name, email, password, confirm_password]):
            flash('Please fill all required fields', 'error')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html')
        
        if not terms:
            flash('Please accept the terms and conditions', 'error')
            return render_template('signup.html')
        
        if email in users:
            flash('Email already registered', 'error')
            return render_template('signup.html')
        
        # Create user (in production, hash the password)
        users[email] = {
            'name': name,
            'password': password,
            'streak': 0,
            'quizzes_taken': 0,
            'tasks_done': 0
        }
        
        user = User(id=email, name=name)
        login_user(user)
        flash('Account created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('signup.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user_email = current_user.id
    user_data = users.get(user_email, {})
    
    if request.method == 'POST':
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('File uploaded successfully! Generating quiz...', 'success')
                # In a real app, you would process the file and generate a quiz
                return redirect(url_for('quiz'))
            else:
                flash('Invalid file type. Please upload PDF, DOCX, or TXT files.', 'error')
    
    return render_template('dashboard.html', 
                         user_name=current_user.name,
                         streak=user_data.get('streak', 0),
                         quizzes_taken=user_data.get('quizzes_taken', 0),
                         tasks_done=user_data.get('tasks_done', 0))

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    if request.method == 'POST':
        # Process quiz answers
        answers = {
            'q1': request.form.get('q1'),
            'q2': request.form.get('q2'),
            'q3': request.form.get('q3'),
            'q4': request.form.get('q4'),
            'q5': request.form.get('q5')
        }
        
        # Calculate score
        correct_answers = {'q1': 'q1a2', 'q2': 'q2a2', 'q3': 'q3a1', 'q4': 'q4a1', 'q5': 'q5a3'}
        score = sum(1 for q, a in answers.items() if a == correct_answers.get(q))
        
        # Update user stats
        user_email = current_user.id
        if user_email in users:
            users[user_email]['quizzes_taken'] = users[user_email].get('quizzes_taken', 0) + 1
        
        return jsonify({'score': score, 'total': len(correct_answers), 'percentage': int((score/len(correct_answers)) * 100)})
    
    return render_template('quiz.html')

@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    if request.method == 'POST':
        email = request.form.get('email')
        
        # In production, send actual reset email
        if email in users:
            flash('Password reset link sent to your email', 'success')
        else:
            # Don't reveal if email exists for security
            flash('If the email exists, a reset link has been sent', 'success')
        
        return redirect(url_for('login'))
    
    return render_template('forgotpassword.html')

@app.route('/profile')
@login_required
def profile():
    user_email = current_user.id
    user_data = users.get(user_email, {})
    
    return render_template('profile.html', 
                         user_name=current_user.name,
                         user_email=user_email,
                         streak=user_data.get('streak', 0),
                         quizzes_taken=user_data.get('quizzes_taken', 0),
                         tasks_done=user_data.get('tasks_done', 0))

@app.route('/updatepassword', methods=['GET', 'POST'])
@login_required
def updatepassword():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        user_email = current_user.id
        user_data = users.get(user_email)
        
        if user_data and user_data['password'] == current_password:
            if new_password == confirm_password:
                users[user_email]['password'] = new_password
                flash('Password updated successfully!', 'success')
                return redirect(url_for('profile'))
            else:
                flash('New passwords do not match', 'error')
        else:
            flash('Current password is incorrect', 'error')
    
    return render_template('updatepassword.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    print("Starting Focus Flow application...")
    print("Available routes:")
    print("  http://localhost:5000/ - Home page")
    print("  http://localhost:5000/login - Login")
    print("  http://localhost:5000/signup - Sign Up")
    print("  http://localhost:5000/dashboard - Dashboard")
    print("  http://localhost:5000/quiz - Quiz")
    print("  http://localhost:5000/profile - Profile")
    print("  http://localhost:5000/forgotpassword - Forgot Password")
    print("  http://localhost:5000/updatepassword - Update Password")
    
    app.run(debug=True, host='0.0.0.0', port=5000)