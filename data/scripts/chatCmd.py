# -*- coding: utf-8 -*-
import bs
import bsInternal
import bsPowerup
import bsUtils
import bsSpaz
import bsGame
from bsSpaz import *
import bsUI
import random
import skins
import bsMainMenu, bsTutorial
import inspect

bsUtils._havePro = bsUtils._haveProOptions = lambda : True

gBots=[i for i in dir(bsSpaz) if inspect.isclass(eval("bsSpaz."+i)) and issubclass(eval("bsSpaz."+i), bsSpaz.SpazBot)]
gBombs=['ice', 'impact', 'landMine', 'normal', 'sticky', 'tnt', 'firework', 'killLaKill', 'qq', 'tp', 'poison', 'ball', 'dirt']
gPowerups=[i[0] for i in list(bsPowerup.getDefaultPowerupDistribution(True))]
gSkins = [skins.get_format_skin_name(i) for i in bsSpaz.appearances.keys()]+["tnt", "shard", "invincible"]
gLang = bs.getLanguage()
gEvent = None

gSettingsEnabled = (hasattr(bs, "get_setting") and hasattr(bs, "set_setting"))

maps={"Doom Shroom":(0.82, 1.10, 1.15), "Hockey Stadium":(1.2,1.3,1.33), \
    "Football Stadium":(1.3, 1.2, 1.0), "Big G":(1.1, 1.2, 1.3), \
    "Roundabout":(1.0, 1.05, 1.1), "Monkey Face":(1.1, 1.2, 1.2), \
    "Bridgit":(1.1, 1.2, 1.3), "Zigzag":(1.0, 1.15, 1.15), \
    "The Pad":(1.1, 1.1, 1.0), "Lake Frigid":(1, 1, 1), \
    "Tip Top":(0.8, 0.9, 1.3), "Crag Castle":(1.15, 1.05, 0.75), \
    "Tower D":(1.15, 1.11, 1.03), "Happy Thoughts":(1.3, 1.23, 1.0), \
    "Step Right Up":(1.2, 1.1, 1.0), "Courtyard":(1.2, 1.17, 1.1), \
    "Rampage":(1.2, 1.1, 0.97)}

if gSettingsEnabled: settings = bs.get_settings()
else: settings = {}
admins, vips, banned, prefixes = settings.get("admins", []), settings.get("vips", []), \
    settings.get("banned", []), settings.get("prefixes", {})

motion_normal, map_tint, tint_normal = None, None, None

def get_normal_tint():
    global map_tint
    a=bsInternal._getForegroundHostActivity()
    if a is not None:
        if isinstance(a, bsMainMenu.MainMenuActivity): name = "The Pad"
        elif isinstance(a, bsTutorial.TutorialActivity): name = "Rampage"
        else: name = a.getMap().name if hasattr(a, "getMap") else None
        if name is not None and name in maps: map_tint = maps[name]
        else: 
            raise ValueError("Invalid map name: "+name)
    return map_tint

def get_motion():
    global motion_normal
    a=bsInternal._getForegroundHostActivity()
    if a is not None and hasattr(a, "settings"): return bool(a.settings.get("Epic Mode", False)) if motion_normal is None else bool(motion_normal)
    return bool(motion_normal)

def get_tint():
    global tint_normal
    if tint_normal is None: tint_normal = get_normal_tint()
    return tint_normal

def set_tint(tint):
    if tint is None or (isinstance(tint, tuple) and len(tint) == 3): 
        global tint_normal
        tint_normal = tint
    else:
        raise ValueError()

def set_motion(motion):
    if motion is None or isinstance(motion, bool):
        global motion_normal
        motion_normal = motion
    else:
        raise ValueError()

def send_message(msg):
    if len(bsInternal._getGameRoster()) < 1:
        if bsUI.gPartyWindow is not None and bsUI.gPartyWindow() is not None:
            with bs.Context("UI"): bsUI.gPartyWindow()._addMsg(msg=msg, color=(1, 1, 1))
    else: bsInternal._chatMessage(msg)

def is_num(num="0"):
    try: int(num)
    except Exception: return False
    else: return True

def is_account(account, return_account=False):
    def check(account):
        if isinstance(account, unicode):
            for icon in ['googlePlusLogo', 'gameCenterLogo', 'gameCircleLogo', \
                'ouyaLogo', 'localAccount', 'alibabaLogo', \
                'oculusLogo', 'nvidiaLogo']:
                if bs.getSpecialChar(icon) in account: return True
        return False
    if isinstance(account, str):
        try: account = account.decode("utf-8")
        except UnicodeEncodeError: account = unicode(account)
    result = check(account=account)
    if return_account: return account if result else None
    else: return result

def get_account_string(arg):
    a = bsInternal._getForegroundHostActivity()
    if arg is not None:
        account = is_account(arg, True)
        if account is not None: return account
        if a is not None and is_num(arg) and hasattr(a, "players") and len(a.players) > int(arg): arg = a.players[int(arg)] 
        if isinstance(arg, bs.Player) and arg.exists(): return is_account(arg.getInputDevice()._getAccountName(True), True)
    return None
    
