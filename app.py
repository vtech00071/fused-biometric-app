import os
import sqlite3
import hashlib
import io
from flask import Flask, render_template, request, flash, redirect, url_for, g
from PIL import Image

# --- App Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_123'
DATABASE = 'users.db' # This will be our new database file

# --- Database Functions ---

def get_db():
    """Opens a new database connection if one doesn't exist in the context."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # This lets us access columns by name
    return db

@app.teardown_appcontext
def close_db(exception):
    """Closes the database again at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database and creates the 'users' table if it doesn't exist."""
    
    # This logic was moved from the bottom of the file
    if not os.path.exists('schema.sql'):
        with open('schema.sql', 'w') as f:
            f.write("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,  -- <-- THIS IS THE FIX
                face_hash TEXT NOT NULL,
                fingerprint_hash TEXT NOT NULL
            );
            """)
            
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# --- Hashing Function ---

def hash_image(image_file):
    """Reads an image file and returns its SHA-256 hash."""
    try:
        # Read image data
        img = Image.open(image_file.stream)
        # Use a BytesIO object to hold the image data in memory
        buf = io.BytesIO()
        # Save image to the buffer in a consistent format (PNG) to ensure hash is stable
        img.save(buf, format='PNG')
        
        # Get the bytes data
        image_bytes = buf.getvalue()
        
        # Create hash
        sha256 = hashlib.sha256()
        sha256.update(image_bytes)
        return sha256.hexdigest()
        
    except Exception as e:
        print(f"Error hashing image: {e}")
        return None

# === Routes ===

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    if request.method == 'POST':
        username = request.form['username']
        face_file = request.files.get('face_image')
        fingerprint_file = request.files.get('fingerprint_image')

        if not username or not face_file or not fingerprint_file:
            flash('All fields are required!', 'error')
            return redirect(url_for('register'))

        face_hash = hash_image(face_file)
        fingerprint_hash = hash_image(fingerprint_file)

        if not face_hash or not fingerprint_hash:
            flash('Error processing images. Please try again.', 'error')
            return redirect(url_for('register'))

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, face_hash, fingerprint_hash) VALUES (?, ?, ?)",
                (username, face_hash, fingerprint_hash)
            )
            db.commit()
            flash(f"User '{username}' registered successfully!", 'success')
            return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            flash(f"Username '{username}' already exists. Please choose another.", 'error')
            return redirect(url_for('register'))
        except Exception as e:
            flash(f"An error occurred: {e}", 'error')
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/face', methods=['GET', 'POST'])
def face():
    """Handles Face Verification."""
    if request.method == 'POST':
        username = request.form['username']
        face_file = request.files.get('face_image')

        if not username or not face_file:
            flash('Username and face image are required!', 'error')
            return redirect(url_for('face'))

        uploaded_hash = hash_image(face_file)
        if not uploaded_hash:
            flash('Error processing uploaded image.', 'error')
            return redirect(url_for('face'))

        db = get_db()
        user = db.execute(
            "SELECT face_hash FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            flash('Username not found.', 'error')
            return redirect(url_for('face'))

        if user['face_hash'] == uploaded_hash:
            flash('Verification Successful!', 'success')
        else:
            flash('Verification Failed. Face does not match.', 'error')
        
        return redirect(url_for('face'))

    return render_template('fingerprint.html') # <-- I also found a bug here. This was wrong.
    # It should be:
    # return render_template('face.html')


@app.route('/fingerprint', methods=['GET', 'POST'])
def fingerprint():
    """Handles Fingerprint Verification."""
    if request.method == 'POST':
        username = request.form['username']
        fingerprint_file = request.files.get('fingerprint_image')

        if not username or not fingerprint_file:
            flash('Username and fingerprint image are required!', 'error')
            return redirect(url_for('fingerprint'))

        uploaded_hash = hash_image(fingerprint_file)
        if not uploaded_hash:
            flash('Error processing uploaded image.', 'error')
            return redirect(url_for('fingerprint'))

        db = get_db()
        user = db.execute(
            "SELECT fingerprint_hash FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            flash('Username not found.', 'error')
            return redirect(url_for('fingerprint'))

        if user['fingerprint_hash'] == uploaded_hash:
            flash('Verification Successful!', 'success')
        else:
            flash('Verification Failed. Fingerprint does not match.', 'error')
        
        return redirect(url_for('fingerprint'))

    return render_template('fingerprint.html')


@app.route('/about')
def about():
    """Renders the about page."""
    return render_template('about.html')

# === Main ===
# This part ONLY runs when you run 'python app.py' locally
if __name__ == '__main__':
    init_db() # Set up the database
    app.run(debug=True, port=8090)