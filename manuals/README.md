# Igor

## Table of Contents

1. About
2. Installation
3. Operation
4. Development

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


### Deploying via Docker



## 3. Operation
Igor is accessed through your web browser...

## 4. Development
If you have modifications or want to take the project further, Igor can be forked as required and further developed by your local teams. 