#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import datetime
import logging
import re
import sys
from time import sleep
from collections import OrderedDict, namedtuple

import requests
from num2words import num2words as n2w
from bs4 import BeautifulSoup
from functools import lru_cache

from Stat import Stat
from util import mail, get_html

from util import exec_mysql, cm
from secrets import dbconfig, api_key

cm.set_credentials(dbconfig)

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt="%H:%M:%S")
logging.getLogger("requests").setLevel(logging.WARNING)

s = requests.Session()
s.headers.update({'AS-Key': api_key})

def num2words(n):
    if n < 10:
        return n2w(n).title()
    return str(n)

def get_stats(group_id, time_span='now', number=10, submitters=[0]):
    time_span = {'all time': 'now',
                 'monthly': 'month',
                 'weekly': 'week'}.get(time_span, time_span)
    output = []
    logging.info('read table: group {}, span {}'.format(groups()[group_id], time_span))

    data = list(read_table(group_id, time_span))

    definitions = {'explorer': '_(New Portals Visited)_',
                   'seer': '_(Portals Discovered)_',
                   'trekker': '_(Distance Walked)_',
                   'builder': '_(Resonators Deployed)_',
                   'connector': '_(Links Created)_',
                   'mind-controller': '_(Control Fields Created)_',
                   'illuminator': '_(Mind Units Captured)_',
                   'recharger': '_(XM Recharged)_',
                   'liberator': '_(Portals Captured)_',
                   'pioneer': '_(New Portals Captured)_',
                   'engineer': '_(Mods Deployed)_',
                   'purifier': '_(Resonators Destroyed)_',
                   'guardian': '_(Max Time Portal Held)_',
                   'specops': '_(New Missions Completed)_',
                   'missionday': '_(Mission Day(s) Attended)_',
                   'hacker': '_(Hacks)_',
                   'translator': '_(Glyph Hack Points)_',
                   'sojourner': '_(Longest Hacking Streak)_',
                   'recruiter': '_(Agents successfully recruited)_',
                   'magnusbuilder': '_(Unique Resonator Slots Deployed)_',
                   'collector': '_(XM Collected)_',
                   'binder': '_(Longest Link Ever Created)_',
                   'country-master': '_(Largest Control Field)_',
                   'neutralizer': '_(Portals Neutralized)_',
                   'disruptor': '_(Enemy Links Destroyed)_',
                   'salvator': '_(Enemy Control Fields Destroyed)_',
                   'smuggler': '_(Max Time Link Maintained)_',
                   'link-master': '_(Max Link Length × Days)_',
                   'controller': '_(Max Time Field Held)_',
                   'field-master': '_(Largest Field MUs × Days)_',
                   'missionday':'_(Mission Days Attended)_'}

    # these categories are what become the topN lists. definitions above are just for reference (still needed if a category is active)
    categories = ['ap', 'explorer', 'trekker', 'builder', 'connector',
                  'mind-controller', 'illuminator', 'recharger', 'liberator',
                  'pioneer', 'engineer', 'purifier', 'hacker', 'translator',
                  'specops', 'seer', 'collector', 'neutralizer', 'disruptor',
                  'salvator', 'magnusbuilder', 'missionday']
    submitters[0] = 0
    for category in categories:
        output.append('\n*Top %s* %s' % (category.title(), definitions.get(category.lower(), '')))
        top_list = sorted((line for line in data if float(line[category])), key=lambda k: float(k[category]), reverse=True)
        submitters[0] = max(submitters[0], len(top_list))
        i = -1
        for i, line in enumerate(top_list):
            datum = float(line[category])
            if i > number-1 and datum != temp: # the 0s got filtered out on that inscrutable line above
                break
                
            if datum.is_integer():
                datum_string = '{:,}'.format(int(datum))
            elif datum > 100000:
                datum_string = '{:,}'.format(datum)
            else:
                datum_string = '{:,g}'.format(datum)
            
            output.append('{}  {}'.format(line['name'], datum_string))
            temp = datum
        if i < 0:
            output.pop()
    return '\n'.join(output)

def cleanup_data(data):
    last_submit = data['last_submit']
    for k, v in data.items():
        if v == '-':
            data[k] = 0
    data['last_submit'] = last_submit
    return data

