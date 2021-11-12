import json

def getconfig(cfgfile):
    cfg = {}
    
    with open(cfgfile) as f:
        cfg = json.load(f)

    # Set defaults if need to be.
    if 'BotMsgStayTime' not in cfg:
        cfg['BotMsgStayTime'] = 10.0

    if 'UpdateTime' not in cfg:
        cfg['UpdateTime'] = 60.0

    if 'AppendGuildName' not in cfg:
        cfg['AppendGuildName'] = True

    if 'AllowMentions' not in cfg:
        cfg['AllowMentions'] = False
    
    return cfg