
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Base de datos
DATABASE = 'data.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            email TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            description TEXT NOT NULL,
                            priority TEXT NOT NULL,
                            contact_id INTEGER,
                            FOREIGN KEY(contact_id) REFERENCES contacts(id))''')
        conn.commit()

# Ruta para la página de inicio de sesión
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            if user:
                return redirect(url_for('main_page'))
            else:
                flash('Usuario o contraseña incorrectos', 'error')
    return render_template('login.html')

# Ruta para la página de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                flash('Usuario registrado exitosamente', 'success')
                return redirect(url_for('login'))  # Redirige al inicio de sesión
        except sqlite3.IntegrityError:
            flash('El usuario ya existe', 'error')
    return render_template('register.html')

# Ruta para la página principal
@app.route('/main', methods=['GET', 'POST'])
def main_page():
    if request.method == 'POST':
        if 'contact_name' in request.form and 'contact_email' in request.form:
            name = request.form['contact_name']
            email = request.form['contact_email']
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO contacts (name, email) VALUES (?, ?)", (name, email))
                conn.commit()
        elif 'task_title' in request.form:
            title = request.form['task_title']
            description = request.form['task_description']
            priority = request.form['task_priority']
            contact_id = request.form.get('contact_id')
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO tasks (title, description, priority, contact_id) VALUES (?, ?, ?, ?)",
                                (title, description, priority, contact_id))
                conn.commit()
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts")
        contacts = cursor.fetchall()
        cursor.execute("SELECT tasks.id, tasks.title, tasks.priority, tasks.description, contacts.name FROM tasks LEFT JOIN contacts ON tasks.contact_id = contacts.id")
        tasks = cursor.fetchall()
    return render_template('pagina-principal.html', contacts=contacts, tasks=tasks)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
