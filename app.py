# from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
# from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
# from pymongo import MongoClient
# from bson.objectid import ObjectId
# import os
# from werkzeug.security import generate_password_hash, check_password_hash
# from werkzeug.utils import secure_filename
# from datetime import datetime
# import base64
# from db import get_db
# import PyPDF2
# from docx import Document
# import re
# from typing import List, Dict, Tuple
# # Get the absolute path to the project root
# basedir = os.path.abspath(os.path.dirname(__file__))

# app = Flask(__name__, 
#             template_folder=os.path.join(basedir, 'Templates', 'HTML'),
#             static_folder=os.path.join(basedir, 'Static'))
# app.secret_key = 'your-secret-key-here-change-in-production'
# app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'Static', 'uploads')
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# # Initialize Flask-Login
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'

# # MongoDB Atlas connection
# try:
#     db = get_db()
#     users_collection = db['users']
#     quizzes_collection = db['quizzes']
#     print("✓ MongoDB Atlas connection successful")
# except Exception as e:
#     print(f"✗ MongoDB connection failed: {e}")
#     print("Please check your MongoDB Atlas connection string in MONGO_URI")
#     db = None

# # User class (example)
# class User(UserMixin):
#     def __init__(self, id, name):
#         self.id = id
#         self.name = name

# # User loader
# @login_manager.user_loader
# def load_user(user_id):
#     # Replace with your user loading logic
#     return User(user_id, "Example User")

# # Allowed file extensions
# ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'}

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def extract_text_from_file(file_path: str, file_type: str) -> str:
#     """
#     Extract text from uploaded file based on file type.
#     Supports PDF, DOCX, TXT files.
#     """
#     try:
#         if file_type == 'pdf':
#             try:
#                 import PyPDF2
#                 with open(file_path, 'rb') as file:
#                     pdf_reader = PyPDF2.PdfReader(file)
#                     text = ""
#                     for page in pdf_reader.pages:
#                         text += page.extract_text()
#                     return text
#             except ImportError:
#                 return None
        
#         elif file_type == 'docx':
#             try:
#                 from docx import Document
#                 doc = Document(file_path)
#                 text = ""
#                 for para in doc.paragraphs:
#                     text += para.text + "\n"
#                 return text
#             except ImportError:
#                 return None
        
#         elif file_type == 'txt':
#             with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
#                 return file.read()
        
#         return None
#     except Exception as e:
#         print(f"Error extracting text: {e}")
#         return None

# def generate_questions_from_text(text: str, num_questions: int = 5) -> List[Dict]:
#     """
#     Generate multiple-choice questions from extracted text.
#     Returns a list of question dictionaries with answers.
#     """
#     if not text or len(text.strip()) == 0:
#         return None
    
#     # Clean and split text into sentences
#     sentences = re.split(r'[.!?]+', text)
#     sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
#     if len(sentences) < num_questions:
#         return None
    
#     questions = []
    
#     # Generate questions from selected sentences
#     import random
#     selected_sentences = random.sample(sentences, min(num_questions, len(sentences)))
    
#     for idx, sentence in enumerate(selected_sentences):
#         # Extract key terms and concepts
#         words = sentence.split()
        
#         if len(words) < 5:
#             continue
        
#         # Create question stem by selecting a key phrase
#         question_stem = sentence[:min(120, len(sentence))]
        
#         # Extract potential answers from the sentence
#         key_words = [w.strip('.,!?;:') for w in words if len(w) > 3]
        
#         if len(key_words) < 2:
#             continue
        
#         # Create question text
#         question_text = f"Based on the document, what is mentioned about: {question_stem}?"
        
#         # Create answer options
#         correct_answer = key_words[0]
        
#         # Generate plausible but incorrect alternatives
#         alternatives = []
#         for word in key_words[1:]:
#             if len(alternatives) < 3:
#                 alternatives.append(word)
        
#         # If we don't have enough alternatives, create generic ones
#         while len(alternatives) < 3:
#             alternatives.append(f"Option {len(alternatives) + 2}")
        
#         answers = [
#             {"id": f"q{idx+1}a1", "text": correct_answer, "is_correct": True},
#             {"id": f"q{idx+1}a2", "text": alternatives[0], "is_correct": False},
#             {"id": f"q{idx+1}a3", "text": alternatives[1], "is_correct": False},
#             {"id": f"q{idx+1}a4", "text": alternatives[2], "is_correct": False}
#         ]
        
