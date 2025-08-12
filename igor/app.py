from flask import Flask, render_template, session, request, redirect, url_for, make_response
from markupsafe import escape
import os
import boto3
import configparser
import csv
import hashlib
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import datetime
from datetime import datetime as dt

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
        rowCount=0
        for r in response['Reservations']:
            for i in r['Instances']:
                ThisTag = ""
                ThisName = ""
                groupName = ""
                scheduleName = ""
                thisscheduleid = ""
                MyInstanceState = ""
                ThisInstance = i['InstanceId']
                InstanceState = i['State']['Name']
                if InstanceState == "stopped":
                    MyInstanceState = "<a title=\"Stopped\" alt=\"Stopped\">&#9940;</a>"
                if InstanceState == "running":
                    MyInstanceState = "<a title=\"Running\" alt=\"Running\">&#128250;</a>"

                for t in i['Tags']:
                    if t['Key'] == 'Name':
                        ThisName = t['Value']
                    if t['Key'] == 'autostartstop':
                        ThisTag = t['Value']
                groupName = ""
                mygroupList = db.session.execute(db.select(groups)
                    .filter_by(groupname=ThisTag)).scalars()
                for mygroupitem in mygroupList:
                    groupName = mygroupitem.groupname
                    thisscheduleid = mygroupitem.scheduleid
                myscheduleList = db.session.execute(db.select(schedules)
                    .filter_by(scheduleid=thisscheduleid)).scalars()
                for myscheduleitem in myscheduleList:
                    scheduleName = myscheduleitem.scheduleName
                # Populate another row in the table
                rowcode += "<tr><td>" + ThisInstance + "</td><td>" + ThisName + "</td><td>" + ThisTag + "</td><td>" + groupName + "</td><td>" + scheduleName + "</td><td align=\"center\">" + MyInstanceState + "</td></tr>"
                rowCount += 1
        return render_template('index.html', mainTable=rowcode, instanceCount=rowCount)
    else:
        return render_template('auth.html',imgBox="img/igor_128_anim.gif")




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
            return render_template('auth.html',failmessage="I do not recognise your paperwork, traveller.",imgBox="img/closedDoor_anim.gif")
    else:
        return render_template('auth.html',imgBox="img/igor_128_anim.gif")



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
@app.route('/schedule', methods=['GET', 'POST'])
def show_schedule():
    processInfo = ""
    myList = ""
    # Display the current schedules
    if 'username' in session:
        if request.method == "POST":
            schedulename = request.form['schedulename']
            scheduledescription = request.form['scheduledescription']
            starttime = request.form['schedulestart']
            endtime = request.form['scheduleend']
            scheduleDays = request.form['scheduledays']
            record = schedules(schedulename,scheduledescription,starttime,endtime,scheduleDays)
            db.session.add(record)
            db.session.commit()
            updateMessage="Added Schedule \"" + schedulename + "\""
        # Display current schedules
        try:
            scheduleList = db.session.execute(db.select(schedules)
                .order_by(schedules.scheduleName)).scalars()
            for item in scheduleList:
                myList += "<tr><td>" + item.scheduleName + "</td><td>" + item.scheduleDescription + "</td><td>" + item.scheduleStart + "</td><td>" + item.scheduleEnd + "</td><td>" + item.scheduleDays + "</td><td><a href=\"/schedule/" + str(item.scheduleid) + "\" class=\"button\">View</a></td></tr>"
        except Exception as e:
            processInfo = str(e)
        return render_template('schedules.html',updateMessage=processInfo,scheduleTable=myList)
    else:
        return render_template('auth.html')
    

# Display Specific Schedule
@app.route('/schedule/<scheduleid>')
def show_specific_schedule(scheduleid):
    scheduleInfo=""
    processInfo=""
    # Display the current schedules
    if 'username' in session:
        # Display the current groups
        try:
            scheduleList = db.session.execute(db.select(schedules)
                    .filter_by(scheduleid=scheduleid)
                    .order_by(schedules.scheduleName)).scalars()
            for item in scheduleList:
                scheduleInfo += "<h3>Schedule: " + item.scheduleName + "</h3><p><strong>" + item.scheduleStart + " to " + item.scheduleEnd + "</strong><br/>Days: " + item.scheduleDays + "</p><p>" + item.scheduleDescription + "<br/><a href=\"/schedule/delete/" + str(item.scheduleid) + "\" class=\"button\">Delete</a></p>"
        except Exception as e:
            processInfo = str(e)
        return render_template('schedules_view.html',updateMessage=processInfo,scheduleInfo=scheduleInfo)
    else:
        return render_template('auth.html')


