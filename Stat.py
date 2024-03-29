from util import exec_mysql
import datetime
import logging
from itertools import chain
from dateutil.parser import parse # pip install python-dateutil
from collections import namedtuple
from cached_property import cached_property # pip install cached-property


today = datetime.date.today()
sojourner_start = datetime.date(2015, 3, 5)
game_start = datetime.date(2012, 11, 15)

fields = '''name, date, flag, min_ap, lifetime_ap, recursions, ap, level, explorer,
discoverer, seer, recon, scout, trekker, builder, connector, mind_controller, illuminator,
recharger, liberator, pioneer, engineer, purifier, guardian, specops, missionday,
nl_1331_meetups, cassandra_neutralizer, hacker, translator, sojourner, recruiter,
collector, binder, country_master, neutralizer, disruptor, salvator, smuggler,
link_master, controller, field_master, magnusbuilder, prime_challenge, stealth_ops,
opr_live, ocf, intel_ops, urban_ops, ifs, dark_xm_threat, myriad_hack, aurora_glyph,
umbra_deploy, didact_field, drone_explorer, drone_distance, drone_recalls, drone_sender,
maverick, scout_controller, crafter, bb_combatant, red_disruptor, red_purifier,
red_neutralizer, reclaimer, hack_the_world202104, epoch, matryoshka_links, operation_sentinel,
second_sunday, eos_imprint, overclocker, operation_chronos, cryptic_memories_op, research_bounties, 
research_days'''

Row = namedtuple('Row', fields)