#         # Shuffle answers
#         random.shuffle(answers)
        
#         # Find the correct answer ID after shuffle
#         correct_id = next(a["id"] for a in answers if a["is_correct"])
        
#         questions.append({
#             "question_number": idx + 1,
#             "question_text": question_text,
#             "answers": answers,
#             "correct_answer": correct_id,
#             "category": "Document-based"
#         })
    
#     return questions if len(questions) >= num_questions else None

# # Mock user data (replace with database in production)
# users = {
#     'test@example.com': {
#         'name': 'John Doe',
#         'password': 'password123',
#         'streak': 7,
#         'quizzes_taken': 12,
#         'tasks_done': 45
#     },
#     'alice@example.com': {
#         'name': 'Alice Smith',
#         'password': 'alice2024',
#         'streak': 14,
#         'quizzes_taken': 25,
#         'tasks_done': 89
#     },
#     'bob@example.com': {
#         'name': 'Bob Johnson',
#         'password': 'bobpass456',
#         'streak': 3,
#         'quizzes_taken': 5,
#         'tasks_done': 18
#     },
#     'sarah@example.com': {
#         'name': 'Sarah Williams',
#         'password': 'sarah789',
#         'streak': 21,
#         'quizzes_taken': 42,
#         'tasks_done': 156
#     }
# }

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         password = request.form.get('password')
#         remember = request.form.get('remember')
        
#         # Mock authentication (replace with real authentication)
#         if email in users and users[email]['password'] == password:
#             user = User(id=email, name=users[email]['name'])
#             login_user(user, remember=remember)
#             flash('Login successful!', 'success')
#             return redirect(url_for('dashboard'))
#         else:
#             flash('Invalid email or password', 'error')
    
#     return render_template('login.html')

# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         name = request.form.get('name')
#         email = request.form.get('email')
#         password = request.form.get('password')
#         confirm_password = request.form.get('confirm_password')
#         terms = request.form.get('terms')
        
#         # Validation
#         if not all([name, email, password, confirm_password]):
#             flash('Please fill all required fields', 'error')
#             return render_template('signup.html')
        
#         if password != confirm_password:
#             flash('Passwords do not match', 'error')
#             return render_template('signup.html')
        
#         if not terms:
#             flash('Please accept the terms and conditions', 'error')
#             return render_template('signup.html')
        
#         if db is None:
#             flash('Database connection error', 'error')
#             return render_template('signup.html')
        
#         # Check if email already exists in MongoDB
#         existing_user = users_collection.find_one({'email': email})
#         if existing_user:
#             flash('Email already registered', 'error')
#             return render_template('signup.html')
        
#         hashed_pw = generate_password_hash(password)
#         # Create user in MongoDB
#         user_data = {
#             'name': name,
#             'email': email,
#             'password': hashed_pw,  # In production, hash the password
#             'streak': 0,
#             'quizzes_taken': 0,
#             'tasks_done': 0,
#             'created_at': datetime.now(),
#             'files': []
#         }
        
#         result = users_collection.insert_one(user_data)
        
#         # Store user ID in session
#         session['user'] = str(result.inserted_id)
#         session['user_name'] = name
#         session['user_email'] = email
        
#         flash('Account created successfully!', 'success')
#         return redirect(url_for('dashboard'))
    
#     return render_template('signup.html')

# @app.route('/dashboard', methods=['GET', 'POST'])
# def dashboard():
#     if 'user' not in session:
#         flash('Please log in first', 'error')
#         return redirect(url_for('login'))
    
#     if db is None:
#         flash('Database connection error', 'error')
#         return redirect(url_for('index'))
    
#     # Fetch user data from MongoDB
#     try:
#         user_doc = users_collection.find_one({'_id': ObjectId(session['user'])})
#         if not user_doc:
#             flash('User not found', 'error')
#             return redirect(url_for('login'))
#     except:
#         flash('Invalid user session', 'error')
#         return redirect(url_for('login'))
    
#     if request.method == 'POST':
#         # Handle file upload
#         if 'file' in request.files:
#             file = request.files['file']
#             if file and file.filename != '' and allowed_file(file.filename):
#                 filename = secure_filename(file.filename)
#                 file_type = filename.rsplit('.', 1)[1].lower()
                
