# -*- coding: utf-8 -*-
import bs
import bsUI
import bsInternal

# writed by drov.drov

gPopupWindowColor = (0.45, 0.4, 0.55)

commands = ['/kick','/ban','/frozen','/flex', \
    '/dance','/dance2','/admin','/vip','/df','/rise','/curse','/head','/skin']

skins = ['delete', 'bunny','bear','pixie','santa','tnt',\
    'shard','invincible','bones','pirate','frosty','agent',\
    'taobao','grumbledorf','penguin','shadow','cyborg','zoe',\
    'spaz','kronk','mel','warrior','lee','zola','butch',\
    'oldlady','middleman','gladiator','alien','wrestler',\
    'gretel','robot','witch','mcburton']

commands_account_needed = ['/kick','/ban','/admin','/vip','/df','/skin']

def get_number(clientID):
    roster, activity = bsInternal._getGameRoster(), bsInternal._getForegroundHostActivity()
    choices = []
    if len(roster) > 0:
        players_ids = []
        my_ids = [i['players'] for i in roster if i['clientID'] == clientID]
        my_ids = [i['id'] for i in my_ids[0]] if len(my_ids) > 0 else None
        dt = [[c["id"] for c in i["players"]] for i in roster]
        for i in dt:
            for d in i:
                players_ids.append(d)
        players_ids.sort()
        if len(my_ids) > 0: choices = [players_ids.index(i) for i in my_ids]
    elif activity is not None and hasattr(activity, 'players') and len(activity.players) > 0:
        for i in activity.players:
            if i.exists() and hasattr(i, 'getInputDevice') and i.getInputDevice().getClientID() == clientID:
                choices.append(activity.players.index(i))
    return choices

def get_account(clientID):
    roster, activity = bsInternal._getGameRoster(), bsInternal._getForegroundHostActivity()
    account = None
    if len(roster) > 0:
        for i in roster: 
            if i['clientID'] == clientID: 
                account = i['displayString'].decode('utf-8')
                break
    elif activity is not None and hasattr(activity, 'players') and len(activity.players) > 0:
        for i in activity.players:
            if i.exists() and hasattr(i, 'getInputDevice') and i.getInputDevice().getClientID() == clientID:
                account = i.getInputDevice()._getAccountName(True)
                break
    return account

def _popupWindow(self, choices=[]):
    return bsUI.PopupMenuWindow(position=getattr(self, 'popupMenuPosition', (0,0)),
        scale=2.3 if bsUI.gSmallUI else 1.65 if bsUI.gMedUI else 1.23,
        choices=choices,
        choicesDisplay=[bs.Lstr(value=i) for i in choices],
        currentChoice=None,
        color=gPopupWindowColor,
        delegate=self)

def _onPartyMemberPress(self, clientID, isHost, widget):
    if bsInternal._getForegroundHostSession() is not None: choicesDisplay = [bs.Lstr(resource='kickText')] 
    else:
        if bsInternal._getConnectionToHostInfo().get('buildNumber', 0) < 14248: return
        choicesDisplay = [bs.Lstr(resource='kickVoteText')]
    choices = ['kick'] + commands
    for i in commands: choicesDisplay.append(bs.Lstr(value=i))
    self.popupMenuPosition = widget.getScreenSpaceCenter()
    bsUI.PopupMenuWindow(position=self.popupMenuPosition,
                    scale=2.3 if bsUI.gSmallUI else 1.65 if bsUI.gMedUI else 1.23,
                    choices=choices,
                    choicesDisplay=choicesDisplay,
                    currentChoice=None,
                    color=gPopupWindowColor,
                    delegate=self)
    self._popupType = 'commands'
    self._popupPartyMemberClientID = clientID
    self._popupPartyMemberIsHost = isHost

popupMenuOld = bsUI.PartyWindow.popupMenuSelectedChoice

def popupMenuSelectedChoice(self, popupWindow, choice):
    cmd = self._popupType == 'commands'
    if cmd and choice == 'kick': 
        self._popupType = 'partyMemberPress'
        popupMenuOld(self, popupWindow=popupWindow, choice=choice)
    elif cmd:
        bs.textWidget(edit=self._textField, text='')
        if choice in ['/skin']:
            account = get_account(self._popupPartyMemberClientID)
            if account is not None: 
                self._popupType = {'skins': account}
                self._popupWindow(choices=skins)
        elif choice in commands_account_needed:
            account = get_account(self._popupPartyMemberClientID)
            if account is not None: bs.textWidget(edit=self._textField, text=choice+' '+account)
        elif choice in commands: 
            result = get_number(self._popupPartyMemberClientID)
            if len(result) > 0:
                self._popupType = 'number'
                bs.textWidget(edit=self._textField, text=choice)
                if len(result) > 1: self._popupWindow(choices=result)
                else: choice = str(result[0])
            else: bs.textWidget(edit=self._textField, text='')
    if self._popupType == 'number': bs.textWidget(edit=self._textField, text=(bs.textWidget(query=self._textField)+' '+choice))
    elif isinstance(self._popupType, dict) and 'skins' in self._popupType and choice != '/skin':
        bs.textWidget(edit=self._textField, text=('/skin '+choice+' '+self._popupType.values()[0]))
    else: popupMenuOld(self, popupWindow=popupWindow, choice=choice)

bsUI.PartyWindow.popupMenuSelectedChoice = popupMenuSelectedChoice
bsUI.PartyWindow._onPartyMemberPress = _onPartyMemberPress
bsUI.PartyWindow._popupWindow = _popupWindow
