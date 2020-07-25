import bs
import bsSpaz
import bsInternal

gSettingsEnabled = (hasattr(bs, "get_setting") and hasattr(bs, "set_setting"))

if gSettingsEnabled: skins = bs.get_setting("skins", {})
else: skins = {}

def get_format_skin_name(name):
    if name == "B-9000": return "cyborg"
    elif name == "Agent Johnson": return "agent"
    elif name == "Santa Claus": return "santa"
    elif name == "Pixel": return "pixie"
    elif name == "Pascal": return "penguin"
    elif name == "Easter Bunny": return "bunny"
    elif name == "Taobao Mascot": return "taobao"
    elif name == "Jack Morgan": return "pirate"
    elif name == "Bernard": return "bear"
    else:
        if len(name.split(" ")) > 1: return name.lower().replace(".", "").replace("-","").split(" ")[1 if len(name.split(" ")[1]) > len(name.split(" ")[0]) else 0]
        else: return name.lower().replace(".", "").replace("-","")

def get_unformat_skin_name(name):
    if name == "cyborg": return "B-9000"
    elif name == "agent": return "Agent Johnson"
    elif name == "santa": return "Santa Claus"
    elif name == "pixie": return "Pixel"
    elif name == "penguin": return "Pascal"
    elif name == "bunny": return "Easter Bunny"
    elif name == "taobao": return "Taobao Mascot"
    elif name == "pirate": return "Jack Morgan"
    elif name == "bear": return "Bernard"
    elif name in ['bomb.man', 'tnt.man', 'tnt', 'invincible', 'shard', 'i']: return "Bones"
    else:
        for i in bsSpaz.appearances.keys():
            if name.lower() in i.lower().replace(".", "").replace("-",""): return i
    return None

def skin(media={}, player=None):
    a = bsInternal._getForegroundHostActivity()
    if a is not None:
        with bs.Context(a):
            if player is not None:
                if isinstance(player, int) and hasattr(a, "players") and len(a.players) > player: player=a.players[player]
                a=None
                if isinstance(player, bs.Player) and player.exists() and player.isAlive(): a=player.actor.node
                if isinstance(player, bs.Node) and player.exists(): a=player
                if a is not None:
                    a.headModel=media.get("headModel", a.headModel)
                    a.pelvisModel=media.get("pelvisModel", a.pelvisModel)
                    a.upperArmModel=media.get("upperArmModel", a.upperArmModel)
                    a.foreArmModel=media.get("foreArmModel", a.foreArmModel)
                    a.handModel=media.get("handModel", a.handModel)
                    a.upperLegModel=media.get("upperLegModel", a.upperLegModel)
                    a.lowerLegModel=media.get("lowerLegModel", a.lowerLegModel)
                    a.torsoModel=media.get("torsoModel", a.torsoModel)
                    a.toesModel=media.get("toesModel", a.toesModel)
                    a.colorTexture=media.get("colorTexture", a.colorTexture)
                    a.colorMaskTexture=media.get("colorMaskTexture", a.colorMaskTexture)
                    a.jumpSounds=media.get('jumpSounds', a.jumpSounds)
                    a.attackSounds=media.get('attackSounds', a.attackSounds)
                    a.impactSounds=media.get('impactSounds', a.impactSounds)
                    a.deathSounds=media.get('deathSounds', a.deathSounds)
                    a.pickupSounds=media.get('pickupSounds', a.pickupSounds)
                    a.fallSounds=media.get('fallSounds', a.fallSounds)
                    a.style=media.get("style", a.style)
                    a.name=media.get("name", a.name)
                    a.color=media.get("color", a.color)
                    a.highlight=media.get("highlight", a.highlight)
                    return True #if we do it, send True
    return False #send False if something went wrong

def change_skin(skin=None, players=[]):
    global skins
    a=bsInternal._getForegroundHostActivity()
    if a is not None and isinstance(players, list) and len(players) > 0:
        for i in players:
            if isinstance(i, int) and len(a.players) > i: i = a.players[i] if a.players[i].exists() else None
            if isinstance(i, bs.Player) and i.exists(): i = str(i.getInputDevice()._getAccountName(True).encode('utf-8'))
            if isinstance(i, str): i = i.decode('utf-8')
            if isinstance(i, unicode):
                skins.update({i: str(skin)})
                print(skins)
                if gSettingsEnabled: bs.set_setting("skins", skins)