#                 # Save file temporarily to extract text
#                 temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#                 file.save(temp_file_path)
                
#                 # Extract text from file
#                 extracted_text = extract_text_from_file(temp_file_path, file_type)
                
#                 if extracted_text is None:
#                     flash('Error: Could not read the file. Please ensure it is a valid document.', 'error')
#                     try:
#                         os.remove(temp_file_path)
#                     except:
#                         pass
#                     return render_template('dashboard.html', 
#                                          user_name=session.get('user_name'),
#                                          streak=user_doc.get('streak', 0),
#                                          quizzes_taken=user_doc.get('quizzes_taken', 0),
#                                          tasks_done=user_doc.get('tasks_done', 0))
                
#                 if len(extracted_text.strip()) == 0:
#                     flash('Error: The uploaded file appears to be empty or unreadable.', 'error')
#                     try:
#                         os.remove(temp_file_path)
#                     except:
#                         pass
#                     return render_template('dashboard.html', 
#                                          user_name=session.get('user_name'),
#                                          streak=user_doc.get('streak', 0),
#                                          quizzes_taken=user_doc.get('quizzes_taken', 0),
#                                          tasks_done=user_doc.get('tasks_done', 0))
                
#                 # Generate questions from extracted text
#                 questions = generate_questions_from_text(extracted_text, num_questions=5)
                
#                 if questions is None:
#                     flash('Error: Could not generate questions from the document. Please upload a document with more content.', 'error')
#                     try:
#                         os.remove(temp_file_path)
#                     except:
#                         pass
#                     return render_template('dashboard.html', 
#                                          user_name=session.get('user_name'),
#                                          streak=user_doc.get('streak', 0),
#                                          quizzes_taken=user_doc.get('quizzes_taken', 0),
#                                          tasks_done=user_doc.get('tasks_done', 0))
                
#                 # Store file reference and questions in MongoDB
#                 file_data = {
#                     'filename': filename,
#                     'file_path': temp_file_path,
#                     'file_type': file_type,
#                     'extracted_text': extracted_text,
#                     'questions': questions,
#                     'uploaded_at': datetime.now()
#                 }
                
#                 # Update user document with the latest file and questions
#                 users_collection.update_one(
#                     {'_id': ObjectId(session['user'])},
#                     {
#                         '$set': {
#                             'current_file': file_data,
#                             'current_questions': questions
#                         }
#                     }
#                 )
                
#                 flash('File uploaded successfully! Quiz generated.', 'success')
#                 return redirect(url_for('quiz'))
#             else:
#                 flash('Invalid file type. Please upload PDF, DOCX, TXT, or image files.', 'error')
    
#     return render_template('dashboard.html', 
#                          user_name=session.get('user_name'),
#                          streak=user_doc.get('streak', 0),
#                          quizzes_taken=user_doc.get('quizzes_taken', 0),
#                          tasks_done=user_doc.get('tasks_done', 0))

# @app.route('/quiz', methods=['GET', 'POST'])
# def quiz():
#     if 'user' not in session:
#         flash('Please log in first', 'error')
#         return redirect(url_for('login'))
    
#     if db is None:
#         flash('Database connection error', 'error')
#         return redirect(url_for('index'))
    
#     # Fetch user document
#     try:
#         user_doc = users_collection.find_one({'_id': ObjectId(session['user'])})
#         if not user_doc:
#             flash('User not found', 'error')
#             return redirect(url_for('login'))
#     except:
#         flash('Invalid user session', 'error')
#         return redirect(url_for('login'))
    
#     # Check if user has generated questions
#     current_questions = user_doc.get('current_questions')
#     if not current_questions:
#         flash('No quiz generated yet. Please upload a document first.', 'error')
#         return redirect(url_for('dashboard'))
    
#     if request.method == 'POST':
#         # Process quiz answers
#         answers = {}
#         score = 0
#         total_questions = len(current_questions)
        
#         # Check answers against correct answers
#         for idx, question in enumerate(current_questions):
#             question_key = f'q{idx + 1}'
#             user_answer = request.form.get(question_key)
#             answers[question_key] = user_answer
            
#             # Check if answer is correct
#             if user_answer == question.get('correct_answer'):
#                 score += 1
        
#         # Calculate percentage
#         percentage = int((score / total_questions) * 100) if total_questions > 0 else 0
        
