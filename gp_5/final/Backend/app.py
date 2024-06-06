import os
from flask import Flask, render_template, request, jsonify,session
from pyresparser import ResumeParser
from flask_cors import CORS
import sqlite3
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
from flask import Flask, request, jsonify
import nltk
from werkzeug.utils import secure_filename
import spacy



# Ensure you have downloaded the necessary NLTK data files
nltk.download('punkt')
nltk.download('stopwords') 

app = Flask(__name__)
app.secret_key = 'hahahaha'
CORS(app)  # Add this line to enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "http://localhost:5050"}})  # Allow requests from 'http://localhost:5000'
CORS(app, resources={r"/*": {"methods": "*"}})
CORS(app, supports_credentials=True, allow_headers=["Content-Type"])

nlp = spacy.load("en_core_web_sm")
# Define the directory to save uploaded resumes
upload_dir = 'upload_dir'  # Directory to save uploaded files
# Check if the directory exists, and create it if it doesn't
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir, exist_ok=True)

# Get the permissions of the directory
permissions = os.stat(upload_dir).st_mode

# Convert permissions to octal representation
octal_permissions = oct(permissions)[-3:]

print(f"Permissions of {upload_dir}: {octal_permissions}")


@app.route('/process_resume', methods=['POST'])
def process_resume():
    if 'cv' not in request.files:
        return jsonify({'error': 'No file uploaded'})

    resume_file = request.files['cv']
    if resume_file.filename == '':
        return jsonify({'error': 'No selected file'})

    # Create the upload directory if it does not exist
    os.makedirs(upload_dir, exist_ok=True)

    try:
        # Save the uploaded file temporarily
        upload_path = os.path.join(upload_dir, secure_filename(resume_file.filename))
        resume_file.save(upload_path)

        # Extract resume data
        extracted_data = ResumeParser(upload_path).get_extracted_data()

        # Delete the uploaded file after extraction
        os.remove(upload_path)

        # Get email and password from form data
        email = request.form.get('email')
        password = request.form.get('password')

        # Convert extracted data to appropriate formats
        skills = ', '.join(str(skill) for skill in extracted_data.get('skills', []))
        education = str(extracted_data.get('degree', ''))
        experience = str(extracted_data.get('experience', 0))
        mobile_number = str(extracted_data.get('mobile_number', ''))

        # Insert data into SQLite database
        conn = sqlite3.connect('resumary.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO employee (name, email, password, skills, education, experience, mobile_number, is_project_manager)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(extracted_data.get('name', '')),
            email,
            password,
            skills,
            education,
            experience,
            mobile_number,
            0  # Set is_project_manager to 0 (False) by default
        ))

        conn.commit()
        conn.close()

        # Return a JSON response
        return jsonify({'message': 'Employee added successfully!'})

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        conn = sqlite3.connect('resumary.db')
        cursor = conn.cursor()

        if 'admin' in email:
            table = 'admin'
            query = "SELECT id, email FROM admin WHERE email = ? AND password = ?"
        else:
            table = 'employee'
            query = "SELECT id, email, is_project_manager FROM employee WHERE email = ? AND password = ?"
        
        cursor.execute(query, (email, password))
        user = cursor.fetchone()

        if user:
            if 'admin' in email:
                user_id, user_email = user
                user_role = 'admin'
            else:
                user_id, user_email, is_project_manager = user
                user_role = 'project_manager' if is_project_manager else 'employee'

            session['user_id'] = user_id
            session['user_email'] = user_email
            session['logged_in'] = True

            if user_role == 'admin':
                session['admin_logged_in'] = True  # Save admin session
            else:
                session['admin_logged_in'] = False

            return jsonify({'status': 200, 'data': {'user_id': user_id, 'email': user_email, 'role': user_role}})
        else:
            return jsonify({'status': 401, 'message': 'Invalid credentials'})
    except Exception as e:
        print("Error during login:", str(e))
        return jsonify({'status': 500, 'message': 'Internal Server Error'})


@app.route('/logout', methods=['POST'])
def logout():
    try:
        # Clear session data for the user
        session.clear()

        return jsonify({'status': 200, 'message': 'Logout successful'})
    except Exception as e:
        print("Error during logout:", str(e))
        return jsonify({'status': 500, 'message': 'Internal Server Error'})



# Preprocess the new project description
def preprocess_text(text):
    # Tokenize the text
    tokens = word_tokenize(text)
    # Remove stop words
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word.lower() for word in tokens if word.lower() not in stop_words]
    # Join the filtered tokens back into a string
    processed_text = ' '.join(filtered_tokens)
    return processed_text