def find_players_and_bots():
    import inspect
    result=[]
    for i in bsInternal.getNodes(): 
        if hasattr(i, "getNodeType") and str(i.getNodeType()) == "spaz": 
            i = i.getDelegate()
            if isinstance(i, bsSpaz.PlayerSpaz) or (inspect.isclass(i.__class__) and issubclass(i.__class__, bsSpaz.SpazBot)): result.append(i)
    return result

def dayCycle():
    if bsInternal._getForegroundHostActivity() is not None:
        tint = get_tint()
        anim={0: tint, 7500:(1.25, 1.21, 1.075),
            30000: (1.25, 1.21, 1.075), 57500: (1.1, 0.86, 0.74),
            67500: (1.1, 0.86, 0.74), 90000: (0, 0.27, 0.51),
            120000: (0, 0.27, 0.51), 142500: (1.3, 1.06, 1.02),
            157500: (1.3, 1.06, 1.02), 180000: (1.3, 1.25, 1.2),
            195500: (1.3, 1.25, 1.2), 220000: tint}
        bsUtils.animateArray(bs.getSharedObject("globals"), "tint", 3, anim, loop=True)
        
def bigger_than_zero(num=''):
    if not isinstance(num, int) and is_num(num=num): num = int(num)
    if isinstance(num, int) and num > 0: return True
    return False