# Delete specific schedule
@app.route('/schedule/delete/<scheduleid>', methods=['GET', 'POST'])
def delete_schedule(scheduleid):
    processInfo = ""
    myScheduleList = ""
    if 'username' in session:
        if request.method == "POST":
            try:
                record = schedules.query.filter_by(scheduleid=scheduleid).first()
                db.session.delete(record)
                db.session.commit()
                processInfo="Removed schedule \"" + request.form['schedulename'] + "\""
            except Exception as e:
                processInfo = str(e)
        else:
            # Display the current schedules
            try:
                groupList = db.session.execute(db.select(schedules)
                        .filter_by(scheduleid=scheduleid)
                        .order_by(schedules.scheduleName)).scalars()
                for item in groupList:
                    myScheduleList += "<tr><td><strong>" + item.scheduleName + "</strong><br/>" + item.scheduleDescription + "</td></tr><tr><td colspan=\"2\"><form action=\"/schedule/delete/" + str(item.scheduleid) + "\" method=\"post\"><input type=\"hidden\" name=\"schedulename\" value=\"" + str(item.scheduleName) + "\" /><input type=\"submit\" class=\"button\" value=\"Confirm\"></form></td></tr>"
            except Exception as e:
                processInfo = str(e)
        return render_template('schedules_delete.html',updateMessage=processInfo,scheduleTable=myScheduleList)
    else:
        return render_template('auth.html')
    



##################################################### REPORTS
# Display Reports
@app.route('/reports')
def show_reports():
    # Display the current reports
    if 'username' in session:
        return render_template('reports.html')
    else:
        return render_template('auth.html')

@app.route('/reports/instances')
def show_reports_instances():
    # Display all the instances that are in the AWS account
    if 'username' in session:
        client = boto3.client('ec2', aws_access_key_id = AWS_KEY, aws_secret_access_key = AWS_SECRET, region_name = AWS_REGION)
        response = client.describe_instances()
        tableData=""
        for r in response['Reservations']:
            ThisManaged = ''
            for i in r['Instances']:
                ThisManaged = '&#128721;'
                ThisInstance = i['InstanceId']
                InstanceState = i['State']['Name']
                InstanceType = i['InstanceType']
                for t in i['Tags']:
                    if t['Key'] == 'Name':
                        ThisName = t['Value']
                    if t['Key'] == 'autostartstop':
                        if t['Value'] != 'disabled':
                            ThisManaged = '&#9989;'
                # Populate another row in the table
                tableData += "<tr><td>" + ThisInstance + "</td><td>" + ThisName + "</td><td>" + InstanceType + "</td><td>" + InstanceState + "</td><td align=\"center\">" + ThisManaged + "</td></tr>"
        return render_template('reports_instances.html',mainTable=tableData)
    else:
        return render_template('auth.html')

@app.route('/reports/tagged')
def show_reports_tagged():
    # Display the instances tagged with 'autostartstop'
    if 'username' in session:
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
        tableData=""
        for r in response['Reservations']:
            for i in r['Instances']:
                ThisInstance = i['InstanceId']
                InstanceState = i['State']['Name']
                InstanceType = i['InstanceType']
                for t in i['Tags']:
                    if t['Key'] == 'Name':
                        ThisName = t['Value']
                    if t['Key'] == 'autostartstop':
                        ThisTag = t['Value']
                # Populate another row in the table
                tableData += "<tr><td>" + ThisInstance + "</td><td>" + ThisName + "</td><td>" + InstanceType + "</td><td>" + ThisTag + "</td><td>" + InstanceState + "</td></tr>"
        return render_template('reports_tagged.html',mainTable=tableData)
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
            scheduleid = request.form['schedule']
            record = groups(groupname,groupdescription,scheduleid)
            db.session.add(record)
            db.session.commit()
            updateMessage="Added group " + groupname
        # Display the current groups
        try:
            # Get the group list
            groupList = db.session.execute(db.select(groups)
                    .order_by(groups.groupname)).scalars()
            for item in groupList:
                scheduleName = ""
                myscheduleList = db.session.execute(db.select(schedules)
                    .filter_by(scheduleid=item.scheduleid)).scalars()
                for myscheduleitem in myscheduleList:
                    scheduleName = myscheduleitem.scheduleName
                myGroupList += "<tr><td>" + item.groupname + "</td><td>" + item.groupdescription + "</td><td>" + scheduleName + "</td><td><a href=\"/groups/edit/" + str(item.groupid) + "\" class=\"groupbutton\">Edit</a>  <a href=\"/groups/delete/" + str(item.groupid) + "\" class=\"groupbutton\">Delete</a> <a href=\"/groups/start/" + str(item.groupid) + "\" class=\"groupbutton\">Start Group</a> <a href=\"/groups/stop/" + str(item.groupid) + "\" class=\"groupbutton\">Stop Group</a></td></tr>"
            # Populate the Schedule Drop-Down Menu
            scheduleMenu = ""
            scheduleList = db.session.execute(db.select(schedules)
                .order_by(schedules.scheduleName)).scalars()
            for scheduleitem in scheduleList:
                scheduleMenu += "<option value=\"" + str(scheduleitem.scheduleid) + "\">" + scheduleitem.scheduleName + "</opion>"
        except Exception as e:
            processInfo = str(e)
        return render_template('groups.html',updateMessage=processInfo,groupTable=myGroupList,scheduleDropdown=scheduleMenu)
    else:
        return render_template('auth.html')

