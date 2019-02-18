def create_code(new_stats):
    templates = ["  `{statname}` bigint(20) unsigned DEFAULT NULL,\n",
                 "  `stats`.`{statname}`,\n",
                 ", {statnodash}",
                 "        self.{statnodash} = row.{statnodash}\n",
                 "        self.{statnodash} = row['{statname}']\n",
                 "                     {statbacktick}='{{{statnodash}}}',\n",
                 "                                         {statbacktick}='{{{statnodash}}}',\n",
                 "                   '{statname}': '({description})',\n",
                 "                  '{statname}': [{tiers}],\n",
                 "               '{statnodash}',\n",
                 ", {statname}",
                 "{{{{ high_scores(chart{stattemplate}) -}}}}\n"]
    for template in templates:
        for stat, description, tiers in new_stats:
            stat_dict = {'description': description,
                         'tiers': ', '.join([tier.strip() for tier in tiers.split('\t')[1:]]),
                         'statname': stat,
                         'statnodash': stat.replace('-', '_'),
                         'statbacktick': f'`{stat}`' if '-' in stat else stat,
                         'stattemplate': f"['{stat}']" if '-' in stat else f'.{stat}',
                        }
            print(template.format(**stat_dict), end='')
        print('\n')


#https://www.agent-stats.com/faq.php

a = '''prime_challenge
Prime Challenges
	1 	2 	3 	4	N/A
stealth_ops
Stealth Ops Missions
	1 	3 	6 	10 	20
opr_live
OPR Live Events
	1 	3 	6 	10 	20
ocf
Clear Field Events
	1 	3 	6 	10 	20
intel_ops
Intel Ops Missions
	1 	3 	6 	10 	20
ifs
First Saturday Events
	1 	6 	12 	24 	36'''

it = iter(a.split('\n'))

create_code(list(zip(it, it, it)))
