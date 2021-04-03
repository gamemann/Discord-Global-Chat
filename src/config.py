import json

def getconfig(cfgfile):
    cfg = {}

    # Set defaults.
    cfg['BotMsgStayTime'] = 10.0
    cfg['UpdateTime'] = 60.0
    cfg['AppendGuildName'] = True
    
    with open(cfgfile) as f:
        cfg = json.load(f)
    
    return cfg