# EDIT GROUP INFORMATION
@app.route('/groups/edit/<groupid>', methods=['GET', 'POST'])
def edit_groups(groupid):
    processInfo = ""
    myGroupName = ""
    myGroupDescription = ""
    myGroupSchedule = ""
    if 'username' in session:
        if request.method == "POST":
            groupname = request.form['groupname']
            groupdescription = request.form['groupdescription']
            scheduleid = request.form['schedule']
            group = groups.query.get(groupid)
            group.groupname = groupname
            group.groupdescription = groupdescription
            group.scheduleid = scheduleid
            db.session.commit()
            updateMessage="Saved group " + groupname
        # Display the current groups
        try:
            # Get the group list
            groupList = db.session.execute(db.select(groups)
                .filter_by(groupid=groupid)
                .order_by(groups.groupname)).scalars()
            for item in groupList:
                myGroupName = item.groupname
                myGroupDescription = item.groupdescription 
                myGroupSchedule = item.scheduleid
                # Populate the Schedule Drop-Down Menu
            scheduleMenu = ""
            scheduleList = db.session.execute(db.select(schedules)
                .order_by(schedules.scheduleName)).scalars()
            for scheduleitem in scheduleList:
                if scheduleitem.scheduleid == myGroupSchedule:
                    scheduleMenu += "<option value=\"" + str(scheduleitem.scheduleid) + "\" selected=\"selected\">* " + scheduleitem.scheduleName + "</opion>"
                else:
                    scheduleMenu += "<option value=\"" + str(scheduleitem.scheduleid) + "\">" + scheduleitem.scheduleName + "</opion>"
        except Exception as e:
            processInfo = str(e)
        return render_template('groups_edit.html',updateMessage=processInfo,groupName=myGroupName,groupDescription=myGroupDescription,groupid=groupid,scheduleDropdown=scheduleMenu)
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
                processInfo="Removed group \"" + request.form['groupname'] + "\""
            except Exception as e:
                processInfo = str(e)
            
            # Get the group list
            groupList = db.session.execute(db.select(groups)
                    .order_by(groups.groupname)).scalars()
            for item in groupList:
                scheduleName = ""
                myscheduleList = db.session.execute(db.select(schedules)
                    .filter_by(scheduleid=item.scheduleid)).scalars()
                for myscheduleitem in myscheduleList:
                    scheduleName = myscheduleitem.scheduleName
                    myGroupList += "<tr><td>" + item.groupname + "</td><td>" + item.groupdescription + "</td><td>" + scheduleName + "</td><td><a href=\"/groups/delete/" + str(item.groupid) + "\" class=\"button\">Delete</a></td></tr>"
            # Populate the Schedule Drop-Down Menu
            scheduleMenu = ""
            scheduleList = db.session.execute(db.select(schedules)
                .order_by(schedules.scheduleName)).scalars()
            for scheduleitem in scheduleList:
                scheduleMenu += "<option value=\"" + str(scheduleitem.scheduleid) + "\">" + scheduleitem.scheduleName + "</opion>"
            return render_template('groups.html',updateMessage=processInfo,groupTable=myGroupList,scheduleDropdown=scheduleMenu)
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




########################### MANUAL START / STOP OF GROUP MACHINES 

# Start Instances in a group
@app.route('/group/start', methods=['GET'])
def start_group_instances():
    if 'username' in session:
        updatemsg = ""
        # Check group details
        try:
            groupList = db.session.execute(db.select(groups)
                .filter_by(groupid=groupid)
                .order_by(groups.groupname)).scalars()
            for item in groupList:
                # Fire off the group process
                response = changeGroupState(item.groupname,'start')
            updatemsg += response
        except Exception as e:
            updatemsg += str(e)
        return render_template('groups.html',updatemsg=updatemsg)
    else:
        return render_template('auth.html')