#         # Delete the quiz file from the uploads folder
#         try:
#             current_file = user_doc.get('current_file')
#             if current_file and 'file_path' in current_file:
#                 file_path = current_file['file_path']
#                 if os.path.exists(file_path):
#                     os.remove(file_path)
#         except Exception as e:
#             print(f"Error deleting file: {e}")
        
#         # Determine if user passed (60% or higher)
#         passing_score = 60
#         passed = percentage >= passing_score
        
#         # Update user stats in MongoDB
#         try:
#             update_fields = {'$inc': {'quizzes_taken': 1}}
            
#             # If user passed, increase streak and tasks_completed
#             if passed:
#                 update_fields['$inc']['streak'] = 1
#                 update_fields['$inc']['tasks_done'] = 1
            
#             # Unset current questions and file
#             update_fields['$unset'] = {'current_questions': '', 'current_file': ''}
            
#             users_collection.update_one(
#                 {'_id': ObjectId(session['user'])},
#                 update_fields
#             )
#         except Exception as e:
#             print(f"Error updating user stats: {e}")
        
#         return jsonify({
#             'score': score,
#             'total': total_questions,
#             'percentage': percentage,
#             'passed': passed
#         })
    
#     # GET request - render quiz with generated questions
#     return render_template('quiz.html', questions=current_questions)

# @app.route('/forgotpassword', methods=['GET', 'POST'])
# def forgotpassword():
#     if request.method == 'POST':
#         email = request.form.get('email')
        
#         if db is None:
#             flash('Database connection error', 'error')
#             return render_template('forgotpassword.html')
        
#         # Check if email exists in MongoDB
#         user = users_collection.find_one({'email': email})
        
#         # In production, send actual reset email
#         if user:
#             flash('Password reset link sent to your email', 'success')
#         else:
#             # Don't reveal if email exists for security
#             flash('If the email exists, a reset link has been sent', 'success')
        
#         return redirect(url_for('login'))
    
#     return render_template('forgotpassword.html')

# @app.route('/profile')
# @login_required
# def profile():
#     user_email = current_user.id
#     user_data = users.get(user_email, {})
    
#     return render_template('profile.html', 
#                          user_name=current_user.name,
#                          user_email=user_email,
#                          streak=user_data.get('streak', 0),
#                          quizzes_taken=user_data.get('quizzes_taken', 0),
#                          tasks_done=user_data.get('tasks_done', 0))

# @app.route('/updatepassword', methods=['GET', 'POST'])
# @login_required
# def updatepassword():
#     if request.method == 'POST':
#         current_password = request.form.get('current_password')
#         new_password = request.form.get('new_password')
#         confirm_password = request.form.get('confirm_password')
        
#         user_email = current_user.id
#         user_data = users.get(user_email)
        
#         if user_data and user_data['password'] == current_password:
#             if new_password == confirm_password:
#                 users[user_email]['password'] = new_password
#                 flash('Password updated successfully!', 'success')
#                 return redirect(url_for('profile'))
#             else:
#                 flash('New passwords do not match', 'error')
#         else:
#             flash('Current password is incorrect', 'error')
    
#     return render_template('updatepassword.html')

# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     flash('You have been logged out', 'info')
#     return redirect(url_for('index'))

# # Error handlers
# @app.errorhandler(404)
# def not_found(error):
#     return render_template('404.html'), 404

# @app.errorhandler(500)
# def internal_error(error):
#     return render_template('500.html'), 500

# if __name__ == '__main__':
#     # Create upload folder if it doesn't exist
#     if not os.path.exists(app.config['UPLOAD_FOLDER']):
#         os.makedirs(app.config['UPLOAD_FOLDER'])
    
#     print("Starting Focus Flow application...")
#     print("Available routes:")
#     print("  http://localhost:5000/ - Home page")
#     print("  http://localhost:5000/login - Login")
#     print("  http://localhost:5000/signup - Sign Up")
#     print("  http://localhost:5000/dashboard - Dashboard")
#     print("  http://localhost:5000/quiz - Quiz")
#     print("  http://localhost:5000/profile - Profile")
#     print("  http://localhost:5000/forgotpassword - Forgot Password")
#     print("  http://localhost:5000/updatepassword - Update Password")
    
#     app.run(debug=True, host='0.0.0.0', port=5000)

from focusflow import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
