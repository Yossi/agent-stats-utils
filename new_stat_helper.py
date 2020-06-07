def create_code(new_stats):
    templates = {
        'schema.sql > create table': "  `{statname}` bigint(20) unsigned DEFAULT NULL,\n",
        'schema.sql > stored procedure': "  `stats`.`{statname}`,\n",
        'Stat.py > fields': ", {statnodash}",
        'Stat.py > db_load()': "        self.{statnodash} = row.{statnodash}\n",
        'Stat.py > table_load()': "        self.{statnodash} = row['{statname}']\n",
        'Stat.py > save(1)': "                     {statbacktick}='{{{statnodash}}}',\n",
        'Stat.py > save(2)': "                                         {statbacktick}='{{{statnodash}}}',\n",
        'agent_stats.py > get_stats() > definitions': "                   '{statname}': '({description})',\n",
        'agent_stats.py > get_badges() > categories (or 3 tier categories)': "                  '{statname}': [{tiers}],\n",
        'agent_stats.py > summary() > headers': "               '{statnodash}',\n",
        'agent_stats.py > summary() > sql_before & sql_after': ", {statname}",
        'templates': "{{{{ high_scores(chart{stattemplate}) -}}}}\n"}
    for place, template in templates.items():
        print(place + ':')
        for stat, description, tiers in new_stats:
            stat_dict = {'description': description,
                         'tiers': ', '.join([tier.strip().replace(',', '') for tier in tiers.split('\t')[1:] if tier != 'N/A']),
                         'statname': stat,
                         'statnodash': stat.replace('-', '_'),
                         'statbacktick': f'`{stat}`' if '-' in stat else stat,
                         'stattemplate': f"['{stat}']" if '-' in stat else f'.{stat}',
                        }
            print(template.format(**stat_dict), end='')
        print('\n')


#https://www.agent-stats.com/faq.php
#copy the new stat(s) from the table and paste them here as is

a = '''drone_explorer
Unique Portals Drone Visited
	100 	1,000 	2,000 	10,000 	30,000
drone_distance
Furthest Drone Flight Distance
	10 	50 	100 	250 	500
drone_recalls
Forced Drone Recalls
	50 	100 	250 	500 	1,000
drone_hacker
Drone Hacks
	2,000 	10,000 	30,000 	100,000 	200,000'''

it = iter(a.split('\n'))

create_code(list(zip(it, it, it)))
