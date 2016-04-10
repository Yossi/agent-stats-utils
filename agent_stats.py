#!/usr/bin/python
# -*- coding: utf-8 -*-

from pprint import pprint
import argparse
import datetime
import logging
from collections import OrderedDict, namedtuple

from bs4 import BeautifulSoup
from dateutil.parser import parse

from util import mail, get_html

from util import exec_mysql, cm
from secrets import dbhost, db, dbuser, dbpasswd

cm.set_credentials({'host': dbhost, 'db': db, 'user': dbuser, 'passwd': dbpasswd})

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt="%H:%M:%S")

from Stat import Stat



today = datetime.date.today()
sojourner_start = datetime.date(2015, 3, 5)
game_start = datetime.date(2012, 11, 15)





def get_stats(group, time_span='current', number=10):
    definitions = {'explorer': '_(Unique Portals Visited)_',
                   'seer': '_(Portals Discovered)_',
                   'trekker': '_(Distance Walked)_',
                   'builder': '_(Resonators Deployed)_',
                   'connector': '_(Links Created)_',
                   'mind-controller': '_(Control Fields Created)_',
                   'illuminator': '_(Mind Units Captured)_',
                   'recharger': '_(XM Recharged)_',
                   'liberator': '_(Portals Captured)_',
                   'pioneer': '_(Unique Portals Captured)_',
                   'engineer': '_(Mods Deployed)_',
                   'purifier': '_(Resonators Destroyed)_',
                   'guardian': '_(Max Time Portal Held)_',
                   'specops': '_(Unique Missions Completed)_',
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

    time_span = {'all time': 'current',
                 'monthly': 'last month',
                 'weekly': 'last week'}.get(time_span, time_span)
    output = []
    html = get_html(scoreboard=group, time_span=time_span)
    soup = BeautifulSoup(html, "html.parser")
    table = soup.table
    data = list(read_table(table))
    categories_full = ('ap', 'explorer', 'seer', 'collector', 'trekker', 'builder',
                       'connector', 'mind-controller', 'illuminator', 'binder',
                       'country-master', 'recharger', 'liberator', 'pioneer',
                       'engineer', 'purifier', 'neutralizer', 'disruptor',
                       'salvator', 'guardian', 'smuggler', 'link-master',
                       'controller', 'field-master', 'specops', 'missionday', 'hacker',
                       'translator', 'sojourner', 'recruiter')
    categories_badges = ('ap', 'explorer', 'seer', 'trekker', 'builder',
                         'connector', 'mind-controller', 'illuminator',
                         'recharger', 'liberator', 'pioneer', 'engineer',
                         'purifier', 'guardian',  'specops', 'missionday', 'hacker',
                         'translator', 'sojourner', 'recruiter')
    categories = ('ap', 'explorer', 'trekker', 'builder', 'connector',
                  'mind-controller', 'illuminator', 'recharger', 'liberator',
                  'pioneer', 'engineer', 'purifier', 'hacker', 'translator',
                  'specops', 'seer', 'collector', 'neutralizer', 'disruptor',
                  'salvator')
    for category in categories:
        output.append('\n*Top %s* %s' % (category.title(), definitions.get(category.lower(), '')))
        for i, line in enumerate(sorted(data, key=lambda k: int(k[category]), reverse=True)):
            if i > number-1 and int(line[category]) != temp or int(line[category]) == 0:
                break
            output.append('{}  {:,}'.format(line['Agent name'], int(line[category])))
            temp = int(line[category])
        if not i:
            output.pop()
    return '\n'.join(output)


def cleanup_data(data):
    for k, v in data.items():
        data[k] = v.replace(',','').replace('-','0')
    data['Last submission'] = parse(data['Last submission'].replace('\u200b', '')).strftime("%Y-%m-%d") if not data['Last submission'].startswith('0') else '0/0/0'
    data['Agent name'] = data['Agent name'].strip()[:16]
    return data

def read_table(table):
    logging.info('read table')
    rows = table.find_all('tr')
    
    headers = [cell.text.replace('↓', '') for cell in rows[0].find_all('td')]
    headers[0] = 'Faction'

    count = 0
    for row in rows[1:]:
        count += 1
        cells = row.find_all('td')
        
        d = [cell.text for cell in cells]
        try: d[0] = cells[1]['class'][0]
        except KeyError: d[0] = 'nul'
        
        data = dict(zip(headers, d))

        yield cleanup_data(data)
    logging.info('%s rows' % count)






def get_groups():
    soup = BeautifulSoup(get_html(), "html.parser")
    return [(li.find('a').text, li.find('a').get('href')[18:]) for li in soup.find_all('ul')[1].find_all('li')[2:]]




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
                 VALUES ('{0}', '{1}')
                 ON DUPLICATE KEY UPDATE idagents=idagents;'''.format(agent_id, general_groups['all'])
        exec_mysql(sql)
     
        sql = '''INSERT INTO `membership`
                 VALUES ('{0}', '{1}')
                 ON DUPLICATE KEY UPDATE idagents=idagents;'''.format(agent_id, general_groups[faction])
        exec_mysql(sql)

def snarf(group=None):
    if group in ('smurfs', 'frogs', 'all'):
        group = None
    
    if not group:
        results = ''
        for group, url in get_groups():
            logging.info('snarfing '+group)
            group_id = exec_mysql("SELECT idgroups FROM groups WHERE name = '{0}';".format(group))
            if group_id:
                group_id = group_id[0][0]
            else:
                sql = '''INSERT INTO `groups`
                         SET `name`='{0}', url='{1}';'''.format(group, url)
                         #ON DUPLICATE KEY UPDATE idgroups=LAST_INSERT_ID(idgroups)
                exec_mysql(sql)
                group_id = exec_mysql("SELECT idgroups FROM groups WHERE name = '{0}';".format(group))[0][0]
            results += snarf(group) # getting all recursive and shiz
        colate_agents()
        #print(results)
        return results
    else:
        added, removed, flagged = [], [], []
        group_id = exec_mysql("SELECT idgroups FROM groups WHERE name = '{0}';".format(group))[0][0]
        remaining_roster = [item for sublist in exec_mysql("SELECT idagents FROM membership WHERE idgroups = {0};".format(group_id)) for item in sublist]
        html = get_html(group)
        logging.info('mix the soup')
        soup = BeautifulSoup(html, "html.parser")
        logging.info("soup's up")
        
        table = read_table(soup.table)
        for data in table:
            stat = Stat()
            stat.table_load(**data)
            stat.save()
            if stat.flag and stat.changed:
                flagged.append((stat.date, stat.name, stat.reasons))
            
            try:
                remaining_roster.remove(stat.agent_id)
            except ValueError:
                logging.info('Agent added: {0}'.format(stat.name))
                added.append(stat.name)
            
            sql = '''INSERT INTO `membership`
                     VALUES ('{0}', '{1}')
                     ON DUPLICATE KEY UPDATE idagents=idagents;'''.format(stat.agent_id, group_id)
            exec_mysql(sql)
            
        if remaining_roster:
            remaining_roster = str(tuple(remaining_roster)).replace(',)',')')
            removed = sum(exec_mysql("SELECT name FROM agents WHERE idagents in {};".format(remaining_roster)), ())
            logging.info('Agent(s) removed: %s' % str(removed))
            exec_mysql("DELETE FROM membership WHERE idagents in {0} and idgroups = {1};".format(remaining_roster, group_id))
        
        output = []
        if added or removed or flagged:
            output.append(group+':')
            if added:
                output.append('  Added:')
                output.append('    '+'\n    '.join(added))
                
            if removed:
                output.append('  Removed:')
                output.append('    '+'\n    '.join(removed))
            
            if flagged:
                output.append('  Flagged:')
                for flagged_agent in flagged:
                    output.append('    {0} {1}'.format(*flagged_agent))
                    output.append('      '+'\n      '.join(flagged_agent[2]))
                
        return '\n'.join(output) + '\n'
        
def test():
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
            if data[category] != '-' and int(data[category]) >= rank:
                current = badge
            if current == 'Onyx':
                multiplier = data[category] // rank
                if multiplier > 1: 
                    current = '%sx %s' % (multiplier, current)
        result[category] = current
    return result

def summary(group='all', days=7):
    if not group: group = 'all'

    snarf(group)
    
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
    
    sql_before = '''SELECT `name`, `date`, `level`, ap, explorer, seer, trekker, builder, connector, `mind-controller` mind_controller, illuminator, recharger,
                           liberator, pioneer, engineer, purifier, guardian, specops, missionday, hacker, translator, sojourner, recruiter
                    FROM (
                        SELECT a.`name` `name`, s.* 
                        FROM agents a, stats s, membership m, groups g 
                        WHERE a.idagents = s.idagents AND a.idagents = m.idagents AND m.idgroups = g.idgroups AND g.`name` = '{}'
                          AND s.flag != 1 AND s.`date` < ( CURDATE() - INTERVAL {} DAY )
                        ORDER BY `date` DESC
                    ) as t1
                    GROUP BY `name`;
                 '''.format(group, days)

    baseline = {}
    for row in exec_mysql(sql_before):
        agent = row[0]
        if row[1]: # if it has a date. filters out the agents with rows of all 0s
            baseline[agent] = {'date': row[1], 'level': row[2], #'ap': row[3],
                               'badges': get_badges(dict(zip(headers, row[4:])))}

    sql_now = '''SELECT `name`, `date`, `level`, ap, explorer, seer, trekker, builder, connector, `mind-controller` mind_controller, illuminator, recharger,
                        liberator, pioneer, engineer, purifier, guardian, specops, missionday, hacker, translator, sojourner, recruiter
                 FROM (
                     SELECT a.`name` `name`, s.* 
                     FROM agents a, stats s, membership m, groups g 
                     WHERE a.idagents = s.idagents AND a.idagents = m.idagents AND m.idgroups = g.idgroups AND g.`name` = '{}'
                       AND s.flag != 1 AND s.`date` >= ( CURDATE() - INTERVAL {} DAY )
                     ORDER BY `date` DESC
                 ) as t1
                 GROUP BY `name`;
              '''.format(group, days)
    output = []
    footnote = ''
    for row in exec_mysql(sql_now):
        agent = row[0]
        #print row
       # print agent, baseline.get(agent, None)
        if agent in baseline:
            date_old = baseline[agent]['date']
            date_new = row[1]
            level_old = baseline[agent]['level']
            level_new = row[2]
            #ap_old = 
            #ap_new = row[3]
            badges_old = baseline[agent]['badges']
            badges_new = get_badges(dict(zip(headers, row[4:])))
            changes = OrderedDict()
            if badges_old != badges_new:
                changes.update(new_badges(badges_old, badges_new))
            if level_old < level_new:
                changes['level'] = [str(l+1) for l in range(level_old, level_new)]
            if changes:
                #print changes
                earnings = englishify(changes)
                stale = datetime.date.today() - datetime.timedelta(days=days*2)
                note = ''
                if date_old < stale:
                    note = '¹' # chcp 65001
                    footnote = '¹Start date more than 2 %s ago' % ('weeks' if days == 7 else 'months',)
                output.append('*{0}* earned {1} sometime between {old.month}/{old.day}{2} and {new.month}/{new.day}'.format(agent, earnings, note, old=date_old, new=date_new))
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
    if not group: return 'please specify group'
    output = []
    logging.info('starting weekly roundup')
    start = datetime.datetime.now()
    output.append(group)
    output.append('*Top Ten for the week of %s*' % (start - datetime.timedelta(days=7)).date().strftime("%m/%d"))
    logging.info('getting weekly top tens')
    output.append(get_stats(group, 'weekly', args.number))
    output.append('')
    output.append('Recent badge dings:')
    output.append('')
    logging.info('getting badge dings')
    output.append(summary(group, 7))
    output.append('')
    output.append(weekly_template.format(exec_mysql('SELECT url FROM groups WHERE name = "{}"'.format(group))[0][0]).replace('\n', ''))
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
    if not group: return 'please specify group'
    output = []
    logging.info('starting monthly roundup')
    start = datetime.datetime.now()
    output.append(group)
    output.append('*Top Ten for the month of %s*' % (start - datetime.timedelta(days=7)).date().strftime("%B"))
    logging.info('getting monthly top tens')
    output.append(get_stats(group, 'monthly', args.number))
    output.append('')
    output.append('Recent badge dings:')
    output.append('')
    logging.info('getting badge dings')
    output.append(summary(group, 30))
    output.append('')
    output.append(monthly_template.format(exec_mysql('SELECT url FROM groups WHERE name = "{}"'.format(group))[0][0]).replace('\n', ''))
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
        message.append('\nGo to {} and click on the [View admin panel] button to take care of it.'.format(html.partition('give them this url: <a href="')[2].partition('">https://www.agent-stats.com/groups.php')[0]))
    return '\n'.join(message)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tools for agent-stats admins')
    parser.add_argument('action', help='task to perform', choices=['snarf', 'check_for_applicants', 'summary', 'weekly', 'monthly', 'test'])
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
               'test': test}
    result = actions.get(args.action)(args.group)

    if result:
        result = result.strip()

        if not args.mail:
            print(result)
        elif result:
            if not args.group: args.group=''
            subject = args.action+' '+args.group if not args.subject else args.subject
            mail(args.mail, subject, result)
            logging.info('email sent')
    logging.info('Done')