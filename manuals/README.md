# Igor

## Table of Contents

1. About
2. Installation
3. Operation
4. Development
5. AWS Settings

---


## 1. About
Igor was designed as a quick front-end to a simple cron-based script I generated to schedule the instance state of AWS fleets. The initial concept was to provide a web interface to manage the power-down/power-up of EC2 instances to try to provide additional cost-savings for a company or organisation.

EC2 instances are often left in a running state unwittingly by development teams in the busy daily activity which can lead to cost-bleed across your AWS accounts. Igor is designed to look across your EC2 instances for particular tags and then send shutdown/start-up commands as necessary.

Using a 9-5 business day schedule for 5 days a week, for exmaple, it is possible to save 128 hours of potential wasted compute resource. That can equate to a significant saving across the month and year. 

Igor is a fun, open-source way for you to start to get a handle on your fleet and begin saving money. The software is licensed under GNU GPL v2. A copy of the license is [included here](../LICENSE)

Why 'Igor'? - well, I'm a sucker for old B-movies and love Terry Pratchett books, Igor's are exceptionally down-to-earth people with a zero-waste mentality. Somewhere in my abstract mind, there's a humorously interesting correlation there! 

## 2. Installation
Igor can be run from your local machine, from a server/virtualised system or via docker for serverless style operation. 

### Running the software

{ Prerequisits: Installation of python 3 on your system and then running installation of the requirements. }

Activate your virtual environment:

```. .venv/bin/activate```

You can run your code for local use and testing with the simple command:

```python3 app.py```

( This is assuming your python installation is using python3 as the command to invoke python - this may be just 'python' on your installation )

You should see a few lines of code appear to tell you the service is running on your local IP , port 5000. You can now access the system using your web browser.

### Deploying via Docker

Igor can be run from docker and rebuilt as necessary after you have customised the code. 

**Building the Igor Docker Image**

```docker image build -t igor .```

**Running the Igor Docker Image**

If you have a docker image already available to you ( or you have just built your image ) you can launch that with the following command:

```docker run -p 5000:5000 -d igor```

## 3. Operation
Igor is accessed through your web browser on the port you have specified ( default is 5000 ).

The authentication screen is the first page you will be shown and will require you to enter the default credentials of *admin* and password *castle*.

Once you sign in you can reset your admin account password and generate more users in the settings page.

The settings page also provides the interface to set your AWS credentials to access your fleet with. See section 5 on **AWS settings** for best practice - do not use an administration account! 

## 4. Development
If you have modifications or want to take the project further, Igor can be forked as required and further developed by your local teams. 

You will require a range of packages installing for your python3 environment.

- pip
- flask
- flask_sqlalchemy

Sqlite is also used to hold certain data values ( which is bundled in Mac but will be an extra download on Windows ).

## 5. AWS Settings

Your Igor installation will require some credentials to be able to access your EC2 fleet. 

1. Generate a new user for your AWS account and specify NO CONSOLE ACCESS.
2. Create new CLI keys for the user and save these aside ( you will not be able to access them again ).
3. Create the following inline policy for your user permissions:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AutoStartStopPermissions",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:StartInstances",
                "ec2:StopInstances"
            ],
            "Resource": "*"
        }
    ]
}
```
4. Store your CLI key and secret in your Igor settings along with the region you want to monitor and the account ID.