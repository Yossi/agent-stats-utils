Agent-stats Utils
=================
Handy utilities for managing an ingress agent-stats group.

## Setting up
###Reqirements
  * python3.5+
  * mysql server

Clone this repo.
Get phantomjs https://bitbucket.org/ariya/phantomjs/downloads the 2.0 version is
a steaming pile of crap, get the 1.9.8 version. Throw it in the same dir as the 
other checked out files, or change the code in util.py that looks like this
```python
    driver = webdriver.PhantomJS('./phantomjs', service_args=['--cookies-file=cookies.txt'])
```
to point to the path where you installed phantomjs.
Create database from schema.sql (This is destructive to existing tables. Do not 
run on an existing setup with data you dont want to lose.)
Copy secrets.py.example to secrets.py and change the settings and credentials in 
there to real values.
Then create a virtualenv, activate it and install the requirements:
```
virtualenv -p /usr/bin/python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

## How to use
python agent_stats.py -h
First time this is run it will ask you to log in to your google account.
The script just takes what you enter and passes it to phantomjs where a google
login page is open (headless). It also stores a cookie so you don't have to
login every time.

VERY IMPORTANT!
 
 GUARD THE cookies.txt FILE WELL. IT GRANTS ACCESS TO YOUR ACCOUNT TO WHOEVER HAS IT! 
 
 If you suspect your cookie file has leaked, you need to hop into gmail and force
 sign out all your other sessions.

You can operate on a group with the -g option (group names are case sensitive).
If -g is left out, it will either do all groups or error out. Whatever works.
Any command that has text output can have that output redirected to email with
the -m option. If you are redirecting to email, you can set a custom subject
with -s. Default subject is the command name + the group name.

Sometimes you find yourself neding to change how many ranks make it into the charts.
By default this is 10 but you can change it to whatever with the -n option.
Note that this does not change any of the places where it says "Top ten" whatever.
Only use in special cases.

Once you get a feel for what this script does, you will want to set it up to run with
crontab, or the like.

## Features
###snarf
Scrape the data. If a new group is encountered, its gets added. If a new agent
is encountered, they get added. If an agent joins or leaves a group, that gets 
handled. If an agent changes their name, sucks to be them, they are treated
like a new agent.
Some stat validation is carried out (see below) and if the sanity check fails, 
the row is flagged and not used for computing dings.
Outputs a list of added/removed agents and flagged stats.

###check_for_applicants
Solves a common problem where agents apply to join a group and no one notices
for weeks. 
If you have a star (mod or admin) you are able to see pending agents. This 
command outputs the list of pending agents. No effort is made to avoid sending a
name again if it was ignored. i.e. If you don't take care of a pending user one 
way or another you will keep getting spammed about them.

###summary
Typically not used stand alone. Gets all the badge dings that happened between
each agent's most recent data point and their most recent data point over 7 days
old. Searches across all groups, unless passed a specific group.

###weekly/monthly
This is the main reason all this was written. Grabs the weekly (or monthly) page
for your group and extracts the top 10 agents for each category. Ties for 10th
place are all included. 
Also includes a ding summary for the week or month (see above: summary). 
Formats everything with G+ markup so it looks decent when you post it to G+.

## Stat validation
Often stats get screwed up. Usually because agent-stats.com botched the OCR.
If any of the following are not true, the stat is considered suspect:
```
    date >= game_start
    today >= date
    connector >= mind_controller/2
    hacker+builder+engineer+connector >= explorer
    explorer >= pioneer
    builder >= liberator
    liberator >= pioneer
    disruptor >= salvator/2
    purifier >= disruptor
    purifier >= neutralizer
    hacker >= translator/15
```
Also, minimum level is calculated based on knowable badges and ap.
In addition, minimum AP is calculated by the following formula 
(good luck teasing this monstrosity apart):
```python
    min_ap = liberator*125 + min(-(-max(0,(builder-liberator*8))/7)*65, -(-max(0,(builder-liberator*8))/8)*125) + connector*313 + mind_controller*1250 + liberator*500 + engineer*125 + purifier*75 + recharger/15000*10 + disruptor*187 + salvator*750
```
~~reported_ap - min_ap is then expected to always be increasing. If it is not, then
flag. Keep an eye on this last one, it's possible that it might come out huge
one time and then all subsequent stats will be flagged. If this happens, please
find the user in the agents table and adjust the apdiff column manually.~~ (learn
some SQL, you lazy bum)