def read_table(group_id, time_span):
    count = 0
    API_url = 'https://api.agent-stats.com/groups/{}/{}'
    r = s.get(API_url.format(group_id, time_span), stream=True)
    r.raise_for_status() # debug
    for agent, data in r.json().items():
        data['name'] = '@'+agent
        count += 1
        yield cleanup_data(data)
    logging.info('%s rows' % count)

@lru_cache(maxsize=None)
def groups():
    r = s.get('https://api.agent-stats.com/groups')
    r.raise_for_status() # debug
    return dict([(g['groupid'], g['groupname']) for g in r.json() if '.' in g['groupid']])

def get_groups(group=None):
    if group in ('smurfs', 'frogs', 'all', None):
        group_id, group_name = None, None
    elif re.fullmatch(r'([0-9a-f]{14}\.[\d]{8})', group):
        group_id = group
        group_name = groups()[group]
    else:
        group_id = exec_mysql('SELECT url FROM groups WHERE `name` = "{}"'.format(group))[0][0]
        group_name = group
        
    return group_id, group_name

def new_badges(old_data, new_data):
    ranks = ['Locked', 'Bronze', 'Silver', 'Gold', 'Platinum', 'Onyx']
    result = {}
    for category, old_rank in old_data.items():
        new_rank = new_data[category]
        if old_rank != new_rank: # still detect changes in Onyx multiples
            old_rank = old_rank.split()[-1]
            try:
                if ranks.index(old_rank) < ranks.index(new_rank): # else if new_rank has a multiplier on it .index() will fail with ValueError
                    result[category] = ranks[ranks.index(old_rank)+1:ranks.index(new_rank)+1]
            except ValueError:
                result[category] = [new_data[category]]
    return result

def englishify(new_badges):
    data = [badge.upper()+' ' + ", ".join(ranks[:-2] + [" and ".join(ranks[-2:])]) for badge, ranks in new_badges.items()]
    return ", ".join(data[:-2] + [" and ".join(data[-2:])])

def collate_agents():
    logging.info('collate agents')
    general_groups = dict(exec_mysql("SELECT name, idgroups FROM groups WHERE name IN ('smurfs', 'frogs', 'all');"))
    for agent_id, name, faction in exec_mysql('select idagents, name, faction from agents;'):
        faction = 'frogs' if faction == 'enl' else 'smurfs'
        sql = '''INSERT INTO `membership`
                 VALUES ('{}', '{}')
                 ON DUPLICATE KEY UPDATE idagents=idagents;'''.format(agent_id, general_groups['all'])
        exec_mysql(sql)

        sql = '''INSERT INTO `membership`
                 VALUES ('{}', '{}')
                 ON DUPLICATE KEY UPDATE idagents=idagents;'''.format(agent_id, general_groups[faction])
        exec_mysql(sql)