@app.route('/search', methods=['POST'])
def search_employees():
    # Get the project description and number of employees from the request form
    project_description = request.form['project_description']
    num_employees = int(request.form['num_employees'])

    # Preprocess the project description
    processed_description = preprocess_text(project_description)

    # Connect to your SQLite database
    conn = sqlite3.connect('resumary.db')
    cursor = conn.cursor()

    # Fetch relevant columns for all employees from the database
    cursor.execute("SELECT id, name, email, skills, education, experience FROM employee")
    employees = cursor.fetchall()

    if not employees:
        return jsonify({"message": "No employees found"}), 404

    # Initialize CountVectorizer
    count_vectorizer = CountVectorizer()

    # Combine project description with employee descriptions for fitting the vectorizer
    documents = [processed_description] + [preprocess_text(f"{emp[3]} {emp[4]} {emp[5]}") for emp in employees]

    # Fit and transform all documents
    X_all = count_vectorizer.fit_transform(documents)

    # Extract the vector for the project description
    X_project = X_all[0]

    # Calculate similarity between the project description and each employee's combined description
    similarity_scores = []
    for i, employee in enumerate(employees):
        X_employee = X_all[i + 1]  # Employee descriptions start from index 1
        similarity_score = cosine_similarity(X_project, X_employee)[0][0]
        similarity_scores.append((employee, similarity_score))

    # Sort employees by similarity score in descending order
    similarity_scores.sort(key=lambda x: x[1], reverse=True)

    # Define a threshold for similarity score
    similarity_threshold = 0.1  # Adjust this threshold based on your requirements

    # Select the top N employees from the sorted list if above the threshold
    best_employees = [score[0] for score in similarity_scores if score[1] >= similarity_threshold][:num_employees]

    # Close the database connection
    cursor.close()
    conn.close()

    if best_employees:
        # Return the best employees' details in the response
        response = {
            "employees": [
                {
                    "name": emp[1],  # Assuming name is in the 2nd column (index 1)
                    "email": emp[2],  # Assuming email is in the 3rd column (index 2)
                    "similarity_score": score[1]  # Include similarity score for reference
                }
                for emp, score in zip(best_employees, similarity_scores) if emp in best_employees
            ]
        }
        return jsonify(response)
    else:
        return jsonify({"message": "No suitable employee found"})