# Stop all Instances in a group
@app.route('/group/stop', methods=['GET'])
def stop_group_instances():
    if 'username' in session:
        updatemsg = ""
        # Check group details
        try:
            groupList = db.session.execute(db.select(groups)
                .filter_by(groupid=groupid)
                .order_by(groups.groupname)).scalars()
            for item in groupList:
                # Fire off the group process
                response = changeGroupState(item.groupname,'stop')
            updatemsg += response
        except Exception as e:
            updatemsg += str(e)
        return render_template('groups.html',updatemsg=updatemsg)
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
    scheduleid = db.Column(db.Integer)

    def __init__(self,groupname,groupdescription,scheduleid):
        self.groupname = groupname
        self.groupdescription = groupdescription
        self.scheduleid = scheduleid

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
    scheduleDays = db.Column(db.String)
    
    def __init__(self,scheduleName,scheduleDescription,scheduleStart,scheduleEnd,scheduleDays):
        self.scheduleName = scheduleName
        self.scheduleDescription = scheduleDescription
        self.scheduleStart = scheduleStart
        self.scheduleEnd = scheduleEnd
        self.scheduleDays = scheduleDays


############################################################



################## BACKEND ADMIN PROCESSES #############################


######### RUN INSTANCE CONTROL FOR A PARTICULAR TAG ##########
@app.route('/cronjobs', methods=['GET'])
def checkGroupMembers():
    cronOutput=""
    # Get the Date Time
    today = datetime.datetime.today()
    dayOfWeek = today.weekday()
    # Get the current time
    nowtime = dt.now().strftime('%H:%M')
    # For each item in the known groups
    try:
        groupName = ""
        # For every group member
        groupList = db.session.execute(db.select(groups)
                    .order_by(groups.groupname)).scalars()
        for item in groupList:
            scheduleName = ""
            scheduleStart = ""
            scheduleEnd = ""
            scheduleDays = ""
            groupName = item.groupname
            myscheduleList = db.session.execute(db.select(schedules)
                .filter_by(scheduleid=item.scheduleid)).scalars()
            for myscheduleitem in myscheduleList:
                stateChange = ""
                scheduleStart = myscheduleitem.scheduleStart
                scheduleEnd = myscheduleitem.scheduleEnd
                scheduleDays = myscheduleitem.scheduleDays
                scheduleName = myscheduleitem.scheduleName
                # Check the day from the list
                if scheduleDays[dayOfWeek] == "x":
                    # Check the launch time
                    # If now time matches the startup time then fire the process
                    cronOutput += scheduleName + " : " + scheduleStart + " : " + scheduleEnd + " : -Scheduled day- <br/>"
                    if str(nowtime) == str(scheduleStart):
                        cronOutput += "Schedule " + scheduleName + " [START]<br/>"
                        stateChange = changeGroupState(groupName,"start")                    
                    if str(nowtime) == str(scheduleEnd):
                        cronOutput += "Schedule " + scheduleName + " [STOP]<br/>"
                        stateChange = changeGroupState(groupName,"stop")
                    cronOutput += stateChange
                else:
                    cronOutput += scheduleName + " : " + scheduleStart + " : " + scheduleEnd + " : -Not a scheduled day- <br/>"
    except Exception as e:
        # Error out
        logMessage = "ERROR! " + str(e)
        exit(1)
    return render_template('cron.html',cronOutputMessage=cronOutput)

    
# Startup or Shutdown instances in the group specified
def changeGroupState(groupName,stateMode):
    myclient = boto3.client('ec2', aws_access_key_id = AWS_KEY, aws_secret_access_key = AWS_SECRET, region_name = AWS_REGION)
    response = myclient.describe_instances()
    logMessage = ""
    instanceCounter = 0
    for r in response['Reservations']:
        for i in r['Instances']:
            ThisInstance = i['InstanceId']
            InstanceState = i['State']['Name']
            for t in i['Tags']:
                if t['Key'] == 'Name':
                    ThisName = t['Value']
                if t['Key'] == 'autostartstop':
                    if t['Value'] == groupName:
                        instanceCounter += 1
                        # Launch instances with the tag
                        if stateMode == "start":
                            logMessage += "Changing State for " + ThisInstance + " to " + stateMode + "<br/>"
                            response = myclient.start_instances(
                                InstanceIds=[
                                    ThisInstance,
                                ]
                            )
                            # logMessage += response
                        else:
                            if InstanceState != "stopped":
                                logMessage += "Changing State for " + ThisInstance + " to " + stateMode + "<br/>"
                                response = myclient.stop_instances(
                                    InstanceIds=[
                                        ThisInstance,
                                    ], 
                                    Force=True
                                )
                                # logMessage += response
                            else:
                                logMessage += "Instance " + ThisInstance + " already stopped - no action taken<br/>"
    logMessage += str(instanceCounter) + " instances<br/>"
    return logMessage


##################################################### APP SETUP

# Failure to load that page - throw a 404
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404

# Run the main system on port 5000
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)