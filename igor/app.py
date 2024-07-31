from flask import Flask, render_template, session, request, redirect, url_for, make_response
from markupsafe import escape
import os
import boto3
import configparser
import csv
import hashlib
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

# Load AWS Config from the file system settings
try:
    config = configparser.ConfigParser()
    config.read_file(open(r".awsconfig"))
    AWS_ACCOUNT_ID=config.get('AWS', 'AWS_ACCOUNT_ID')
    AWS_REGION=config.get('AWS', 'AWS_REGION')
    AWS_KEY=config.get('AWS', 'AWS_KEY')
    AWS_SECRET=config.get('AWS', 'AWS_SECRET')
except:
    AWS_ACCOUNT_ID=""
    AWS_REGION=""
    AWS_KEY=""
    AWS_SECRET=""

# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# change string to the name of your database; add path if necessary
db_name = 'igor.db'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, db_name)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# initialize the app with Flask-SQLAlchemy db
db.init_app(app)


# Set secret key for sessions
# This should be changed to a different item for each deployment
app.secret_key = b'8wefhsdfSELFWLi4fsefhbsd'


##################################################### MAIN AUTH AND HOMEPAGE
# Primary Route
@app.route('/')
def index():
    if 'username' in session:
        # Get EC2 instances in fleet
        client = boto3.client('ec2', aws_access_key_id = AWS_KEY, aws_secret_access_key = AWS_SECRET, region_name = AWS_REGION)
        response = client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:autostartstop',
                    'Values': [
                        '*',
                    ],
                }
            ],
        )
        rowcode=""
        for r in response['Reservations']:
            for i in r['Instances']:
                ThisInstance = i['InstanceId']
                InstanceState = i['State']['Name']
                for t in i['Tags']:
                    if t['Key'] == 'Name':
                        ThisName = t['Value']
                    if t['Key'] == 'autostartstop':
                        ThisTag = t['Value']
                # Populate another row in the table
                rowcode += "<tr><td>" + ThisInstance + "</td><td>" + ThisName + "</td><td>" + ThisTag + "</td><td></td><td>" + InstanceState + "</td><td></td></tr>"
        return render_template('index.html', mainTable=rowcode)
    else:
        return render_template('auth.html')




# AUTH ROUTE POINTS 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        okayAuth = checkAuth(request.form['username'],request.form['password'])
        if okayAuth == True:
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            session.pop('username', None)
            return render_template('auth.html',failmessage="Authentication Failure")
    else:
        return render_template('auth.html')



# Run authentication with local user file
def checkAuth(username,password):
    # Hash the string to SHA1
    hashstring = hashlib.sha1(password.encode()).hexdigest()
    try:
        with open('userList.conf', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['username'] == username:
                    if row['password'] == hashstring:
                        return True
                    else:
                        return False
                else:
                    return False
    except:
        return True


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('index'))


# Home Screen
def home():
    return render_template('index.html')



##################################################### SCHEDULES
# Display all Schedules
@app.route('/schedule')
def show_schedule():
    processInfo = ""
    myList = ""
    # Display the current schedules
    if 'username' in session:
        try:
            scheduleList = db.session.execute(db.select(schedules)
                    .order_by(schedules.scheduleName)).scalars()
            for item in scheduleList:
                myList += "<tr><td>" + item.scheduleName + "</td><td>" + item.scheduleDescription + "</td><td>" + item.scheduleStart + "</td><td>" + item.scheduleEnd  + "</td><td></td></tr>"
        except Exception as e:
            processInfo = str(e)
        return render_template('schedules.html',updateMessage=processInfo,scheduleTable=myList)
    else:
        return render_template('auth.html')
    

# Display Specific Schedule
@app.route('/schedule/<scheduleid>')
def show_specific_schedule():
    # Display the current schedules
    if 'username' in session:
        # Display the current groups
        try:
            scheduleList = db.session.execute(db.select(schedules)
                    .order_by(schedules.scheduleName)).scalars()
            for item in scheduleList:
                scheduleInfo += "<h3>" + item.scheduleName + "</h3><strong>" + item.scheduleStart + " to " + item.scheduleEnd + "</strong><p>" + item.scheduleDescription + "<br/><a href=\"/schedules/delete/" + str(item.scheduleid) + "\" class=\"button\">Delete</a></p>"
        except Exception as e:
            processInfo = str(e)
        return render_template('schedules.html',updateMessage=processInfo,groupTable=scheduleInfo)
    else:
        return render_template('auth.html')




##################################################### REPORTS
# Display Reports
@app.route('/reports')
def show_reports():
    # Display the current reports
    if 'username' in session:
        return render_template('reports.html',mainTable="")
    else:
        return render_template('auth.html')




