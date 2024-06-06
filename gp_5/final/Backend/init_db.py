import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('resumary.db')
cursor = conn.cursor()

# Create employee table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS employee (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT,
        skills TEXT,
        education TEXT,
        experience TEXT,
        mobile_number TEXT,
        is_project_manager INTEGER DEFAULT 0  -- Added is_project_manager column with default value 0 (False)
    )
''')
# Create Project table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS project (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        p_Name TEXT,
        PM_name TEXT,
        Description TEXT,
        id_Admin INTEGER,
        id_PM INTEGER,
        FOREIGN KEY (id_Admin) REFERENCES Admin(id),
        FOREIGN KEY (id_PM) REFERENCES employee(id)
    )
''')
# Create Tasks table if not exists with composite primary key
# the status has these values: [Not Started, In Progress, Completed]
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Tasks (
        id_project INTEGER,
        id_employee INTEGER,
        employee_name TEXT,
        Task_Name TEXT,
        start_date TEXT,
        end_date TEXT,
        status TEXT,
        PRIMARY KEY (id_project, id_employee),
        FOREIGN KEY (id_project) REFERENCES project(id),
        FOREIGN KEY (id_employee) REFERENCES employee(id)
    )
''')
# Create Tasks table if not exists with composite primary key
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Project_emp (
        id_project INTEGER,
        id_employee INTEGER,
        PRIMARY KEY (id_project, id_employee),
        FOREIGN KEY (id_project) REFERENCES project(id),
        FOREIGN KEY (id_employee) REFERENCES employee(id)
    )
''')
# Create Score table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Score (
        id_project INTEGER,
        id_employee INTEGER,
        T_Score INTEGER,
        PRIMARY KEY (id_project, id_employee),
        FOREIGN KEY (id_project) REFERENCES project(id),
        FOREIGN KEY (id_employee) REFERENCES employee(id)
    )
''')
# Create Admin table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT
    )
''')

# Commit changes and close connection
conn.commit()
conn.close()