def snarf(group=None):
    group_id, group_name = get_groups(group)

    if not group_id:
        results = ''
        for group_id, group_name in groups().items():
            logging.info('snarfing '+group_name)
            idgroups = exec_mysql("SELECT idgroups FROM groups WHERE url = '{}';".format(group_id))
            if not idgroups:
                sql = '''INSERT INTO `groups`
                         SET `name`='{}', url='{}';'''.format(group_name, group_id)
                exec_mysql(sql)
            results += snarf(group_id) # getting all recursive and shiz
        collate_agents()
        return results
    else:
        added, removed, flagged, flipped = [], [], [], []
        idgroups = exec_mysql("SELECT idgroups FROM groups WHERE url = '{}';".format(group_id))[0][0]
        remaining_roster = [item for sublist in exec_mysql("SELECT idagents FROM membership WHERE idgroups = {};".format(idgroups)) for item in sublist] # get the class attendance sheet

        logging.info('read table: group {}, span now'.format(group_name))
        for data in read_table(group_id, 'now'):
            stat = Stat()
            stat.table_load(**data)
            stat.save()
            if stat.flag and stat.changed:
                flagged.append((stat.date, stat.name, stat.reasons))

            try:
                remaining_roster.remove(stat.agent_id) # take attendance
            except ValueError:
                logging.info('Agent added: {} {}'.format(stat.faction.upper(), stat.name)) # new kid
                added.append(stat.faction.upper() + ' ' + stat.name)

            sql = '''INSERT INTO `membership`
                     VALUES ('{}', '{}')
                     ON DUPLICATE KEY UPDATE idagents=idagents;'''.format(stat.agent_id, idgroups)
            exec_mysql(sql)
            
            if stat.faction != exec_mysql('SELECT faction FROM agents WHERE `name` = "{}";'.format(stat.name))[0][0]:
                logging.info('Agent flipped: {} -> {}'.format(stat.name, stat.faction.upper()))
                flipped.append('{} -> {}'.format(stat.name, stat.faction))
                exec_mysql('UPDATE agents SET faction="{}" WHERE `name`="{}";'.format(stat.faction, stat.name))

        if remaining_roster:
            remaining_roster = str(tuple(remaining_roster)).replace(',)',')') # absentees
            removed = sum(exec_mysql("SELECT name FROM agents WHERE idagents in {};".format(remaining_roster)), ())
            logging.info('Agent(s) removed: %s' % str(removed))
            exec_mysql("DELETE FROM membership WHERE idagents in {} and idgroups = {};".format(remaining_roster, idgroups))

        output = []
        if added or removed or flagged or flipped:
            output.append(group_name+':')
            if flipped:
                output.append('  Flipped:')
                output.append('    '+'\n    '.join(flipped))

            if added:
                output.append('  Added:')
                output.append('    '+'\n    '.join(added))

            if removed:
                output.append('  Removed:')
                output.append('    '+'\n    '.join(removed))

            if flagged:
                output.append('  Flagged:')
                for flagged_agent in flagged:
                    output.append('    {} {}'.format(*flagged_agent))
                    output.append('      '+'\n      '.join(flagged_agent[2]))

        return '\n'.join(output) + '\n'

def get_badges(data):
    categories = {'explorer': [100, 1000, 2000, 10000, 30000],
                  'seer': [10, 50, 200, 500, 5000],
                  'trekker': [10, 100, 300, 1000, 2500],
                  'builder': [2000, 10000, 30000, 100000, 200000],
                  'connector': [50, 1000, 5000, 25000, 100000],
                  'mind_controller': [100, 500, 2000, 10000, 40000],
                  'illuminator': [5000, 50000, 250000, 1000000, 4000000],
                  'recharger': [100000, 1000000, 3000000, 10000000, 25000000],
                  'liberator': [100, 1000, 5000, 15000, 40000],
                  'pioneer': [20, 200, 1000, 5000, 20000],
                  'engineer': [150, 1500, 5000, 20000, 50000],
                  'purifier': [2000, 10000, 30000, 100000, 300000],
                  'guardian': [3, 10, 20, 90, 150],
                  'specops': [5, 25, 100, 200, 500],
                  'missionday': [1, 3, 6, 10, 20],
                  'hacker': [2000, 10000, 30000, 100000, 200000],
                  'translator': [200, 2000, 6000, 20000, 50000],
                  'sojourner': [15, 30, 60, 180, 360],
                  'recruiter': [2, 10, 25, 50, 100]}

    result = {}
    for category, ranks in categories.items():
        current = 'Locked'
        multiplier = 1
        for rank, badge in zip(ranks, ['Bronze', 'Silver', 'Gold', 'Platinum', 'Onyx']):
            if data[category] not in ['-', None] and int(data[category]) >= rank:
                current = badge
            if current == 'Onyx':
                multiplier = data[category] // rank
                if multiplier > 1:
                    current = '%sx %s' % (multiplier, current)
        result[category] = current
    
    #for category, ranks in {'magnusbuilder': [1331, 3113]}.items(): # doesn't strictly have to be a loop, but i want it to match above
    #    current = 'Locked'
    #    multiplier = 1
    #    for rank, badge in zip(ranks, ['Builder', 'Architect']):
    #        if data[category] not in ['-', None] and int(data[category]) >= rank:
    #            current = badge
    #        if current == 'Architect':
    #            multiplier = data[category] // rank
    #            if multiplier > 1:
    #               current = '%sx %s' % (multiplier, current)
    #    result[category] = current

    return result