class Stat(object):
    def load(self, name):
        if not name.startswith('@'):
            name = '@' + name
        self.db_load(exec_mysql("call FindAgentByName('{name}');".format(name=name))[-1])

    def db_load(self, row): # ATTENTION: DO NOT simply use 'SELECT * FROM stats;' here. It will end in tears.
        row = Row(*row) # your boat...

        self.name = row.name
        self.date = row.date if row.date else datetime.date(1000, 1, 1)
        #self.flag = row.flag
        #self.min_ap = row.min_ap
        self.ap = row.ap
        self.lifetime_ap = row.lifetime_ap
        self.recursions = row.recursions
        self.level = row.level
        self.explorer = row.explorer
        self.discoverer = row.discoverer
        self.seer = row.seer
        self.recon = row.recon
        self.scout = row.scout
        self.collector = row.collector
        self.trekker = row.trekker
        self.builder = row.builder
        self.connector = row.connector
        self.mind_controller = row.mind_controller
        self.illuminator = row.illuminator
        self.binder = row.binder
        self.country_master = row.country_master
        self.recharger = row.recharger
        self.liberator = row.liberator
        self.pioneer = row.pioneer
        self.engineer = row.engineer
        self.purifier = row.purifier
        self.neutralizer = row.neutralizer
        self.disruptor = row.disruptor
        self.salvator = row.salvator
        self.guardian = row.guardian
        self.smuggler = row.smuggler
        self.link_master = row.link_master
        self.controller = row.controller
        self.field_master = row.field_master
        self.specops = row.specops
        self.missionday = row.missionday
        self.nl_1331_meetups = row.nl_1331_meetups
        self.hacker = row.hacker
        self.translator = row.translator
        self.sojourner = row.sojourner
        self.recruiter = row.recruiter
        self.prime_challenge = row.prime_challenge
        self.stealth_ops = row.stealth_ops
        self.opr_live = row.opr_live
        self.ocf = row.ocf
        self.intel_ops = row.intel_ops
        self.urban_ops = row.urban_ops
        self.ifs = row.ifs
        self.drone_explorer = row.drone_explorer
        self.drone_distance = row.drone_distance
        self.drone_recalls = row.drone_recalls
        self.drone_sender = row.drone_sender
        self.maverick = row.maverick
        self.scout_controller = row.scout_controller
        self.crafter = row.crafter
        self.bb_combatant = row.bb_combatant
        self.red_disruptor = row.red_disruptor
        self.red_purifier = row.red_purifier
        self.red_neutralizer = row.red_neutralizer
        self.reclaimer = row.reclaimer
        self.epoch = row.epoch
        self.matryoshka_links = row.matryoshka_links
        self.operation_sentinel = row.operation_sentinel
        self.second_sunday = row.second_sunday
        self.eos_imprint = row.eos_imprint
        self.overclocker = row.overclocker
        self.operation_chronos = row.operation_chronos
        self.cryptic_memories_op = row.cryptic_memories_op
        self.research_bounties = row.research_bounties
        self.research_days = row.research_days

        # obsolete stats
        self.hack_the_world202104 = row.hack_the_world202104
        self.cassandra_neutralizer = row.cassandra_neutralizer
        self.magnusbuilder = row.magnusbuilder
        self.dark_xm_threat = row.dark_xm_threat
        self.myriad_hack = row.myriad_hack
        self.aurora_glyph = row.aurora_glyph
        self.umbra_deploy = row.umbra_deploy
        self.didact_field = row.didact_field

        if str(self.name).startswith('@'):
            self.agent_id = exec_mysql("SELECT idagents FROM agents WHERE name = '{0}';".format(self.name[:16]))[0][0]
        else: # probably good enough, but if this still blows up then make sure it's a numeric id and not just a name missing its @
            self.agent_id = self.name
            self.name = exec_mysql("SELECT name FROM agents WHERE idagents = '{0}';".format(self.agent_id))[0][0]

    def table_load(self, **row):
        self.date = parse(row['last_submit'] if row['last_submit'] and not row['last_submit'].startswith('0') else '1000/1/1').date()
        self.name = row['name'][:16]
        self.faction = row['faction'] if row['faction'] else 'UNK'
        self.level = row.get('level', 0)
        self.lifetime_ap = row.get('lifetime_ap', 0)
        self.recursions = row.get('recursions', 0)
        self.ap = row.get('ap', 0)
        self.explorer = row.get('explorer', 0)
        self.discoverer = row.get('discoverer', 0)
        self.seer = row.get('seer', 0)
        self.recon = row.get('recon', 0)
        self.scout = row.get('scout', 0)
        self.collector = row.get('collector', 0)
        self.trekker = row.get('trekker', 0)
        self.builder = row.get('builder', 0)
        self.connector = row.get('connector', 0)
        self.mind_controller = row.get('mind-controller', 0)
        self.illuminator = row.get('illuminator', 0)
        self.binder = row.get('binder', 0)
        self.country_master = row.get('country-master', 0)
        self.recharger = row.get('recharger', 0)
        self.liberator = row.get('liberator', 0)
        self.pioneer = row.get('pioneer', 0)
        self.engineer = row.get('engineer', 0)
        self.purifier = row.get('purifier', 0)
        self.neutralizer = row.get('neutralizer', 0)
        self.disruptor = row.get('disruptor', 0)
        self.salvator = row.get('salvator', 0)
        self.guardian = row.get('guardian', 0)
        self.smuggler = row.get('smuggler', 0)
        self.link_master = row.get('link-master', 0)
        self.controller = row.get('controller', 0)
        self.field_master = row.get('field-master', 0)
        self.specops = row.get('specops', 0)
        self.missionday = row.get('missionday', 0)
        self.nl_1331_meetups = row.get('nl-1331-meetups', 0)
        self.hacker = row.get('hacker', 0)
        self.translator = row.get('translator', 0)
        self.sojourner = row.get('sojourner', 0)
        self.recruiter = row.get('recruiter', 0)
        self.prime_challenge = row.get('prime_challenge', 0)
        self.stealth_ops = row.get('stealth_ops', 0)
        self.opr_live = row.get('opr_live', 0)
        self.ocf = row.get('ocf', 0)
        self.intel_ops = row.get('intel_ops', 0)
        self.urban_ops = row.get('urban_ops', 0)
        self.ifs = row.get('ifs', 0)
        self.drone_explorer = row.get('drone_explorer', 0)
        self.drone_distance = row.get('drone_distance', 0)
        self.drone_recalls = row.get('drone_recalls', 0)
        self.drone_sender = row.get('drone_sender', 0)
        self.maverick = row.get('maverick', 0)
        self.scout_controller = row.get('scout_controller', 0)
        self.crafter = row.get('crafter', 0)
        self.bb_combatant = row.get('bb_combatant', 0)
        self.red_disruptor = row.get('red-disruptor', 0)
        self.red_purifier = row.get('red-purifier', 0)
        self.red_neutralizer = row.get('red-neutralizer', 0)
        self.reclaimer = row.get('reclaimer', 0)
        self.epoch = row.get('epoch', 0)
        self.operation_sentinel = row.get('operation_sentinel', 0)
        self.second_sunday = row.get('second_sunday', 0)
        self.eos_imprint = row.get('eos_imprint', 0)
        self.overclocker = row.get('overclocker', 0)
        self.operation_chronos = row.get('operation_chronos', 0)
        self.cryptic_memories_op = row.get('cryptic_memories_op', 0)
        self.research_bounties = row.get('research_bounties', 0)
        self.research_days = row.get('research_days', 0)

        agent_id = exec_mysql("SELECT idagents FROM agents WHERE name = '{0}';".format(self.name))
        if agent_id:
            self.agent_id = agent_id[0][0]
        else:
            sql = '''INSERT INTO `agents` SET `name`='{0}', `faction`='{1}';'''.format(self.name, self.faction)
            exec_mysql(sql)
            logging.info('new entry created for {} in agents table'.format(self.name))
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
    def reasons(self):
        return self.validate()

    @cached_property
    def flag(self):
        return bool(self.reasons)

    def validate(self):
        if str(self.date) == '1000-01-01': return ['date missing']

        max_sojourner = (self.date - sojourner_start).days + 1
        max_guardian = (self.date - game_start).days + 1

        apdiff = exec_mysql("SELECT apdiff FROM agents WHERE `name` = '{0}';".format(self.name))
        if apdiff: self.apdiff = apdiff[0][0]

        reasons = []
        # this seems to be a more common bug, and until there is some action agents can take to fix it, it wont be flagged
        #if self.min_level > self.level + 1: # +1 is for special case where agents just dinged and scanner hasn't caught up yet. better to let some slip through than to flag an exited agent's ding
        #    reasons.append( 'reported level %s < %s' % (self.level, self.min_level) )
        if self.ap > self.lifetime_ap:
            reasons.append( 'ap:lifetime_ap %s > %s' % (self.ap, self.lifetime_ap) )
        if self.guardian > max_guardian:
            reasons.append( 'guardian %s > %s' % (self.guardian, max_guardian) )
        if self.sojourner > max(0, max_sojourner):
            reasons.append( 'sojourner %s > %s' % (self.sojourner, max_sojourner) )
        if game_start > self.date:
            reasons.append( 'date %s < %s' % (self.date, game_start) )
        if self.date > today+datetime.timedelta(days=1):
            reasons.append( 'date %s > %s' % (self.date, today+datetime.timedelta(days=1)) )
        if (self.mind_controller/2) > self.connector:
            reasons.append( 'connector:mind controller %s < %s/2' % (self.connector, self.mind_controller) )
        if self.explorer > self.hacker+self.builder+self.engineer+self.connector:
            reasons.append( 'explorer:H+B+E+C %s > %s' % (self.explorer, self.hacker+self.builder+self.engineer+self.connector) )
        if self.pioneer > self.explorer:
            reasons.append( 'pioneer:explorer %s > %s' % (self.pioneer, self.explorer) )
        if self.pioneer > self.liberator:
            reasons.append( 'pioneer:liberator %s > %s' % (self.pioneer, self.liberator) )
        if self.liberator > self.builder:
            reasons.append( 'liberator:builder %s > %s' % (self.liberator, self.builder) )
        if (self.salvator/2) > self.disruptor:
            reasons.append( 'disruptor:salvator %s < %s/2' % (self.disruptor, self.salvator) )
        if self.disruptor > self.purifier:
            reasons.append( 'disruptor:purifier %s > %s' % (self.disruptor, self.purifier) )
        if self.neutralizer > self.purifier:
            reasons.append( 'neutralizer:purifier %s > %s' % (self.neutralizer, self.purifier) )
        if (self.translator/15) > self.hacker:
            reasons.append( 'hacker:translator %s < %s/15' % (self.hacker, self.translator) )
        if self.seer > self.discoverer:
            reasons.append( 'seer:discoverer %s > %s' % (self.seer, self.discoverer) )

        # there can be multiple crafting capsules now. this signal is very weak even if recalibrated
        # if (self.crafter*2) > self.trekker:
        #     reasons.append( 'trekker:crafter %s < %s*2' % (self.trekker, self.crafter) )

        # there was a missionday where they didnt require missions at all. 100 UPV would get you the badge
        # http://www.pref.iwate.jp/dbps_data/_material_/_files/000/000/031/399/morioka0621.pdf (in japanese, on page 2)
        #if self.missionday > self.specops:
        #    reasons.append( 'missionday:specops %s > %s' % (self.missionday, self.specops) )

        # this catches faction flippers unfortunately
        #if self.min_ap > self.lifetime_ap:
        #    reasons.append( 'lifetime_ap:min_ap %s < %s' % (self.lifetime_ap, self.min_ap) )

        #if self.apdiff > self.lifetime_ap-self.min_ap:
        #    reasons.append( 'apdiff %s > %s' % (self.apdiff, self.lifetime_ap-self.min_ap) )

        if not reasons:
            exec_mysql("UPDATE agents SET apdiff={0} WHERE `name`='{1}';".format(self.lifetime_ap-self.min_ap, self.name))

        return reasons

    def save(self):
        self.flag, self.min_ap # hack to make sure these are in the cache

        sql = '''INSERT INTO `stats`
                 SET idagents={agent_id},
                     `date`='{date}',
                     `level`='{level}',
                     ap='{ap}',
                     lifetime_ap='{lifetime_ap}',
                     recursions='{recursions}',
                     explorer='{explorer}',
                     discoverer='{discoverer}',
                     seer='{seer}',
                     recon='{recon}',
                     scout='{scout}',
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
                     missionday='{missionday}',
                     `nl-1331-meetups`='{nl_1331_meetups}',
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
                     prime_challenge='{prime_challenge}',
                     stealth_ops='{stealth_ops}',
                     opr_live='{opr_live}',
                     ocf='{ocf}',
                     intel_ops='{intel_ops}',
                     urban_ops='{urban_ops}',
                     ifs='{ifs}',
                     drone_explorer='{drone_explorer}',
                     drone_distance='{drone_distance}',
                     drone_recalls='{drone_recalls}',
                     drone_sender='{drone_sender}',
                     maverick='{maverick}',
                     scout_controller='{scout_controller}',
                     crafter='{crafter}',
                     bb_combatant='{bb_combatant}',
                     `red-disruptor`='{red_disruptor}',
                     `red-purifier`='{red_purifier}',
                     `red-neutralizer`='{red_neutralizer}',
                     reclaimer='{reclaimer}',
                     epoch='{epoch}',
                     operation_sentinel='{operation_sentinel}',
                     second_sunday='{second_sunday}',
                     eos_imprint='{eos_imprint}',
                     overclocker='{overclocker}',
                     operation_chronos='{operation_chronos}',
                     cryptic_memories_op='{cryptic_memories_op}',
                     research_bounties='{research_bounties}',
                     research_days='{research_days}',

                     flag={flag},
                     `min-ap`='{min_ap}'
                 ON DUPLICATE KEY UPDATE `level`='{level}',
                                         ap='{ap}',
                                         lifetime_ap='{lifetime_ap}',
                                         recursions='{recursions}',
                                         explorer='{explorer}',
                                         discoverer='{discoverer}',
                                         seer='{seer}',
                                         recon='{recon}',
                                         scout='{scout}',
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
                                         missionday='{missionday}',
                                         `nl-1331-meetups`='{nl_1331_meetups}',
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
                                         prime_challenge='{prime_challenge}',
                                         stealth_ops='{stealth_ops}',
                                         opr_live='{opr_live}',
                                         ocf='{ocf}',
                                         intel_ops='{intel_ops}',
                                         urban_ops='{urban_ops}',
                                         ifs='{ifs}',
                                         drone_explorer='{drone_explorer}',
                                         drone_distance='{drone_distance}',
                                         drone_recalls='{drone_recalls}',
                                         drone_sender='{drone_sender}',
                                         maverick='{maverick}',
                                         scout_controller='{scout_controller}',
                                         crafter='{crafter}',
                                         bb_combatant='{bb_combatant}',
                                         `red-disruptor`='{red_disruptor}',
                                         `red-purifier`='{red_purifier}',
                                         `red-neutralizer`='{red_neutralizer}',
                                         reclaimer='{reclaimer}',
                                         epoch='{epoch}',
                                         operation_sentinel='{operation_sentinel}',
                                         second_sunday='{second_sunday}',
                                         eos_imprint='{eos_imprint}',
                                         overclocker='{overclocker}',
                                         operation_chronos='{operation_chronos}',
                                         cryptic_memories_op='{cryptic_memories_op}',
                                         research_bounties='{research_bounties}',
                                         research_days='{research_days}',
                                         
                                         flag={flag},
                                         `min-ap`='{min_ap}';'''.format(**self.__dict__)
        self.changed = exec_mysql(sql)

    def __repr__(self):
        return '<Stat: {} {}>'.format(self.name, self.date)

# lifetime_ap >= ap
# date >= game_start
# today >= date
# discoverer >= seer
# connector >= mind_controller/2
# hacker+builder+engineer+connector >= explorer
# explorer >= pioneer
# builder >= liberator
# liberator >= pioneer
# disruptor >= salvator/2
# purifier >= disruptor
# purifier >= neutralizer
# hacker >= translator/15
## trekker >= crafter*2
## builder >= magnusbuilder
## explorer >= magnusbuilder/8
## translator >= aurora_glyph
## missionday > specops
# min_ap = liberator*125 + min(-(-max(0,(builder-liberator*8))/7)*65, -(-max(0,(builder-liberator*8))/8)*125) + connector*313 + mind_controller*1250 + liberator*500 + engineer*125 + purifier*75 + recharger/15000*10 + disruptor*187 + salvator*750
## requirement[level] <= ap