##################################################### GROUPS
# Display Processing Groups
@app.route('/groups', methods=['GET', 'POST'])
def show_groups():
    processInfo = ""
    myGroupList = ""
    if 'username' in session:
        if request.method == "POST":
            groupname = request.form['groupname']
            groupdescription = request.form['groupdescription']
            record = groups(groupname,groupdescription)
            db.session.add(record)
            db.session.commit()
            updateMessage="Added group " + groupname
        # Display the current groups
        try:
            groupList = db.session.execute(db.select(groups)
                    .order_by(groups.groupname)).scalars()
            for item in groupList:
                myGroupList += "<tr><td>" + item.groupname + "</td><td>" + item.groupdescription + "</td><td><a href=\"/groups/delete/" + str(item.groupid) + "\" class=\"button\">Delete</a></td></tr>"
        except Exception as e:
            processInfo = str(e)
        return render_template('groups.html',updateMessage=processInfo,groupTable=myGroupList)
    else:
        return render_template('auth.html')

# Delete specific processing group
@app.route('/groups/delete/<groupid>', methods=['GET', 'POST'])
def delete_group(groupid):
    processInfo = ""
    myGroupList = ""
    if 'username' in session:
        if request.method == "POST":
            try:
                record = groups.query.filter_by(groupid=groupid).first()
                db.session.delete(record)
                db.session.commit()
                processInfo="Removed group " + request.form['groupname']
            except Exception as e:
                processInfo = str(e)
        else:
            # Display the current groups
            try:
                groupList = db.session.execute(db.select(groups)
                        .filter_by(groupid=groupid)
                        .order_by(groups.groupname)).scalars()
                for item in groupList:
                    myGroupList += "<tr><td><strong>" + item.groupname + "</strong><br/>" + item.groupdescription + "</td></tr><tr><td colspan=\"2\"><form action=\"/groups/delete/" + str(item.groupid) + "\" method=\"post\"><input type=\"hidden\" name=\"groupname\" value=\"" + str(item.groupname) + "\" /><input type=\"submit\" class=\"button\" value=\"Confirm\"></form></td></tr>"
            except Exception as e:
                processInfo = str(e)
        return render_template('groups_delete.html',updateMessage=processInfo,groupTable=myGroupList)
    else:
        return render_template('auth.html')




##################################################### SETTINGS

# Display Settings
@app.route('/settings', methods=['GET', 'POST'])
def show_settings():
    if 'username' in session:
        updatemsg = ""
        if request.method == 'POST':
            completeFileContents = "[AWS]\nAWS_ACCOUNT_ID = " + request.form['accountID'] + "\nAWS_REGION = " + request.form['region'] + "\nAWS_KEY = " + request.form['userkey'] + "\nAWS_SECRET = " + request.form['usersecret'] + "\n"
            # Save settings
            try:
                f = open(".awsconfig", "w")
                f.write(completeFileContents)
                f.close()
                updatemsg = "Settings Stored"
            except: 
                updatemsg = "Error Saving Settings"
        # Display the current settings
        # Load the user list
        userList = ""
        try:
            with open('userList.conf', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    userList += "<tr><td>" + row['username'] + "</td><td>" + row['fullname'] + "</td><td>" + row['status'] + "</td><td><a href=\"/users/modify/" + row['username'] + "\" class=\"button\">Modify</a> <a href=\"/users/delete/" + row['username'] + "\" class=\"button\">Delete</a></td></tr>"
        except:
            userList = "<tr><td colspan=3>-No user file-</td></tr>"
        return render_template('settings.html',accountID=AWS_ACCOUNT_ID, region=AWS_REGION, userkey=AWS_KEY, usersecret=AWS_SECRET, userList=userList,updatemsg=updatemsg)
    else:
        return render_template('auth.html')



################## Database Specification ##################

class groups(db.Model):
    __tablename__ = 'groups'
    groupid = db.Column(db.Integer, primary_key=True)
    groupname = db.Column(db.String)
    groupdescription = db.Column(db.String)

    def __init__(self,groupname,groupdescription):
        self.groupname = groupname
        self.groupdescription = groupdescription

class instances(db.Model):
    __tablename__ = 'instances'
    itemid = db.Column(db.Integer, primary_key=True)
    instanceid = db.Column(db.String)
    groupid = db.Column(db.Integer)

class schedules(db.Model):
    __tablename__ = 'schedules'
    scheduleid = db.Column(db.Integer, primary_key=True)
    scheduleName = db.Column(db.String)
    scheduleDescription = db.Column(db.String)
    scheduleStart = db.Column(db.String)
    scheduleEnd = db.Column(db.String)


############################################################




##################################################### APP SETUP

# Failure to load that page - throw a 404
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404

# Run the main system on port 5000
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)