def summary(group='all', days=7):
    snarf(group)
    
    group_id, group_name = get_groups(group)
    if not group_id:
        group_id = {'all': 1, 'smurfs': 2, 'frogs':3}.get(group, None)

    headers = ('explorer',
               'seer',
               'trekker',
               'builder',
               'connector',
               'mind_controller',
               'illuminator',
               'recharger',
               'liberator',
               'pioneer',
               'engineer',
               'purifier',
               'guardian',
               'specops',
               'missionday',
               'hacker',
               'translator',
               'sojourner',
               'recruiter',
               'magnusbuilder')

    sql_before = '''SELECT x.name, s.`date`, `level`, ap, explorer, seer, trekker, builder, connector, `mind-controller` mind_controller, illuminator,
                           recharger, liberator, pioneer, engineer, purifier, guardian, specops, missionday, hacker, translator, sojourner, recruiter, magnusbuilder
                    FROM (
                        SELECT a.name name, s.idagents id, MAX(s.date) AS date
                        FROM agents a, stats s, membership m, groups g
                        WHERE a.idagents = s.idagents AND
                              s.idagents = m.idagents AND
                              m.idgroups = g.idgroups AND
                              g.`url` = '{}' AND
                              s.flag != 1 AND
                              date < ( CURDATE() - INTERVAL {} DAY )
                        GROUP BY id ) x
                    JOIN stats s ON x.id = s.idagents AND x.date = s.date
                 '''.format(group_id, days)

    baseline = {}
    for row in exec_mysql(sql_before):
        agent = row[0]
        if row[1]: # if has date. filters out the agents with rows of all 0s
            baseline[agent] = {'date': row[1], 'level': row[2], 'ap': row[3],
                               'badges': get_badges(dict(zip(headers, row[4:])))}

    sql_now = '''SELECT x.name, s.`date`, `level`, ap, explorer, seer, trekker, builder, connector, `mind-controller` mind_controller, illuminator,
                           recharger, liberator, pioneer, engineer, purifier, guardian, specops, missionday, hacker, translator, sojourner, recruiter, magnusbuilder
                    FROM (
                        SELECT a.name name, s.idagents id, MAX(s.date) AS date
                        FROM agents a, stats s, membership m, groups g
                        WHERE a.idagents = s.idagents AND
                              s.idagents = m.idagents AND
                              m.idgroups = g.idgroups AND
                              g.`url` = '{}' AND
                              s.flag != 1 AND
                              date >= ( CURDATE() - INTERVAL {} DAY )
                        GROUP BY id ) x
                    JOIN stats s ON x.id = s.idagents AND x.date = s.date
              '''.format(group_id, days)
    output = []
    footnote = ''
    for row in exec_mysql(sql_now):
        agent = row[0]
        if agent in baseline:
            date_old = baseline[agent]['date']
            date_new = row[1]
            level_old = baseline[agent]['level']
            level_new = row[2]
            ap_old = baseline[agent]['ap']
            ap_new = row[3]
            ap_40m_old = int(ap_old)//40000000
            ap_40m_new = int(ap_new)//40000000
            badges_old = baseline[agent]['badges']
            badges_new = get_badges(dict(zip(headers, row[4:])))
            changes = OrderedDict()
            if badges_old != badges_new:
                changes.update(new_badges(badges_old, badges_new))
            if ap_40m_old != ap_40m_new:
                changes['ap'] = ['{} MILLION'.format((l+1)*40) for l in range(ap_40m_old, ap_40m_new)]
            if level_old < level_new:
                changes['level'] = [str(l+1) for l in range(level_old, level_new)]
            if changes:
                earnings = englishify(changes)
                today = datetime.date.today()
                stale = today - datetime.timedelta(days=days*2)
                note = ''
                if date_old < stale:
                    note = '¹' # chcp 65001
                    footnote = '¹Start date more than 2 %s ago' % ('weeks' if days == 7 else 'months',)

                if today - date_old > datetime.timedelta(days=365): # close enough. no one cares about leap years
                    template = '*{}* earned {} sometime between {old.month}/{old.day}/{old.year}{} and {new.month}/{new.day}/{new.year}'
                else:
                    template = '*{}* earned {} sometime between {old.month}/{old.day}{} and {new.month}/{new.day}'

                output.append(template.format(agent, earnings, note, old=date_old, new=date_new))
    output = sorted(output, key=lambda s: s.lower())
    if footnote:
        output.append(footnote)
    return '\n'.join(output)

