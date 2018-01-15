Agent-stats Utils
=================
Handy utilities for managing an ingress agent-stats group.

## Setting up
"Easy" instructions for getting started on ubuntu 16.04 are now on the [wiki](https://github.com/Yossi/agent-stats-utils/wiki/Ubuntu-16.04-instructions-from-scratch).
### Requirements
  * python3.4+
  * mysql server

Clone this repo.   
Create database from schema.sql (This is destructive to existing tables. DO NOT 
run on an existing setup with data you don't want to lose.)  
Copy secrets.py.example to secrets.py and change the settings and credentials in 
there to real values. Get yourself an [API key](https://www.agent-stats.com/preferences.php) and put it in secrets.py .  
Then create a virtualenv, activate it and install the requirements:
```
virtualenv -p /usr/bin/python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

## How to use
```
python agent_stats.py snarf
```

You can operate on a group with the -g option (group names are case sensitive).
If -g is left out, it will either do all groups or error out. Whatever works.
Any command that has text output can have that output redirected to email with
the -m option. If you are redirecting to email, you can set a custom subject
with -s. Default subject is the command name + the group name. Pass the -a option 
to have the output attached as a .txt file as well.

Sometimes you find yourself needing to change how many ranks make it into the charts.
By default this is 10 but you can change it to whatever with the -n option.

Once you get a feel for what this script does, you may want to set it up to run with
crontab, or something similar.

## Features
### snarf
Scrape the data. If a new group is encountered, its gets added. If a new agent
is encountered, they get added. If an agent joins or leaves a group, that gets 
handled. If an agent changes their name, sucks to be them, they are treated
like a new agent.
Some stat validation is carried out (see below) and if the sanity check fails, 
the row is flagged and not used for computing dings.
Outputs a list of added/removed agents and flagged stats.

### check_for_applicants
Solves a common problem where agents apply to join a group and no one notices
for weeks. 
If you have a star (mod or admin) you are able to see pending agents. This 
command outputs the list of pending agents. No effort is made to avoid sending a
name again if it was ignored. i.e. If you don't take care of a pending user one 
way or another you will keep getting spammed about them.

### summary
Typically not used stand alone. Gets all the badge dings that happened between
each agent's most recent data point and their most recent data point over 7 days
old. Searches across groups, if passed "all", "smurfs" or "frogs".

### weekly/monthly/custom
This is the main reason all this was written. Grabs the weekly (or monthly, etc.) page
for your group and extracts the top *N* agents for each category. Ties for *N*th
place are all included. 
Also includes a ding summary for the week or month (see above: summary). 
Formats everything with G+ markup so it looks decent when you post to G+.

### update_group_names
Compares the group names from the database to the names online. If a name has 
changed, you are offered the opportunity to update it. You will need to update 
the names in crontab manually after you update the database names.

## Custom stats
You can invent your own stats. Look in [extra_stats.py.example](https://github.com/Yossi/agent-stats-utils/blob/master/extra_stats.py.example) to see how. Save as extra_stats.py when ready.

## Stat validation
Often stats get screwed up. Usually because agent-stats.com botched the OCR.
If any of the following conditions are not true, the stat is considered suspect:
```
    date >= game_start
    today >= date
    discoverer >= seer
    connector >= mind_controller/2
    hacker+builder+engineer+connector >= explorer
    explorer >= pioneer
    builder >= liberator
    liberator >= pioneer
    disruptor >= salvator/2
    purifier >= disruptor
    purifier >= neutralizer
    hacker >= translator/15
    builder >= magnusbuilder
    explorer >= magnusbuilder/8
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
find the user in the agents table and adjust the apdiff column manually. (learn
some SQL, you lazy bum)~~ (While this was fun to work out, it doesn't really provide a very good
signal. Far too much noise. So I cut it out)
