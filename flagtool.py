import sys
from util import exec_mysql, cm
from secrets import dbconfig
cm.set_credentials(dbconfig)

#call FindAgentByName('@agent');

def set_flag(agent, date, flag=1):
    #date needs to be yyyy-mm-dd
    if not agent.startswith('@'):
        agent = '@' + agent
    print(agent)
    sql1 = "SELECT idagents FROM agents WHERE `name`='{}';".format(agent)
    print(sql1)
    agentid = exec_mysql(sql1)[0][0]
    print(agentid)
    
    sql2 = "UPDATE `agent_stats`.`stats` SET `flag`='{flag}' WHERE `idagents`='{agentid}' and`date`='{date}';".format(agentid=agentid, date=date, flag=flag)
    print(sql2)
    exec_mysql(sql2)
    print('done')

if __name__ == '__main__':
    # python flagtool.py agent yyyy-mm-dd
    set_flag(*sys.argv[1:])

