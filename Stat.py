from util import exec_mysql
import datetime
import logging
from itertools import chain
from dateutil.parser import parse

from cached_property import cached_property


today = datetime.date.today()
sojourner_start = datetime.date(2015, 3, 5)
game_start = datetime.date(2012, 11, 15)

class Stat(object):
    def __init__(self):
        pass

    def db_load(self, data):
        #be sure this is an empty object first
        pass

    def table_load(self, **row):
        self.date = parse(row['Last submission']).date() if not row['Last submission'].startswith('0') else '0/0/0'
        self.name = row['Agent name']
        self.faction = row['Faction']
        self.level = int(row['Level'])
        self.ap = int(row['ap'])
        self.explorer = int(row['explorer'])
        self.seer = int(row['seer'])
        self.collector = int(row['collector'])
        self.trekker = int(row['trekker'])
        self.builder = int(row['builder'])
        self.connector = int(row['connector'])
        self.mind_controller = int(row['mind-controller'])
        self.illuminator = int(row['illuminator'])
        self.binder = int(row['binder'])
        self.country_master = int(row['country-master'])
        self.recharger = int(row['recharger'])
        self.liberator = int(row['liberator'])
        self.pioneer = int(row['pioneer'])
        self.engineer = int(row['engineer'])
        self.purifier = int(row['purifier'])
        self.neutralizer = int(row['neutralizer'])
        self.disruptor = int(row['disruptor'])
        self.salvator = int(row['salvator'])
        self.guardian = int(row['guardian'])
        self.smuggler = int(row['smuggler'])
        self.link_master = int(row['link-master'])
        self.controller = int(row['controller'])
        self.field_master = int(row['field-master'])
        self.specops = int(row['specops'])
        self.hacker = int(row['hacker'])
        self.translator = int(row['translator'])
        self.sojourner = int(row['sojourner'])
        self.recruiter = int(row['recruiter'])

        agent_id = exec_mysql("SELECT idagents FROM agents WHERE name = '{0}';".format(self.name))
        if agent_id:
            self.agent_id = agent_id[0][0]
        else:
            sql = '''INSERT INTO `agents` SET `name`='{0}', `faction`='{1}';'''.format(self.name, self.faction)
            exec_mysql(sql)
            self.agent_id = exec_mysql("SELECT idagents FROM agents WHERE name = '{0}';".format(self.name))[0][0]

    @cached_property
    def min_ap(self):
        return self.liberator*125 + min(-(-max(0,(self.builder-self.liberator*8))//7)*65, -(-max(0,(self.builder-self.liberator*8))//8)*125) \
               + self.connector*313 + self.mind_controller*1250 + self.liberator*500 + self.engineer*125 \
               + self.purifier*75 + self.recharger//15000*10 + self.disruptor*187 + self.salvator*750

    @cached_property
    def min_level(self):
        from agent_stats import get_badges
        ranks = ['Onyx', 'Platinum', 'Gold', 'Silver', 'Bronze', 'Locked']
        sorted_badges = sorted([a.split(' ')[-1] for a in get_badges(self.__dict__).values()], key=lambda x: ranks.index(x))
        expanded_badges = list(chain.from_iterable([ranks[ranks.index(a):] for a in sorted_badges]))
        
        if 0 <= self.ap:
            level = 1
        if 2500 <= self.ap:
            level = 2
        if 20000 <= self.ap:
            level = 3
        if 700000 <= self.ap:
            level = 4
        if 150000 <= self.ap:
            level = 5
        if 300000 <= self.ap:
            level = 6
        if 600000 <= self.ap:
            level = 7
        if 1200000 <= self.ap:
            level = 8
        if 2400000 <= self.ap:
            if expanded_badges.count('Gold') < 1 or expanded_badges.count('Silver') < 4:
                return level
            level = 9
        if 4000000 <= self.ap:
            if expanded_badges.count('Gold') < 2 or expanded_badges.count('Silver') < 5:
                return level
            level = 10
        if 6000000 <= self.ap:
            if expanded_badges.count('Gold') < 4 or expanded_badges.count('Silver') < 6:
                return level
            level = 11
        if 8400000 <= self.ap:
            if expanded_badges.count('Gold') < 6 or expanded_badges.count('Silver') < 7:
                return level
            level = 12
        if 12000000 <= self.ap:
            if expanded_badges.count('Platinum') < 1 or expanded_badges.count('Gold') < 7:
                return level
            level = 13
        if 17000000 <= self.ap:
            if expanded_badges.count('Platinum') < 2:
                return level
            level = 14
        if 24000000 <= self.ap:
            if expanded_badges.count('Platinum') < 3:
                return level
            level = 15
        if 40000000 <= self.ap:
            if expanded_badges.count('Platinum') < 4 or expanded_badges.count('Onyx') < 2:
                return level
            level = 16
        
        return level

    @cached_property
    def flag(self):
        return bool(self.validate())

    def validate(self):
        if self.date == '0/0/0': return ['date missing']

        max_sojourner = (self.date - sojourner_start).days + 1
        max_guardian = (self.date - game_start).days + 1

        #apdiff = exec_mysql("SELECT apdiff FROM agents WHERE `name` = '{0}';".format(self.name))
        #if apdiff: self.apdiff = apdiff[0][0]

        reasons = []
        #if self.min_level > self.level:
        #    reasons.append( 'reported level too low: %s Min: %s' % (self.level, self.min_level) )
        if self.guardian > max_guardian:
            reasons.append( '%s %s %s %s %s' % (self.name.ljust(16), self.date, str(self.guardian).rjust(8), 'high guardian, max =', max_guardian) )
        if self.sojourner > max(0, max_sojourner):
            reasons.append( '%s %s %s %s %s' % (self.name.ljust(16), self.date, str(self.sojourner).rjust(8), 'high sojourner, max =', max_sojourner) )
        if game_start > self.date:
            reasons.append( '%s %s %s' % (self.name.ljust(16), self.date, 'date from before the game') )
        if self.date > today+datetime.timedelta(days=1):
            reasons.append( '%s %s %s' % (self.name.ljust(16), self.date, 'date in the future') )
        if (self.mind_controller/2) > self.connector:
            reasons.append( '%s %s %s %s %s' % (self.name.ljust(16), self.date, str(self.mind_controller).rjust(8), 'high mind_controller, max =', self.connector*2) )
        if self.explorer > self.hacker+self.builder+self.engineer+self.connector:
            reasons.append( '%s %s %s %s %s' % (self.name.ljust(16), self.date, str(self.explorer).rjust(8), 'high explorer, max =', self.hacker+self.builder+self.engineer+self.connector) )
        if self.pioneer > self.explorer:
            reasons.append( '%s %s %s %s %s' % (self.name.ljust(16), self.date, str(self.pioneer).rjust(8), 'high pioneer, (exp)max =', self.explorer) )
        if self.pioneer > self.liberator:
            reasons.append( '%s %s %s %s %s' % (self.name.ljust(16), self.date, str(self.pioneer).rjust(8), 'high pioneer, (lib)max =', self.liberator) )
        if self.liberator > self.builder:
            reasons.append( '%s %s %s %s %s' % (self.name.ljust(16), self.date, str(self.liberator).rjust(8), 'high liberator, max =', self.builder) )
        if (self.salvator/2) > self.disruptor:
            reasons.append( '%s %s %s %s %s' % (self.name.ljust(16), self.date, str(self.salvator).rjust(8), 'high salvator, max =', self.disruptor*2) )
        if self.disruptor > self.purifier:
            reasons.append( '%s %s %s %s %s' % (self.name.ljust(16), self.date, str(self.disruptor).rjust(8), 'high disruptor, max =', self.purifier) )
        if self.neutralizer > self.purifier:
            reasons.append( '%s %s %s %s %s' % (self.name.ljust(16), self.date, str(self.neutralizer).rjust(8), 'high neutralizer, max =', self.purifier) )
        if (self.translator/15) > self.hacker:
            reasons.append( '%s %s %s %s %s' % (self.name.ljust(16), self.date, str(self.translator).rjust(8), 'high translator, max =', self.hacker*15) )

        #if self.min_ap-self.apdiff > self.ap:
        #    reasons.append( '%s : %s %s | Reported AP %s, Calulated min AP %s' % (str(self.min_ap-self.ap).rjust(10), self.name.ljust(16), self.date, str(self.ap).rjust(8), self.min_ap) )
        #elif not reasons:
        #    exec_mysql("UPDATE agents SET apdiff={0} WHERE `name`='{1}';".format(self.min_ap-self.ap, self.name))

        return reasons

    def save(self):
        self.flag, self.min_ap # hack to make sure these are in the cache
        
        sql = '''INSERT INTO `stats`
                 SET idagents={agent_id},
                     `date`='{date}',
                     `level`='{level}',
                     ap='{ap}',
                     explorer='{explorer}',
                     seer='{seer}',
                     trekker='{trekker}',
                     builder='{builder}',
                     connector='{connector}',
                     `mind-controller`='{mind_controller}',
                     illuminator='{illuminator}',
                     recharger='{recharger}',
                     liberator='{liberator}',
                     pioneer='{pioneer}',
                     engineer='{engineer}',
                     purifier='{purifier}',
                     guardian='{guardian}',
                     specops='{specops}',
                     hacker='{hacker}',
                     translator='{translator}',
                     sojourner='{sojourner}',
                     recruiter='{recruiter}',
                     collector='{collector}',
                     binder='{binder}',
                     `country-master`='{country_master}',
                     neutralizer='{neutralizer}',
                     disruptor='{disruptor}',
                     salvator='{salvator}',
                     smuggler='{smuggler}',
                    `link-master`='{link_master}',
                     controller='{controller}',
                     `field-master`='{field_master}',
                     flag={flag},
                     `min-ap`='{min_ap}'
                 ON DUPLICATE KEY UPDATE `level`='{level}',
                                         ap='{ap}',
                                         explorer='{explorer}',
                                         seer='{seer}',
                                         trekker='{trekker}',
                                         builder='{builder}',
                                         connector='{connector}',
                                         `mind-controller`='{mind_controller}',
                                         illuminator='{illuminator}',
                                         recharger='{recharger}',
                                         liberator='{liberator}',
                                         pioneer='{pioneer}',
                                         engineer='{engineer}',
                                         purifier='{purifier}',
                                         guardian='{guardian}',
                                         specops='{specops}',
                                         hacker='{hacker}',
                                         translator='{translator}',
                                         sojourner='{sojourner}',
                                         recruiter='{recruiter}',
                                         collector='{collector}',
                                         binder='{binder}',
                                         `country-master`='{country_master}',
                                         neutralizer='{neutralizer}',
                                         disruptor='{disruptor}',
                                         salvator='{salvator}',
                                         smuggler='{smuggler}',
                                        `link-master`='{link_master}',
                                         controller='{controller}',
                                         `field-master`='{field_master}',
                                         flag={flag},
                                         `min-ap`='{min_ap}';'''.format(**self.__dict__)
        exec_mysql(sql)

    def __repr__(self):
        return '<Stat: {} {}>'.format(self.name, self.date)

# date >= game_start
# today >= date
# connector >= mind_controller/2
# hacker+builder+engineer+connector >= explorer
# explorer >= pioneer
# builder >= liberator
# liberator >= pioneer
# disruptor >= salvator/2
# purifier >= disruptor
# purifier >= neutralizer
# hacker >= translator/15
# min_ap = liberator*125 + min(-(-max(0,(builder-liberator*8))/7)*65, -(-max(0,(builder-liberator*8))/8)*125) + connector*313 + mind_controller*1250 + liberator*500 + engineer*125 + purifier*75 + recharger/15000*10 + disruptor*187 + salvator*750
## requirement[level] <= ap