class ChatOptions(object):
    def __init__(self):
        self.is_vip = False
        self.is_admin = False
        self.is_host = False
        self._bots = None
        self.time={"normal":None, "sunrise": (1.3, 1.06, 1.02), "day": (1.3, 1.25, 1.2), "noon": (1.25, 1.21, 1.075), "sunset": (1.1, 0.86, 0.74), "night":(0, 0.27, 0.51)}

    def add_admin(self, admin=False, account=None):
        global admins
        global vips
        if account is not None:
            if admin and account not in admins:
                admins.append(account)
                if gSettingsEnabled: bs.set_setting("admins", admins)
            if not admin and account not in vips:
                vips.append(account)
                if gSettingsEnabled: bs.set_setting("vips", vips)
                
    def del_admin(self, account=None):
        global admins
        global vips
        if account is not None:
            if account in vips: 
                vips.remove(account)
                if gSettingsEnabled: bs.set_setting("vips", vips)
            if account in admins: 
                admins.remove(account)
                if gSettingsEnabled: bs.set_setting("admins", admins)
            
    def ban(self, account=None):
        if account is not None and account not in banned:
            banned.append(account)
            if gSettingsEnabled: bs.set_setting("banned", banned)
            self.update()

    def set_prefix(self, account=None, prefix='', type='spark'):
        global prefixes
        if account is not None and type in ['slime', 'ice', 'metal', 'rock', 'spark']:
            prefixes.update({account: {type: prefix}})
            if gSettingsEnabled: bs.set_setting("prefixes", prefixes)

    def update(self):
        if bsInternal._getForegroundHostActivity() is not None:
            for i in bsInternal._getGameRoster():
                account = i['displayString'].decode("utf-8")
                id = i['clientID']
                if bs.getSpecialChar('localAccount') in account: 
                    legal = False
                    for i in ["VR","PC","Mac","Android","Linux","Server"]:
                        if i in account: legal=True
                    if not legal: self.ban(account)
                if len(banned) > 0 and account in banned: bsInternal._disconnectClient(id, banTime=1800)
        
    def opt(self, clientID=None, msg=""):
        global gEvent, admins, vips, settings
        global banned, prefixes
        if gSettingsEnabled: 
            settings = bs.get_settings()
            admins, vips, banned, prefixes = settings.get("admins", []), settings.get("vips", []), \
                settings.get("banned", []), settings.get("prefixes", {})
        a = bsInternal._getForegroundHostActivity()
        roster = bsInternal._getGameRoster()
        if gEvent is None: gEvent = bsInternal._getAccountMiscReadVal('easter', False)
        def format_message(msg=''):
            msg = msg.replace("/", "")
            mg = msg.split(" ")
            command = mg[0].lower()
            if len(mg) > 1: 
                arg = mg[1:]
                for i in range(len(arg)):
                    key = arg[i]
                    c = is_account(key, True)
                    if c is not None: arg[i] = c
                    else: arg[i] = key.lower()
            else: arg = []
            if self.player is not None and self.player.exists() and command in ['s', 'summon'] and hasattr(self.player.actor.node, 'position'):
                if ('~' in arg) or ('^' in arg):
                    rng = (2, 5)
                    if len(arg) > 0:
                        if arg[0] in ['f','flag']: rng = (1, 4)
                    for i in range(rng[0], rng[1]):
                        if len(arg) > i and arg[i] in ["~", "^"]: arg[i] = self.player.actor.node.position[i-rng[0]]
            return msg, command, arg
        def check_player():
            global admins
            self.is_vip = self.is_admin = self.is_host = False
            self.player = None
            host = get_account_string(arg=bsInternal._getAccountDisplayString(True))
            if gSettingsEnabled:
                hosts = bs.get_setting("hosts", [])
                if host not in hosts: 
                    hosts.append(host)
                    bs.set_setting("hosts", hosts)
            else: hosts = []
            if len(roster) > 0:
                account = None
                for i in roster: 
                    if i['clientID'] == clientID: 
                        account = i['displayString'].decode('utf-8')
                        break
                if account is not None:
                    if account in vips: self.is_vip = True
                    if account in admins: self.is_vip = self.is_admin = True
                    if account == host or (account != host and account in hosts): self.is_host = self.is_admin = self.is_vip = True
                    for i in a.players:
                        if i.exists():
                            id = i.getInputDevice().getClientID()
                            if id == clientID: self.player = i
            else:
                self.is_host = self.is_admin = self.is_vip = True
                if len(a.players) > 0: self.player = a.players[0]
        check_player()
        msg, command, arg = format_message(msg=msg)
        if a is not None:
            with bs.Context(a):
                if command in ["h", "help"] and self.is_vip:
                    commands, num = {1: []}, 1
                    def add_commands(cmds=[], commands={1: []}, num=1):
                        for i in cmds:
                            if len(commands[num]) < 30: commands[num].append(i)
                            else:
                                num += 1
                                commands[num] = []
                                commands[num].append(i)
                        return commands, num
                    commands, num = add_commands(["help - помощь", "time - установить время", \
                        "skin - изменить облик", "kick - выгнать из игры", \
                        "end - закончить игру", "sm - замедленный режим игры", \
                        "rise - возродить", "frozen - заморозить", "shatter - разделить на части"], 
                        commands=commands, num=num)
                    if self.is_admin: 
                        commands, num = add_commands(['summon - вызвать объект', 'vip - выдать права vip-пользователя', \
                            'punch - сила удара', 'hitpoints - очки жизни', 'prefix - выдать префикс', \
                            'ban - забанить', 'mp - максимальное кол-во игроков', \
                            'pause - остановить/продолжить игру', \
                            'sleep - усыпить', 'head - ребят я черешня', \
                            'nodes - список всех типов объектов на карте', 'connect - а это че', \
                            'curse - проклятие'], commands=commands, num=num)
                    if gEvent:
                        commands, num = add_commands(['flex - хайпово флексить'], commands=commands, num=num)
                        if self.is_admin:
                            commands, num = add_commands(['dance - станцевать брейк', 'dance2 - станцевать лезгинку', 'party - устроить вечеринку'], commands=commands, num=num)
                    if self.is_host:
                        commands, num = add_commands(['default - отобрать права пользователя', \
                            'admin - выдать права администратора'], commands=commands, num=num)
                    commands, num = add_commands(['help [номер страницы] - следующий список команд', \
                        'команды могут выполняться через спец-символ ;', 'pause;/pause(перед каждой командой /)'], commands=commands, num=num)
                    num = 1
                    if len(arg) > 0 and bigger_than_zero(arg[0]): num=int(arg[0])
                    commands = commands.get(num, [])
                    for i in commands: send_message(i)

                elif command in ["l", "list"] and self.is_vip:
                    if len(roster) > 0:
                        players = []
                        for i in [[c["id"] for c in k["players"]] for k in roster]:
                            for d in i: players.append(d)
                        players.sort()
                        for i in roster:
                            data = [(", ").join([r["nameFull"] for r in i["players"]]) if len(i["players"]) > 0 else " - ", (", ").join([str(players.index(r)) for r in [c["id"] for c in i["players"]]]) if len(i["players"]) > 0 else " - "]
                            bsInternal._chatMessage(i["displayString"] + " : "+ data[0] + " : " + data[1])
                    else:
                        if len(a.players) > 0:
                            for i in a.players:
                                bsInternal._chatMessage(i.getInputDevice().getPlayer().getName(True) + " : " + str(a.players.index(i)))
                        else: send_message(" - ")

                elif command in ['timeset', 'time'] and self.is_vip:
                    if len(arg) > 0:
                        tint = get_tint()
                        self.time.update({"normal": get_normal_tint()})
                        for i in self.time:
                            if arg[0] == i:
                                bs.getSharedObject("globals").tint = tint = self.time[i]
                                break
                        if arg[0] == 'cycle': bs.getSharedObject('globals').tint = tint = get_normal_tint()
                        set_tint(tint=tint)
                    else:
                        for i in ['time [normal|sunrise|day|noon|sunset|night|cycle]', \
                            'timeset cycle - дневной цикл(плавная смена времени)', \
                            'timeset noon - середина дня', 'timeset sunset - закат']: send_message(i)
    
                elif command in ['summon','s'] and self.is_admin:
                    if len(arg) > 0:
                        if arg[0] in ['bomb','b']:
                            if len(arg) > 1:
                                bombs = [i.lower() for i in gBombs]
                                bombType, pos, count = 'normal', [0, 5, 0], 1
                                bombType = gBombs[bombs.index(arg[1].lower())] if arg[1].lower() in bombs else 'normal'
                                if len(arg) > 5: count = min(30, int(arg[5])) if bigger_than_zero(arg[5]) else 1
                                for i in range(2, 5):
                                    if len(arg) > i and is_num(arg[i]): pos[i-2] = float(arg[i])
                                for i in range(count):
                                    bs.Bomb(position=tuple(pos), bombType=bombType).autoRetain()
                            else:
                                mg = bs.text_split(words=gBombs)
                                mg += "s bomb [название] [позиция(3 числа)] [кол-во]\ns bomb normal 0 5 0 1"
                                for i in mg.split('\n'): send_message(i)
                        elif arg[0] in ['bot']:
                            if len(arg) > 1:
                                bots = [i.lower() for i in gBots]
                                botType, pos, count = 'BomberBot', [0, 5, 0], 1
                                botType = gBots[bots.index(arg[1].lower())] if arg[1].lower() in bots else 'BomberBot'
                                if len(arg) > 5: count = min(30, int(arg[5])) if bigger_than_zero(arg[5]) else 1
                                for i in range(2, 5):
                                    if len(arg) > i and is_num(arg[i]): pos[i-2] = float(arg[i])
                                if hasattr(bsSpaz, botType):
                                    bot = eval("bsSpaz."+botType)
                                    if not hasattr(self, "_bots") or (hasattr(self, "_bots") and self._bots is None): self._bots = bs.BotSet()
                                    for i in range(count):
                                        self._bots.spawnBot(bot, pos=tuple(pos), spawnTime=0, onSpawnCall=self._on_spawn)
                            else:
                                mg = bs.text_split(words=gBots, words_count=3)
                                mg += "s bot [название] [позиция(3 числа)] [кол-во]\ns bot BomberBot 0 5 0 1"
                                for i in mg.split('\n'): send_message(i)
                        elif arg[0] in ['flag','f']:
                            if len(arg) > 1:
                                pos, count, time_out, color = [0, 5, 0], 1, 20, [1, 1, 0]
                                if len(arg) > 4: count = min(30, int(arg[4])) if bigger_than_zero(arg[4]) else 1
                                if len(arg) > 5: time_out = int(arg[5]) if bigger_than_zero(arg[5]) else 20
                                for i in range(1, 4):
                                    if len(arg) > i and is_num(arg[i]): pos[i-1] = float(arg[i])
                                for i in range(6, 9):
                                    if len(arg) > i and is_num(arg[i]): color[i-6] = float(arg[i])
                                for i in range(count):
                                    bs.Flag(position=tuple(pos), droppedTimeout=time_out, color=color).autoRetain()
                            else:
                                for i in ["s flag [позиция(3 числа)] [кол-во] [тайм-аут] [цвет(3 числа)]", \
                                    "s flag 0 5 0", "s flag ~ ~ ~ 10 999 1 0 0"]: send_message(i)
                        elif arg[0] in ['powerup','p']:
                            if len(arg) > 1:
                                powerups = [i.lower() for i in gPowerups]
                                powerupType, pos, count = 'punch', [0, 5, 0], 1
                                powerupType = gPowerups[powerups.index(arg[1].lower())] if arg[1].lower() in powerups else 'punch'
                                if len(arg) > 5: count = min(30, int(arg[5])) if bigger_than_zero(arg[5]) else 1
                                for i in range(2, 5):
                                    if len(arg) > i and is_num(arg[i]): pos[i-2] = float(arg[i])
                                for i in range(count):
                                    bs.Powerup(position=tuple(pos),powerupType=powerupType).autoRetain()
                            else:
                                mg = bs.text_split(words=gPowerups)
                                mg += "s p [название] [позиция(3 числа)] [кол-во]\ns p punch 0 5 0 1"
                                for i in mg.split('\n'): send_message(i)
                        elif arg[0] in ['box']:
                            if len(arg) > 1:
                                boxTypes = ['s','small','big','b']
                                boxType, pos, count = 'small', [0, 5, 0], 1
                                boxType = arg[1].lower() if arg[1].lower() in boxTypes else 'small'
                                if len(arg) > 5: count = min(30, int(arg[5])) if bigger_than_zero(arg[5]) else 1
                                for i in range(2, 5):
                                    if len(arg) > i and is_num(arg[i]): pos[i-2] = float(arg[i])
                                for i in range(count):
                                    Box(pos=tuple(pos), scale=1 if boxType in ["s","small"] else 1.38, owner=None).autoRetain()
                            else:
                                for i in ["s box [small|big] [позиция] [кол-во]", \
                                    "s box small 0 5 0", "s box big ~ ~ ~ 5"]: send_message(i)
                    else:
                        for i in ["summon [bomb|powerup|bot|box|flag]", "bomb - вызвать бомбу.", "powerup - вызвать усилитель.", "bot - вызвать бота.", "box - вызвать коробку."]: send_message(i)

                elif command in ['skin'] and self.is_vip:
                    if len(arg) > 0:
                        if len(arg) < 2: arg.append(get_account_string(self.player))
                        if arg[0] in gSkins or arg[0] == 'delete':
                            account = is_account(arg[1], True)
                            if arg[1] == "all": 
                                if arg[0] == 'delete':
                                    for i in a.players: skins.delete_skin(i)
                                else: skins.change_skin(skin=arg[0], players=[a.players])
                            elif account is not None: 
                                if arg[0] == 'delete': skins.delete_skin(account)
                                else: skins.change_skin(skin=arg[0], players=[account])
                            elif is_num(arg[1]):
                                if len(a.players) > int(arg[1]) and int(arg[1]) >= 0: 
                                    if arg[0] == 'delete': skins.delete_skin(int(arg[1]))
                                    else: skins.change_skin(skin=arg[0], players=[int(arg[1])])
                            
                    else:
                        mg = bs.text_split(words=gSkins)
                        mg += "skin [название] [номер игрока]\nskin bunny 0\nskin pixie"
                        for i in mg.split('\n'): send_message(i)

                elif command in ['ph','punch','hp','hitpoints'] and self.is_admin:
                    if len(arg) > 0 and len(a.players) > 0:
                        if len(arg) < 2: player = [self.player]
                        if len(arg) > 1:
                            if is_num(arg[1]) and len(a.players) > int(arg[1]) and int(arg[1]) >= 0: player = [a.players[int(arg[1])]]
                            elif arg[1] == "all": player = a.players
                        if player is not None:
                            if bigger_than_zero(arg[0]):
                                arg[0] = int(arg[0])
                                if command in ["punch", "ph"] and arg[0] > 10: arg[0] = 10
                                for i in player:
                                    if i.exists():
                                        if command in ["punch", "ph"]: i.actor._punchPowerScale = arg[0]
                                        else: i.actor.hitPointsMax = i.actor.hitPoints = arg[0]
                    else:
                        for i in [command+" [число] [номер игрока | all]", \
                            command+" 1000 0", command+" 10 all"]: send_message(i)
    
                elif (command in ['vip'] and self.is_admin) or (command in ['admin'] and self.is_host):
                    if len(arg) > 0: self.add_admin(True if command == "admin" else False, get_account_string(arg[0]))
                    else:
                        for i in [command+" [номер игрока|имя аккаунта]", \
                            command+" 0", command+u" \ue030PC123456"]: send_message(i)
                        
                elif command in ['df','default'] and self.is_host:
                    if len(arg) > 0: self.del_admin(get_account_string(arg[0]))
                    else:
                        for i in [command+" [номер игрока|имя аккаунта]", \
                            command+" 0", command+u" \ue030PC123456"]: send_message(i)

                elif command in ['prefix'] and self.is_admin:
                    global prefixes
                    if len(arg) > 0:
                        type = arg[1] if len(arg) > 1 else "spark"
                        prefix = "prefix" if len(arg) < 3 else (" ").join(msg.split(" ")[3:])
                        if arg[0] == 'delete' and len(arg) > 1: account = get_account_string(arg[1])
                        elif arg[0] != 'delete': account = get_account_string(arg[0])
                        else: account = None
                        if arg[0] == 'delete': 
                            if account is not None and account in prefixes:
                                prefixes.pop(account)
                                if gSettingsEnabled: bs.set_setting("prefixes", prefixes)
                        else: self.set_prefix(account=account, prefix=prefix, type=type)
                    else:
                        for i in ["prefix [номер игрока | имя аккаунта] [slime|ice|spark|rock|metal] [префикс]", \
                            "prefix 0 spark клоун сбежал"]: send_message(i)

                elif command in ['kick'] and self.is_vip:
                    if len(arg) > 0:
                        account = get_account_string(arg[0])
                        if account is not None and len(roster) > 0:
                            id = None
                            for i in roster:
                                if i['displayString'].decode('utf-8') == account:
                                    id = i['clientID']
                                    break
                            if id is not None: bsInternal._disconnectClient(id, 300)
                    else:
                        for i in [command+" [номер игрока|имя аккаунта]", \
                            command+" 0", command+u" \ue030PC123456"]: send_message(i)
    
                elif command in ['ban'] and self.is_admin:
                    if len(arg) > 0: self.ban(account=get_account_string(arg[0]))
                    else:
                        for i in [command+" [номер игрока|имя аккаунта]", \
                            command+" 0", command+u" \ue030PC123456"]: send_message(i)
                    
                elif command in ['end'] and self.is_vip:
                    if hasattr(a, "endGame"): a.endGame()
                    else: send_message("Сейчас это недоступно")
                                   
                elif command in ['party','pt'] and self.is_admin:
                    if hasattr(a, 'cameraFlash') and gEvent:
                        time = 1000
                        def run(time=1000):
                            color = tuple([random.randrange(1,2) for i in range(3)])
                            a.cameraFlash(duration=time, color=color)
                        if hasattr(a, "_partyFlash") and a._partyFlash is not None: 
                            a._partyFlash = None
                            a._cameraFlash = []
                        else: 
                            run(time=time)
                            a._partyFlash = bs.Timer(time, bs.Call(run, time), True)
                    else: send_message("Сейчас это недоступно")

                elif command in ['sm'] and self.is_vip:
                    bs.getSharedObject("globals").slowMotion = motion = bs.getSharedObject("globals").slowMotion == False
                    set_motion(motion=motion)
                    
                elif command in ['pause'] and self.is_admin:
                    bs.getSharedObject("globals").paused = bs.getSharedObject("globals").paused == False

                elif command in ['max_players', 'mp'] and self.is_admin:
                    if bigger_than_zero(arg[0]): bsInternal._setPublicPartyMaxSize(int(arg[0]))
                    else:
                        for i in ["mp [кол-во игроков]", "mp 8", "максимальное кол-во игроков сейчас: "+str(bsInternal._getPublicPartyMaxSize())]: send_message(i)
                        
                elif command in ['shatter', 'sh'] and self.is_vip:
                    if len(arg) > 0:
                        def shatter(player=None, shatterMultiple=1): 
                            if player is not None and player.exists() and player.isAlive():
                                player.actor.node.shattered = shatterMultiple
                                player.actor.shattered = True if shatterMultiple > 0 else False
                        if bigger_than_zero(arg[0]):
                            if len(arg) > 1:
                                if is_num(arg[1]) and int(arg[1]) < len(a.players): shatter(a.players[int(arg[1])], int(arg[0]))
                                elif arg[1] == "all":
                                    for i in a.players: shatter(i, int(arg[0])) 
                            elif self.player is not None: shatter(self.player, int(arg[0]))
                    else: 
                        for i in [command+" [число] [номер игрока | all]", command+" 2 0", command+" 10"]: send_message(i)
                        
                elif command in ['frozen', 'fr'] and self.is_vip:
                    if len(arg) > 0:
                        def frozen(player=None):
                            if player is not None and player.exists() and player.isAlive():
                                player.actor.node.frozen = player.actor.node.frozen == 0
                                player.actor.frozen = player.actor.frozen == False
                        if is_num(arg[0]) and int(arg[0]) < len(a.players): frozen(a.players[int(arg[0])])
                        elif arg[0] == "all":
                            for i in a.players: frozen(i)
                        elif self.player is not None: frozen(self.player)
                    else:
                        for i in [command+" [номер игрока | all]", command+" 2", \
                            command+" me", "введи команду повторно, чтобы её отменить"]: send_message(i)
                        
                elif command in ['sleep','sl'] and self.is_admin:
                    if len(arg) > 0:
                        def sleep(player=None, sleepTime=5000):
                            def work(player=None, sleepTime=5000): 
                                if player is not None and player.exists() and player.isAlive():
                                    player.actor.node.handleMessage('knockout', sleepTime)
                                    if not hasattr(player.actor, 'sleepTime') or (hasattr(player.actor, 'sleepTime') and player.actor.sleepTime is None): 
                                        player.actor.sleepTime = sleepTime
                                    else: 
                                        player.actor.sleepTime -= 500
                                        if player.actor.sleepTime <= 0: 
                                            player.actor._sleep = player.actor.sleepTime = None
                            if player is not None and player.exists() and player.isAlive():
                                if sleepTime > 500:
                                    if hasattr(player.actor, '_sleep') and player.actor._sleep is not None: player.actor._sleep = None
                                    else: 
                                        player.actor._sleep = bs.Timer(500, bs.Call(work, player, sleepTime), repeat=True)
                                        work(player=player, sleepTime=sleepTime)
                                else: work(player=player, sleepTime=sleepTime)
                        if bigger_than_zero(arg[0]):
                            if len(arg) > 1:
                                if is_num(arg[1]) and int(arg[1]) < len(a.players): sleep(a.players[int(arg[1])], int(arg[0]))
                                elif arg[1] == "all":
                                    for i in a.players: sleep(i, int(arg[0]))
                            elif self.player is not None: sleep(self.player, int(arg[0]))
                    else:
                        for i in [command+" [число] [номер игрока | all]", command+" 2000 0", \
                            command+" 5000", "введи команду повторно, чтобы её отменить"]: send_message(i)
                    
                elif command in ['curse','cr'] and self.is_admin:
                    if len(arg) > 0:
                        def curse(player=None):
                            if player is not None and player.exists() and player.isAlive():
                                if hasattr(player.actor, 'curse'): player.actor.curse()
                        if is_num(arg[0]) and int(arg[0]) < len(a.players): curse(a.players[int(arg[0])])
                        elif arg[0] == "all":
                            for i in a.players: curse(i)
                        elif self.player is not None: curse(self.player)
                    else:
                        for i in [command+" [номер игрока | all]", command+" 2", command+" me"]: send_message(i)
                    
                elif command in ['nodes'] and self.is_admin:
                    if len(arg) > 0:
                        if arg[0] == 'types': nodes = list(set([i.getNodeType() for i in bsInternal.getNodes() if hasattr(i, "getNodeType")]))
                        if arg[0] == 'names': nodes = [i.getName() for i in bsInternal.getNodes() if hasattr(i, 'getName')]
                        if len(arg) > 1: nodes = [i for i in nodes if arg[1].lower() in i.lower()]
                        for i in bs.text_split(words=nodes, stroke_on_end=False).split('\n'): send_message(i)
                    else: 
                        for i in [command+' types spaz', command+' types', command+' names']: send_message(i)

                elif command in ['connect'] and self.is_admin:
                    def connect(node=None, connected_node=None, type='position'):
                        if node is not None and node.exists():
                            if connected_node is not None and connected_node.exists(): 
                                try: node.connectAttr(type, connected_node, type)
                                except: pass
                    if len(arg) > 0:
                        node = [i for i in bsInternal.getNodes() if hasattr(i, 'getName') and i.getName().lower() == arg[0].lower()]
                        if len(node) > 0: 
                            node = node[0]
                            if len(arg) < 3: arg[2] = 'position'
                            if is_num(arg[1]) and int(arg[1]) < len(a.players): 
                                player = a.players[int(arg[1])]
                                if player.exists(): connect(player.actor.node, node, arg[2])
                            elif arg[1] == "all":
                                for i in a.players: 
                                    if i.exists(): connect(i.actor.node, node, arg[2])
                            elif self.player is not None and self.player.exists(): connect(self.player.actor.node, node, arg[2])
                    else:
                        for i in [command+' [имя объекта (/nodes names)] [номер игрока | all] [тип присоединения]', \
                            command+' spaz@bsSpaz.py:259 all position']: send_message(i)
                    
                        
                elif command in ['head'] and self.is_admin:
                    if len(arg) > 0:
                        def head(player=None):
                            if player is not None and player.exists() and player.isAlive():
                                player.actor.node.holdNode = player.actor.node
                        if is_num(arg[0]) and int(arg[0]) < len(a.players): head(a.players[int(arg[0])])
                        elif arg[0] == "all":
                            for i in a.players: head(i)
                        elif self.player is not None: head(self.player)
                    else:
                        for i in [command+" [номер игрока | all]", command+" 2", command+" me"]: send_message(i)

                elif command in ['rise', 'rs'] and self.is_vip:
                    if len(arg) > 0:
                        def respawn(player=None):
                            if player is not None and player.exists() and not player.isAlive():
                                player.gameData['respawnTimer'] = player.gameData['respawnIcon'] = None
                                with bs.Context(a): a.spawnPlayer(player=player)
                        if is_num(arg[0]) and int(arg[0]) < len(a.players): respawn(a.players[int(arg[0])])
                        elif arg[0] == "all":
                            for i in a.players: respawn(i)
                        elif self.player is not None: respawn(self.player)
                    else:
                        for i in [command+" [номер игрока | all]", command+" 2", command+" me"]: send_message(i)
                        
                elif command in ['flex','fl'] and self.is_vip:
                    if not gEvent:
                        send_message("Сейчас это недоступно")
                        return 
                    if len(arg) > 0:
                        def flex(actor=None):
                            def work(node=None):
                                if node is not None and node.exists(): node.handleMessage('celebrate', 1000)
                            if actor is not None and actor.exists():
                                if not hasattr(actor, '_flex') or (hasattr(actor, '_flex') and actor._flex is None):
                                    actor._flex = bs.Timer(1000, bs.Call(work, actor.node), repeat=True)
                                    work(node=actor.node)
                                else: actor._flex = None
                        if is_num(arg[0]) and int(arg[0]) < len(a.players): flex(a.players[int(arg[0])].actor)
                        elif arg[0] == 'all':
                            for i in find_players_and_bots(): flex(i)
                        elif self.player is not None and self.player.exists(): flex(self.player.actor)
                    else:
                        for i in [command+" [номер игрока|all]", command+" 0", command+" me", "введи команду повторно, чтобы её отменить"]: send_message(i)
                        
                elif command in ['dn', 'dance'] and self.is_admin:
                    if not gEvent:
                        send_message("Сейчас это недоступно")
                        return 
                    if len(arg) > 0:
                        def dance(actor=None):
                            def work(node=None):
                                if node is not None and node.exists():
                                    pos = (node.position[0], node.position[1] + 0.5, node.position[2])
                                    node.handleMessage("impulse", pos[0], pos[1], pos[2], 0, -2, 0, 2000, 0, 1, 0, 0, -2, 0)
                            if actor is not None and actor.exists(): 
                                if not hasattr(actor, '_dance') or (hasattr(actor, '_dance') and actor._dance is None):
                                    actor._dance = bs.Timer(100, bs.Call(work, actor.node), repeat=True)
                                    work(node=actor.node)
                                else: actor._dance = None
                        if is_num(arg[0]) and int(arg[0]) < len(a.players): dance(a.players[int(arg[0])].actor)
                        elif arg[0] == 'all':
                            for i in find_players_and_bots(): dance(i)
                        elif self.player is not None and self.player.exists(): dance(self.player.actor)
                    else:
                        for i in [command+" [номер игрока|all]", command+" 0", command+" me", "введи команду повторно, чтобы её отменить"]: send_message(i)
                        
                elif command in ['dn2', 'dance2'] and self.is_admin:
                    if not gEvent:
                        send_message("Сейчас это недоступно")
                        return 
                    if len(arg) > 0:
                        def dance2(actor=None):
                            def work(node=None):
                                if node is not None and node.exists():
                                    node.jumpPressed = True
                                    node.jumpPressed = False
                            if actor is not None and actor.exists(): 
                                if not hasattr(actor, '_dance2') or (hasattr(actor, '_dance2') and actor._dance2 is None):
                                    actor._dance2 = bs.Timer(500, bs.Call(work, actor.node), repeat=True)
                                    work(node=actor.node)
                                else: actor._dance2 = None
                        if is_num(arg[0]) and int(arg[0]) < len(a.players): dance2(a.players[int(arg[0])].actor)
                        elif arg[0] == 'all':
                            for i in find_players_and_bots(): dance2(i)
                        elif self.player is not None and self.player.exists(): dance2(self.player.actor)
                    else:
                        for i in [command+" [номер игрока|all]", command+" 0", command+" me", "введи команду повторно, чтобы её отменить"]: send_message(i)
                        
    def _on_spawn(self, bot):
        bot.targetPointDefault = bs.Vector(0,0,0)

