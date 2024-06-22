from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Reservation model
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100), nullable=False)
    guests = db.Column(db.Integer, nullable=False)

# Dummy users for demonstration purposes
users = {
    'customer': 'customer123',
    'admin': 'admin123'
}

# Decorator to protect routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['logged_in'] = True
            session['username'] = username
            if username == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/index')
@login_required
def index():
    if session['username'] == 'admin':
        return redirect(url_for('admin'))
    return render_template('index.html')

@app.route('/book', methods=['POST'])
@login_required
def book():
    if session['username'] == 'admin':
        return redirect(url_for('admin'))
    name = request.form['name']
    email = request.form['email']
    date = request.form['date']
    time = request.form['time']
    guests = request.form['guests']
    
    # Save the reservation
    new_reservation = Reservation(name=name, email=email, date=date, time=time, guests=guests)
    db.session.add(new_reservation)
    db.session.commit()
    
    return redirect(url_for('confirmation', name=name))

@app.route('/confirmation')
@login_required
def confirmation():
    if session['username'] == 'admin':
        return redirect(url_for('admin'))
    name = request.args.get('name')
    return render_template('confirmation.html', name=name)

@app.route('/admin')
@login_required
def admin():
    if session['username'] != 'admin':
        return redirect(url_for('index'))
    reservations = Reservation.query.all()
    return render_template('admin.html', reservations=reservations)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
