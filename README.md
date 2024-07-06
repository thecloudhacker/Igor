# Igor 

![igor](./igor/static/img/igor_128_anim.gif)

"Yeth, mathtur...! What ith thy bidding?"

## Description 

![igor](./igor/static/img/igor_32_anim.gif) An automated AWS Caretaker, Igor does thy bidding by blowing the candles out at night and lighting the fires in the morning. He produces all the necessary ~~shavings~~ er, savings on costs...

With a mixture of front-end web interface and back-end comms scripts, Igor is able to keep a watch on your AWS estate and turn off the electric generators if calculatory activities are not requried.

---

## Operation

**Igor, clean up this mess!?**

---

## Deployment

**Igor, go forth and replicate thyself!**

Igor is designed to be deployed in your own environment, be that your residential castle, your industrial complex or on the Ether. 

### Development machine
Igor utilises Python and Flask to operate. Installation requirements for pip are stored in the requirements.txt file. To install those run: 

`pip install -r requirements.txt`

If you change and add to any of the libraries, be sure to add those to the requirements.txt file or run:

`pip freee > requirements.txt`

Rebuilding the Docker image:

`docker image build -t igor_docker .`

Run the Docker container:

`docker run -p 5000:5000 -d igor_docker`

### Deployment of service

Igor can be deloyed locally for development testing or to dedicated resource.

Docker Launch:

`docker run igor`

---


## Instructions

**Igor, how in the name of Frankenstein do you work?**

### Configuring AWS connection

1. Create an IAM user for Igor and provide CLI access only.
2. Specify Permissions:
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
3. Add CLI keys to Igor's settings


### Setting up Schedules

Schedules must be generated first in order to set times for turning systems on/off.

### Adding instances to schedule groups

Once you have generated schedules, you can generate groups of instances 

### Enabling automation

Once you have groups of instanes assigned to schedules, you can turn the automation on or off using the web interface.

### Manual Control

You can manually operate tasks on a group by selecting the group and using the context menu to underake your operation.

---

## License

Licensed under GNU GPL v2, a copy of this is included [here](LICENSE)

Igor, an AWS automated Caretaker.
    Copyright (C) 2024  R. Trotter

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
