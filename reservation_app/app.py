from flask import Flask, render_template, request, redirect, url_for, session, flash
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# Path to your service account key file
SERVICE_ACCOUNT_FILE = '/Users/panjingyi/Documents/GitHub/reservation/reservation-427619-eb480d1a778c.json'

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

# The ID and range of your Google Sheet
SPREADSHEET_ID = '1ElTbBg6Zj-gOU-sBjaFMx7I_qEIhDKCFeSdr2i2H7bQ'
RANGE_NAME = 'Sheet1!A:D'  # Adjust the range as needed

@app.route('/')
def home():
    return render_template('customer.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Implement your user authentication logic here
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/book', methods=['POST'])
def book():
    name = request.form['name']
    email = request.form['email']
    datetime = request.form['datetime']
    guests = request.form['guests']

    # Append the reservation to Google Sheets
    values = [[name, email, datetime, guests]]
    body = {'values': values}
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption='RAW',
        body=body
    ).execute()

    return redirect(url_for('confirmation', name=name))

@app.route('/confirmation')
def confirmation():
    name = request.args.get('name')
    return render_template('confirmation.html', name=name)

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    # Fetch reservations from Google Sheets
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()
    reservations = result.get('values', [])

    return render_template('admin.html', reservations=reservations)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
