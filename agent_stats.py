#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import datetime
import logging
import re
from collections import OrderedDict, namedtuple

import requests
from num2words import num2words
from bs4 import BeautifulSoup
from functools import lru_cache

from Stat import Stat
from util import mail, get_html

from util import exec_mysql, cm
from secrets import dbhost, db, dbuser, dbpasswd, api_key

cm.set_credentials({'host': dbhost, 'db': db, 'user': dbuser, 'passwd': dbpasswd})

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt="%H:%M:%S")
logging.getLogger("requests").setLevel(logging.WARNING)

s = requests.Session()
s.headers.update({'AS-Key': api_key})
API_url = 'https://api.agent-stats.com/groups/{}/{}'

def get_stats(group_id, time_span='now', number=10):
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
                   'collector': '_(XM Collected)_',
                   'binder': '_(Longest Link Ever Created)_',
                   'country-master': '_(Largest Control Field)_',
                   'neutralizer': '_(Portals Neutralized)_',
                   'disruptor': '_(Enemy Links Destroyed)_',
                   'salvator': '_(Enemy Control Fields Destroyed)_',
                   'smuggler': '_(Max Time Link Maintained)_',
                   'link-master': '_(Max Link Length × Days)_',
                   'controller': '_(Max Time Field Held)_',
                   'field-master': '_(Largest Field MUs × Days)_'}

    time_span = {'all time': 'now',
                 'monthly': 'month',
                 'weekly': 'week'}.get(time_span, time_span)
    output = []
    logging.info('read table: group {}, span {}'.format(groups()[group_id], time_span))
    data = list(read_table(group_id, time_span))
    categories = ('ap', 'explorer', 'trekker', 'builder', 'connector',
                  'mind-controller', 'illuminator', 'recharger', 'liberator',
                  'pioneer', 'engineer', 'purifier', 'hacker', 'translator',
                  'specops', 'seer', 'collector', 'neutralizer', 'disruptor',
                  'salvator')
    submitters = 0
    for category in categories:
        output.append('\n*Top %s* %s' % (category.title(), definitions.get(category.lower(), '')))
        top_list = sorted((line for line in data if int(line[category])), key=lambda k: int(k[category]), reverse=True)
        submitters = max(submitters, len(top_list))
        i = 0
        for i, line in enumerate(top_list):
            if i > number-1 and int(line[category]) != temp:# or int(line[category]) == 0: # the 0s get filtered out on that inscrutable line above
                break
            output.append('{}  {:,}'.format(line['name'], int(line[category])))
            temp = int(line[category])
        if not i:
            output.pop()
    #print(submitters) # submitters now contains the info we're after but the manner of disseminating it is still undecided
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
    r = s.get(API_url.format(group_id, time_span), stream=True)
    for agent, data in r.json().items():
        data['name'] = '@'+agent
        count += 1
        yield cleanup_data(data)
    logging.info('%s rows' % count)

@lru_cache(maxsize=None)
def groups():
    r = s.get('https://api.agent-stats.com/groups')
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
        if old_rank != new_data[category]:
            try:
                if ranks.index(old_rank)+1 < ranks.index(new_data[category])+1:
                    result[category] = ranks[ranks.index(old_rank)+1:ranks.index(new_data[category])+1]
            except ValueError:
                result[category] = [new_data[category]]
    return result

def englishify(new_badges):
    data = [badge.upper()+' ' + ", ".join(ranks[:-2] + [" and ".join(ranks[-2:])]) for badge, ranks in new_badges.items()]
    return ", ".join(data[:-2] + [" and ".join(data[-2:])])

def colate_agents():
    logging.info('colate agents')
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
        colate_agents() # TODO: look into solving #7 in here
        return results
    else:
        added, removed, flagged = [], [], []
        idgroups = exec_mysql("SELECT idgroups FROM groups WHERE url = '{}';".format(group_id))[0][0]
        remaining_roster = [item for sublist in exec_mysql("SELECT idagents FROM membership WHERE idgroups = {};".format(idgroups)) for item in sublist]

        logging.info('read table: group {}, span now'.format(group_name))
        for data in read_table(group_id, 'now'):
            stat = Stat()
            stat.table_load(**data)
            stat.save()
            if stat.flag and stat.changed:
                flagged.append((stat.date, stat.name, stat.reasons))

            try:
                remaining_roster.remove(stat.agent_id)
            except ValueError:
                logging.info('Agent added: {}'.format(stat.name))
                added.append(stat.name)

            sql = '''INSERT INTO `membership`
                     VALUES ('{}', '{}')
                     ON DUPLICATE KEY UPDATE idagents=idagents;'''.format(stat.agent_id, idgroups)
            exec_mysql(sql)

        if remaining_roster:
            remaining_roster = str(tuple(remaining_roster)).replace(',)',')')
            removed = sum(exec_mysql("SELECT name FROM agents WHERE idagents in {};".format(remaining_roster)), ())
            logging.info('Agent(s) removed: %s' % str(removed))
            exec_mysql("DELETE FROM membership WHERE idagents in {} and idgroups = {};".format(remaining_roster, idgroups))

        output = []
        if added or removed or flagged:
            output.append(group_name+':')
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