weekly_template = '''Great work agents!! If you would like to be included in future top {} lists please 
join our agent-stats group https://www.agent-stats.com/groups.php?group={} . 
Don’t know what agent-stats is? See here: https://www.agent-stats.com/manual.php . 
To have your stats show up you need to upload your stats at least right after 
you see this (right now) and then again right before you see this next week (just upload 
your stats late Sunday night / early Monday morning when you are done for the night). 
It’s also a good idea to upload your stats every night.'''
def weekly_roundup(group):
    group_id, group_name = get_groups(group)
    if not group_id: return 'please specify group'
    output = []
    submitters = [0]
    logging.info('starting weekly roundup')
    start = datetime.datetime.now()
    output.append(group_name)
    logging.info('getting weekly top lists')
    charts = get_stats(group_id, 'weekly', args.number, submitters)
    output.append('*Top %s (of %s reporting) for the week of %s*' % (num2words(min(args.number, submitters[0])), num2words(submitters[0]), (start - datetime.timedelta(days=7)).date().strftime("%m/%d")))
    output.append(charts)
    output.append('')
    output.append('Recent badge dings:')
    output.append('')
    logging.info('getting badge dings')
    output.append(summary(group_id, 7))
    output.append('')
    output.append(weekly_template.format(num2words(args.number).lower(), group_id).replace('\n', ''))
    end = datetime.datetime.now()
    output.append('')
    output.append('_Job started on {} and ran for {}_'.format(start, end-start))
    return '\n'.join(output)

monthly_template = '''Great work agents!! If you would like to be included in future top {} lists please 
join our agent-stats group https://www.agent-stats.com/groups.php?group={} . 
Don’t know what agent-stats is? See here: https://www.agent-stats.com/manual.php . 
To have your stats show up you need to upload your stats at least right after 
you see this (right now) and then again right before you see this next month (just upload 
your stats late on the night / early morning before the 1st of the month when you are done for the night). 
It’s also a good idea to upload your stats every night.'''
def monthly_roundup(group):
    group_id, group_name = get_groups(group)
    if not group_id: return 'please specify group'
    output = []
    submitters = [0]
    logging.info('starting monthly roundup')
    start = datetime.datetime.now()
    output.append(group_name)
    logging.info('getting monthly top lists')
    charts = get_stats(group_id, 'monthly', args.number, submitters)
    month = (start - datetime.timedelta(days=start.day)).date()
    output.append('*Top %s (of %s reporting) for the month of %s*' % (num2words(min(args.number, submitters[0])), num2words(submitters[0]), month.strftime("%B")))
    output.append(charts)
    output.append('')
    output.append('Recent badge dings:')
    output.append('')
    logging.info('getting badge dings')
    output.append(summary(group_id, month.day))
    output.append('')
    output.append(monthly_template.format(num2words(args.number).lower(), group_id).replace('\n', ''))
    end = datetime.datetime.now()
    output.append('')
    output.append('_Job started on {} and ran for {}_'.format(start, end-start))
    return '\n'.join(output)

