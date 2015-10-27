from util import exec_mysql
import datetime
import logging
from itertools import chain
from dateutil.parser import parse

today = datetime.date.today()
sojourner_start = datetime.date(2015, 3, 5)
game_start = datetime.date(2012, 11, 15)

class Stat(object):
    def __init__(self, **kwargs):
        self.date = parse(kwargs['Last submission']).date() if not kwargs['Last submission'].startswith('0') else '0/0/0'
        self.name = kwargs['Agent name']
        self.faction = kwargs['Faction']
        self.level = int(kwargs['Level'])
        self.ap = int(kwargs['ap'])
        self.explorer = int(kwargs['explorer'])
        self.seer = int(kwargs['seer'])
        self.collector = int(kwargs['collector'])
        self.trekker = int(kwargs['trekker'])
        self.builder = int(kwargs['builder'])
        self.connector = int(kwargs['connector'])
        self.mind_controller = int(kwargs['mind-controller'])
        self.illuminator = int(kwargs['illuminator'])
        self.binder = int(kwargs['binder'])
        self.country_master = int(kwargs['country-master'])
        self.recharger = int(kwargs['recharger'])
        self.liberator = int(kwargs['liberator'])
        self.pioneer = int(kwargs['pioneer'])
        self.engineer = int(kwargs['engineer'])
        self.purifier = int(kwargs['purifier'])
        self.neutralizer = int(kwargs['neutralizer'])
        self.disruptor = int(kwargs['disruptor'])
        self.salvator = int(kwargs['salvator'])
        self.guardian = int(kwargs['guardian'])
        self.smuggler = int(kwargs['smuggler'])
        self.link_master = int(kwargs['link-master'])
        self.controller = int(kwargs['controller'])
        self.field_master = int(kwargs['field-master'])
        self.specops = int(kwargs['specops'])
        self.hacker = int(kwargs['hacker'])
        self.translator = int(kwargs['translator'])
        self.sojourner = int(kwargs['sojourner'])
        self.recruiter = int(kwargs['recruiter'])

        agent_id = exec_mysql("SELECT idagents FROM agents WHERE name = '{0}';".format(self.name))
        if agent_id:
            self.agent_id = agent_id[0][0]
        else:
            sql = '''INSERT INTO `agents` SET `name`='{0}', `faction`='{1}';'''.format(self.name, self.faction)
            exec_mysql(sql)
            self.agent_id = exec_mysql("SELECT idagents FROM agents WHERE name = '{0}';".format(self.name))[0][0]
            
        self.apdiff = 0

    def get_badges(self):
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
                      'hacker': [2000, 10000, 30000, 100000, 200000],
                      'translator': [200, 2000, 6000, 20000, 50000],
                      'sojourner': [15, 30, 60, 180, 360],
                      'recruiter': [2, 10, 25, 50, 100]}

        result = {}
        for category, ranks in categories.items():
            current = 'Locked'
            multiplier = 1
            for rank, badge in zip(ranks, ['Bronze', 'Silver', 'Gold', 'Platinum', 'Onyx']):
                if getattr(self, category) != '-' and int(getattr(self, category)) >= rank:
                    current = badge
                if current == 'Onyx':
                    multiplier = getattr(self, category) // rank
                    if multiplier > 2: 
                        current = '%sx %s' % (multiplier, current)
            result[category] = current
        return result

    def min_level(self):
        ranks = ['Onyx', 'Platinum', 'Gold', 'Silver', 'Bronze', 'Locked']
        sorted_badges = sorted([a.split(' ')[-1] for a in self.get_badges().values()], key=lambda x: ranks.index(x))
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

    @property
    def flag(self):
        try:
            return self._flag
        except AttributeError:
            self._flag = bool(self.validate())
            return self._flag

    def validate(self):
        if self.date == '0/0/0': return ['date missing']

        max_sojourner = (self.date - sojourner_start).days + 1
        max_guardian = (self.date - game_start).days + 1
        min_level = self.min_level()
        self.min_ap = self.liberator*125 + min(-(-max(0,(self.builder-self.liberator*8))//7)*65, -(-max(0,(self.builder-self.liberator*8))//8)*125) \
                      + self.connector*313 + self.mind_controller*1250 + self.liberator*500 + self.engineer*125 \
                      + self.purifier*75 + self.recharger//15000*10 + self.disruptor*187 + self.salvator*750

        apdiff = exec_mysql("SELECT apdiff FROM agents WHERE `name` = '{0}';".format(self.name))
        if apdiff: self.apdiff = apdiff[0][0]

        reasons = []
        #if min_level > self.level:
        #    reasons.append( 'reported level too low: %s Min: %s' % (self.level, min_level) )
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

        if self.min_ap-self.apdiff > self.ap:
            reasons.append( '%s : %s %s | Reported AP %s, Calulated min AP %s' % (str(self.min_ap-self.ap).rjust(10), self.name.ljust(16), self.date, str(self.ap).rjust(8), self.min_ap) )
        elif not reasons:
            exec_mysql("UPDATE agents SET apdiff={0} WHERE `name`='{1}';".format(self.min_ap-self.ap, self.name))

        return reasons

    def save(self):
        sql = '''INSERT INTO `stats`
                 SET idagents={agent_id},
                     `date`='{date}',
                     `level`='{level}',
                     flag={flag},
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
                     `field-master`='{field_master}'
                 ON DUPLICATE KEY UPDATE `level`='{level}',
                                         flag={flag},
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
                                         `field-master`='{field_master}';'''.format(flag=self.flag, **self.__dict__)
        exec_mysql(sql)

    def load(self, name, date=None):
        #be sure this is an empty object first
        pass

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
# requirement[level] <= ap