def delete_skin(player=None):
    global skins
    a = bsInternal._getForegroundHostActivity()
    if a is not None:
        if isinstance(player, int) and len(a.players) > int(player): player = a.players[player]
        if isinstance(player, bs.Node) and player.exists() and hasattr(player, "getDelegate"): player = player.getDelegate().getPlayer()
        if isinstance(player, bs.Player): player = str(player.getInputDevice()._getAccountName(True).encode("utf-8"))    
        if isinstance(player, str): player = player.decode('utf-8')
        if isinstance(player, unicode):
            if skins.get(player) is not None:
                skins.pop(player)
                if gSettingsEnabled: bs.set_setting("skins", skins)

def check_skin(*args):
    global skins
    data={}
    for i in args:
        if isinstance(i, str) or isinstance(i, unicode): data.update({"account": i})
        if isinstance(i, bs.Node): data.update({"node":i})
        if isinstance(i, bs.Player): data.update({"player":i})
    if "account" in data:
        if isinstance(data["account"], str): data["account"] = str(data["account"].encode('utf-8')).decode('utf-8')
        if skins.get(data["account"]) is not None: # settings, and data from it can be only in unicode
            skin_name = skins[data["account"]]
            a=None # get player node
            if data.get("player") is not None and data["player"].exists(): a = data["player"].actor.node
            elif data.get("node") is not None and data["node"].exists(): a = data["node"]
            usualSounds=[bs.getSound(s) for s in ["sparkle01", "sparkle02", "sparkle03"]] #set standart skin utils
            result = {"headModel": None, "pelvisModel": None, "upperArmModel": None, \
                "foreArmModel": None, "handModel": None, "upperLegModel": None, \
                "lowerLegModel": None, "toesModel": None, "style": "bones", \
                "name": "", "color": (1, 1, 1), "highlight": (1, 1, 1), "torsoModel": None, \
                "jumpSounds": usualSounds, "attackSounds": usualSounds, \
                "impactSounds": usualSounds, "deathSounds": usualSounds, \
                "pickupSounds": usualSounds, "fallSounds": usualSounds
            }
            if skin_name == 'tnt': # some rules for these skins
                for i in ["colorTexture", "colorMaskTexture"]: result[i] = bs.getTexture("tnt")
                result["torsoModel"] = bs.getModel("tnt")
            elif skin_name == 'shard':
                for i in ["colorTexture", "colorMaskTexture"]: result[i] = bs.getTexture("flagColor")
                result["torsoModel"] = bs.getModel("flagStand")
            else:
                for i in bsSpaz.appearances.keys():
                    if skin_name == get_format_skin_name(i):
                        result = bsSpaz.SpazFactory()._getMedia(i)
                        result["style"] = bsSpaz.SpazFactory()._getStyle(i)
                        if a is not None: # get character media and style
                            result["name"]=a.name
                            result["color"]=a.color
                            result["highlight"]=a.highlight
            if a is not None: skin(media=result, player=a) # set this media on player

def check_skins(type="players"):
    if type not in ["nodes", "players"]: raise ValueError("type can be only in 2-parameters")
    a=[]
    if type == "nodes": # new way to detect all of player's nodes
        for i in bsInternal.getNodes():
            if "getNodeType" in dir(i):
                if str(i.getNodeType()) == "spaz":
                    if isinstance(i.getDelegate(), bsSpaz.PlayerSpaz): a.append(i)
    elif type == "players": #old way to detect players, often works badly
        a=[i for i in bsInternal._getForegroundHostActivity().players] if bsInternal._getForegroundHostActivity() is not None else None
    if isinstance(a, list):
        skins = bs.get_setting("skins", {})
        if len(a) > 0 and len(skins) > 0:
            if type == "players":
                for player in a:
                    account_name=str(player.getInputDevice()._getAccountName(True).encode("utf-8"))
                    check_skin(account_name, player)
            elif type == "nodes":
                for node in a:
                    account_name=str(node.getDelegate().getPlayer().getInputDevice()._getAccountName(True).encode("utf-8"))
                    check_skin(account_name, node)