custom_template = '''Great work agents!! If you would like to be included in future top {} lists please 
join our agent-stats group https://www.agent-stats.com/groups.php?group={} . 
Don’t know what agent-stats is? See here: https://www.agent-stats.com/manual.php . 
For your stats show up on this list you need to have uploaded your stats at least twice between {} and {}'''
def custom_roundup(group):
    group_id, group_name = get_groups(group)
    if not group_id: return 'please specify group'
    output = []
    submitters = [0]
    logging.info('starting custom roundup')
    start = datetime.datetime.now()
    output.append(group_name)
    startDate, endDate = get_custom_date_ranges(group)
    logging.info('setting off a refresh. waiting 10 seconds to make sure it finishes')
    r = s.post('https://api.agent-stats.com/groups/{}/refresh'.format(group_id))
    r.raise_for_status() # debug
    sleep(10)
    logging.info('getting custom top lists')
    charts = get_stats(group_id, 'custom', args.number, submitters)
    output.append('*Top %s (of %s reporting) for the span from %s to %s*' % (num2words(min(args.number, submitters[0])), num2words(submitters[0]), startDate, endDate))
    output.append(charts)
    output.append('')
    output.append('Recent badge dings:')
    output.append('')
    logging.info('getting badge dings')
    output.append(summary(group_id, (endDate - startDate).days))
    output.append('')
    output.append(custom_template.format(num2words(args.number).lower(), group_id, startDate, endDate).replace('\n', ''))
    end = datetime.datetime.now()
    output.append('')
    output.append('_Job started on {} and ran for {}_'.format(start, end-start))
    return '\n'.join(output)

def get_custom_date_ranges(group):
    html = get_html(scoreboard=group, time_span='custom')
    soup = BeautifulSoup(html, "html.parser")
    #soup.find('input', {'name':'startDate'}).attrs['value']
    for span in soup('span'):
        if span.text.startswith('Last refresh:'):
            return (datetime.datetime.strptime(span.text[42:61], '%Y-%m-%d %H:%M:%S'),
                    datetime.datetime.strptime(span.text[65:], '%Y-%m-%d %H:%M:%S'))

def test(group):
    print(get_custom_date_ranges(group))

def check_for_applicants(group):
    group_id, group_name = get_groups(group)
    r = s.get('https://api.agent-stats.com/groups/{}/pending'.format(group_id), stream=True)
    r.raise_for_status() # debug
    message = []
    if r.json():
        message.append('Agent(s) awaiting validation to the {} group:'.format(group))
        for agent in r.json():
            message.append('    @{username}'.format(**dict(agent)))

        message.append('\nGo to https://www.agent-stats.com/groups.php?group={} and click on the [View admin panel] button to take care of it.'.format(group_id))
    return '\n'.join(message)

def update_group_names(group):
    db = dict(exec_mysql('SELECT url, `name` FROM groups WHERE url IS NOT NULL;'))
    web = dict(groups())
    allgood = True
    for gid in web:
        if web[gid] != db[gid]:
            allgood = False
            print('{} was named "{}" is now "{}"'.format(gid, db[gid], web[gid]))
            if input('Update the database? (y/N) ').lower().startswith('y'):
                exec_mysql('UPDATE groups SET `name`="{}" WHERE url="{}" AND `name`="{}"; '.format(web[gid], gid, db[gid]))
    if allgood:
        print('\nAll group names match\n')

if __name__ == '__main__':
    actions = OrderedDict([('snarf', snarf),
                           ('summary', summary),
                           ('weekly', weekly_roundup),
                           ('monthly', monthly_roundup),
                           ('custom', custom_roundup),
                           ('check_for_applicants', check_for_applicants),
                           ('update_group_names', update_group_names),
                           ('test', test)])

    parser = argparse.ArgumentParser(description='Tools for agent-stats admins')
    parser.add_argument('action', help='task to perform', choices=actions)
    parser.add_argument('-n', '--number', default=10, type=int, help='number of ranks to show')
    parser.add_argument('-g', '--group', help='group to focus on', choices=[name for row in exec_mysql('SELECT name FROM groups;') for name in row])
    parser.add_argument('-m', '--mail', nargs='*', help='email address to get output')
    parser.add_argument('-s', '--subject', help='optional email subject')

    args = parser.parse_args()

    try:
        result = actions.get(args.action)(args.group)
    except:
        if not args.mail:
            raise
        else:
            if not args.group: args.group=''
            subject = args.action+' '+args.group if not args.subject else args.subject
            mail([args.mail[0]], subject, str(sys.exc_info()[0]))
            logging.info('CRASHED and email sent')
    else:
        if result:
            result = result.strip()

            if not args.mail:
                print(result) # chcp 65001
            elif result:
                if not args.group: args.group=''
                subject = args.action+' '+args.group if not args.subject else args.subject
                mail(args.mail, subject, result)
                logging.info('email sent')
        logging.info('Done')