c = ChatOptions()
def cmd(msg="", clientID=None):
	for i in msg.split(";"): c.opt(msg=bs.format_spaces(i), clientID=clientID)

def update():
    c.update()
    
class Box(bs.Actor):
    def __init__(self, pos=(0, 5, 0), scale=1.35, owner=None):
        self.owner = owner
        bs.Actor.__init__(self)
        box_material = bs.Material()
        box_material.addActions(
            conditions=((('weAreYoungerThan', 0),'or',('theyAreYoungerThan', 0)),
            'and', ('theyHaveMaterial', bs.getSharedObject('objectMaterial'))),
            actions=(('modifyNodeCollision', 'collide', True)))
        box_material.addActions(conditions=('theyHaveMaterial',
            bs.getSharedObject('pickupMaterial')),
            actions=(('modifyPartCollision', 'useNodeCollide', False)))
        box_material.addActions(actions=('modifyPartCollision','friction', 1000))
        self.node = bs.newNode('prop', delegate=self, attrs={
            'position': pos,
            'velocity': (0, 0, 0),
            'model': bs.getModel('tnt'),
            'modelScale': scale,
            'body': 'crate',
            'bodyScale': scale,
            'shadowSize': 0.26 * scale,
            'colorTexture': bs.getTexture(random.choice(["flagColor", "frameInset"])),
            'reflection': 'soft',
            'reflectionScale': [0.23],
            'materials': (bs.getSharedObject('footingMaterial'), bs.getSharedObject('objectMaterial'))})

    def getFactory(cls):
        return None

    def handleMessage(self, msg):
        self._handleMessageSanityCheck()
        if isinstance(msg, bs.PickedUpMessage):
            if self.owner is None:
                self.owner=msg.node
                self.node.handleMessage(ConnectToPlayerMessage(msg.node))
            else:
                self.owner=None
                self.node.connectAttr('position', self.node, 'position')
        elif isinstance(msg, ConnectToPlayerMessage):
            if msg.player is not None:
                if msg.player.exists():
                    self.owner=msg.player
                    self.owner.connectAttr('position', self.node, 'position')
        elif isinstance(msg, bs.OutOfBoundsMessage): self.node.delete()
        elif isinstance(msg, bs.DieMessage): self.node.delete()
        elif isinstance(msg, bs.HitMessage):
            self.node.handleMessage("impulse", msg.pos[0], msg.pos[1], msg.pos[2], msg.velocity[0], msg.velocity[1],
                msg.velocity[2], msg.magnitude * 0.2, msg.velocityMagnitude, msg.radius, 0,
                msg.forceDirection[0], msg.forceDirection[1], msg.forceDirection[2])
        else: bs.Actor.handleMessage(self, msg)

class ConnectToPlayerMessage(object):
    def __init__(self, player):
        self.player=player