def test(group):
    pass

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
               'recruiter')

    sql_before = '''SELECT x.name, s.`date`, `level`, ap, explorer, seer, trekker, builder, connector, `mind-controller` mind_controller, illuminator, 
                           recharger, liberator, pioneer, engineer, purifier, guardian, specops, missionday, hacker, translator, sojourner, recruiter
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
                           recharger, liberator, pioneer, engineer, purifier, guardian, specops, missionday, hacker, translator, sojourner, recruiter
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
                stale = datetime.date.today() - datetime.timedelta(days=days*2)
                note = ''
                if date_old < stale:
                    note = '¹' # chcp 65001
                    footnote = '¹Start date more than 2 %s ago' % ('weeks' if days == 7 else 'months',)

                if date_new - date_old > datetime.timedelta(days=365): # close enough. no one cares about leap years
                    template = '*{}* earned {} sometime between {old.month}/{old.day}/{old.year}{} and {new.month}/{new.day}/{new.year}'
                else:
                    template = '*{}* earned {} sometime between {old.month}/{old.day}{} and {new.month}/{new.day}'

                output.append(template.format(agent, earnings, note, old=date_old, new=date_new))
    output = sorted(output, key=lambda s: s.lower())
    if footnote:
        output.append(footnote)
    return '\n'.join(output)

weekly_template = '''Great work agents!! If you would like to be included in future top ten lists please 
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
    logging.info('starting weekly roundup')
    start = datetime.datetime.now()
    output.append(group_name)
    logging.info('getting weekly top lists')
    charts = get_stats(group_id, 'weekly', args.number)
    output.append('*Top %s for the week of %s*' % (num2words(args.number).title(), (start - datetime.timedelta(days=7)).date().strftime("%m/%d")))
    output.append(charts)
    output.append('')
    output.append('Recent badge dings:')
    output.append('')
    logging.info('getting badge dings')
    output.append(summary(group_id, 7))
    output.append('')
    output.append(weekly_template.format(group_id).replace('\n', ''))
    end = datetime.datetime.now()
    output.append('')
    output.append('_Job started on {} and ran for {}_'.format(start, end-start))
    return '\n'.join(output)

monthly_template = '''Great work agents!! If you would like to be included in future top ten lists please 
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
    logging.info('starting monthly roundup')
    start = datetime.datetime.now()
    output.append(group_name)
    logging.info('getting monthly top lists')
    charts = get_stats(group_id, 'monthly', args.number)
    output.append('*Top %s for the month of %s*' % (num2words(args.number).title(), (start - datetime.timedelta(days=7)).date().strftime("%B")))
    output.append(charts)
    output.append('')
    output.append('Recent badge dings:')
    output.append('')
    logging.info('getting badge dings')
    output.append(summary(group_id, 30))
    output.append('')
    output.append(monthly_template.format(group_id).replace('\n', ''))
    end = datetime.datetime.now()
    output.append('')
    output.append('_Job started on {} and ran for {}_'.format(start, end-start))
    return '\n'.join(output)

def check_for_applicants(group):
    html = get_html(scoreboard=group)
    soup = BeautifulSoup(html, "html.parser")
    applicants = None
    for elem in soup(text='Agents waiting for validation:'):
        applicants = elem.parent.parent.text.replace('\n', '').split('@')[1:]
        break
    message = []
    if applicants:
        message.append('Agent(s) awaiting validation to the {} group:'.format(group))
        for agent in applicants:
            message.append('    @{}'.format(agent))
        message.append('\nGo to {} and click on the [View admin panel] button to take care of it.'.format(html.partition('give them this url: <a href="')[2].partition('">https://www.agent-stats.com/groups.php')[0]).partition('&')[0])
    return '\n'.join(message)

def update_group_names(group):
    db = dict(exec_mysql('SELECT url, `name` FROM groups WHERE url IS NOT NULL;'))
    web = dict(groups())
    allgood = True
    for gid in web:
        if web[gid] != db[gid]:
            allgood = False
            print('{} was named "{}" is now "{}"'.format(gid, db[gid], web[gid]))
            if input('Update the db? (y/N) ').lower().startswith('y'):
                exec_mysql('UPDATE groups SET `name`="{}" WHERE url="{}" AND `name`="{}"; '.format(web[gid], gid, db[gid]))

    if allgood:
        print('\nAll group names match\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tools for agent-stats admins')
    parser.add_argument('action', help='task to perform', choices=['snarf', 'check_for_applicants', 'weekly', 'monthly', 'update_group_names', 'summary', 'test'])
    parser.add_argument('-n', '--number', default=10, type=int, help='number of ranks to show')
    parser.add_argument('-g', '--group', help='group to focus on', choices=[name for row in exec_mysql('SELECT name FROM groups;') for name in row])
    parser.add_argument('-m', '--mail', nargs='*', help='email address to get output')
    parser.add_argument('-s', '--subject', help='optional email subject')

    args = parser.parse_args()

    actions = {'snarf': snarf,
               'summary': summary,
               'weekly': weekly_roundup,
               'monthly': monthly_roundup,
               'check_for_applicants': check_for_applicants,
               'update_group_names': update_group_names,
               'test': test}
    result = actions.get(args.action)(args.group)

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