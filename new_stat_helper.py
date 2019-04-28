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
#copy the new stat(s) from the table and paste them here as is

a = '''dark_xm_threat
Dark XM Total Link Length
	5,000 	50,000 	250,000	N/A	N/A'''

it = iter(a.split('\n'))

create_code(list(zip(it, it, it)))
