from flask import Flask, render_template, session, request, redirect, url_for, make_response
from markupsafe import escape
import os

app = Flask(__name__)

# Set secret key for sessions
# This should be changed to a different item for each deployment
app.secret_key = b'8wefhsdfSELFWLi4fsefhbsd'

# Primary Route
@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html')
    else:
        return render_template('auth.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    else:
        return render_template('auth.html')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))



def home():
    # Get EC2 instances in fleet
    return render_template('index.html')

# Display all Schedules
@app.route('/schedules')
def show_schedules():
    # Display the current schedules
    if 'username' in session:
        # Display the current groups
        return render_template('schedules.html')
    else:
        return render_template('auth.html')
    

# Display Specific Schedule



# Display Processing Groups
@app.route('/groups')
def show_groups():
    if 'username' in session:
        # Display the current groups
        return render_template('groups.html')
    else:
        return render_template('auth.html')

# Display specific processing group



# Failure to load that page - throw a 404
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404

# Run the main system on port 5000
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)