#CRUD ADMIN  ..............................................................
@app.route('/add_admin', methods=['POST'])
def add_admin():
    data = request.get_json()
    email = data['email']
    password = data['password']  # In a real application, ensure this password is hashed before storage

    # Check if 'admin' is in the email substring
    if 'admin' not in email:
        return jsonify({'status': 400, 'message': 'Invalid email for admin'})

    # Connect to SQLite database
    conn = sqlite3.connect('resumary.db')
    cursor = conn.cursor()

    # Insert new admin into the database
    try:
        cursor.execute("INSERT INTO admin (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        return jsonify({'status': 200, 'message': 'Admin added successfully'})
    except sqlite3.IntegrityError:
        return jsonify({'status': 400, 'message': 'Admin already exists'})
    finally:
        conn.close()

@app.route('/get_admin', methods=['GET'])
def get_admin():
    conn = sqlite3.connect('resumary.db')
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM Admin")  # Adjusted to select only the email column
    admins = cursor.fetchall()  # Fetch all emails as a list of tuples
    conn.close()
    
    admin_list = [{'email': admin[0]} for admin in admins]  # Extract emails from tuples
    
    if admin_list:
        return jsonify({'status': 200, 'data': admin_list})
    else:
        return jsonify({'status': 404, 'message': 'Admins not found'})


@app.route('/delete_admin', methods=['DELETE'])
def delete_admin():
    email = request.args.get('email')
    conn = sqlite3.connect('resumary.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM admin WHERE email = ?", (email,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    if rows_affected > 0:
        return jsonify({'status': 200, 'message': 'Admin deleted successfully'})
    else:
        return jsonify({'status': 404, 'message': 'Admin not found'})

@app.route('/update_admin', methods=['PUT'])
def update_admin():
    data = request.get_json()
    email = data['email']
    new_password = data['new_password']  # Ensure this password is hashed in a real application
    conn = sqlite3.connect('resumary.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE admin SET password = ? WHERE email = ?", (new_password, email))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    if rows_affected > 0:
        return jsonify({'status': 200, 'message': 'Admin password updated successfully'})
    else:
        return jsonify({'status': 404, 'message': 'Admin not found'})

#......................................................................................................................

#employeeees *************************************************************


@app.route('/get_employees', methods=['GET'])
def get_employees():
    conn = sqlite3.connect('resumary.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, email FROM employee")  # Adjust the query to select name and email columns
    employees = cursor.fetchall()  # Fetch all employees as a list of tuples
    conn.close()
    
    employee_list = [{'name': emp[0], 'email': emp[1]} for emp in employees]  # Extract name and email from tuples
    
    if employee_list:
        return jsonify({'status': 200, 'data': employee_list})
    else:
        return jsonify({'status': 404, 'message': 'Employees not found'})


@app.route('/add_task', methods=['POST'])
def add_task():
    # Connect to SQLite database
    conn = sqlite3.connect('resumary.db')
    cursor = conn.cursor()

    print('enter add task')
    data = request.json
    Task = data['Task']
    Assigned_to = data['Assigned_to']
    Start_Date = data['Start_Date']
    Due_Date = data['Due_Date']
    print('before getting the id')
    # Retrieve project ID from the query parameters
    project_id = request.args.get('projectID')
    userId= request.args.get('userId')
    print('after getting the id')
    print(project_id)
    
    

    # Insert task data into the Tasks table
    cursor.execute('''
        INSERT INTO Tasks (id_project, id_employee , employee_name , Task_Name, start_date, end_date, status)
        VALUES (?, ?, ?, ?, ?, ?,?)
    ''', (project_id, userId, Assigned_to, Task, Start_Date, Due_Date, 'Not Started'))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    # Return success message
    return jsonify({'status': 200, 'message': 'Task added successfully!'})


@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    # Connect to SQLite database
    conn = sqlite3.connect('resumary.db')
    cursor = conn.cursor()

    # Fetch tasks from the Tasks table
    cursor.execute('''
        SELECT id_project, id_employee,employee_name, Task_Name, start_date, end_date, status
        FROM Tasks
    ''')
    tasks = cursor.fetchall()

    # Close connection
    conn.close()

    # Convert tasks to JSON format
    tasks_json = []
    for task in tasks:
        tasks_json.append({
            'id_project': task[0],
            'id_employee': task[1],
            'employee_name': task[2],
            'Task_Name': task[3],
            'start_date': task[4],
            'end_date': task[5],
            'status': task[6]
        })

    # Return tasks as JSON response
    return jsonify({'tasks': tasks_json})

@app.route('/delete_all_tasks', methods=['DELETE'])
def delete_all_tasks():
    # Connect to SQLite database
    conn = sqlite3.connect('resumary.db')
    cursor = conn.cursor()

    # Delete all records from the Tasks table
    cursor.execute('''
        DELETE FROM Tasks
    ''')

    # Commit changes and close connection
    conn.commit()
    conn.close()

    # Return success message
    return jsonify({'status': 200, 'message': 'All tasks deleted successfully!'})

@app.route('/add_Project', methods=['POST'])
def add_Project():
    print('enter add_Project')
    data = request.json
    p_Name = data['p_Name']
    PM_name = data['PM_name']
    Description = data['Description']
    

    # Connect to SQLite database
    conn = sqlite3.connect('resumary.db')
    cursor = conn.cursor()

    # Insert task data into the Tasks table
    cursor.execute('''
        INSERT INTO project ( p_Name , PM_name, Description)
        VALUES (?, ?, ?)
    ''', (p_Name, PM_name, Description))
    print ('project added successfully')
    # Commit changes and close connection
    conn.commit()
    conn.close()

    # Return success message
    return jsonify({'status': 200, 'message': 'Task added successfully!'})

@app.route('/get_projects', methods=['GET'])
def get_projects():
    # Connect to SQLite database
    conn = sqlite3.connect('resumary.db')
    cursor = conn.cursor()

    # Fetch projects from the project table
    cursor.execute('''
        SELECT id, p_Name, PM_name
        FROM project
    ''')
    projects = cursor.fetchall()

    # Close connection
    conn.close()

    # Convert projects to JSON format
    projects_json = []
    for project in projects:
        projects_json.append({
            'id': project[0],
            'p_Name': project[1],
            'PM_name': project[2]
        })

    # Return projects as JSON response
    return jsonify({'projects': projects_json})

@app.route('/get_project_id', methods=['GET'])
def get_project_id():
    project_name = request.args.get('project_name')

    # Connect to SQLite database
    conn = sqlite3.connect('resumary.db')
    cursor = conn.cursor()

    # Fetch project ID based on the project name
    cursor.execute('''
        SELECT id FROM project WHERE p_Name = ?
    ''', (project_name,))
    project_id = cursor.fetchone()
    print(project_id)
    # Close connection
    conn.close()

    if project_id:
        return jsonify({'status': 200, 'project_id': project_id[0]})
    else:
        return jsonify({'status': 404, 'message': 'Project not found'})

if __name__ == '__main__':
    app.run(debug=False, port=5050)



