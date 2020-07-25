import bsUtils
import bs
import bsLobby
import bsInternal
import weakref
import bsSpaz
import random
    
gRandProfileIndex = 1
gLastWarnTime = 0
gRandomCharIndexOffset = None
gAccountProfileDeviceID = None
    
class Chooser(object):

    def __del__(self):
        # just kill off our base node; the rest should go down with it
        self._textNode.delete()
        
    def __init__(self, vPos, player, lobby):
        
        import bsInternal
        
        self._deekSound = bs.getSound('deek')
        self._clickSound = bs.getSound('click01')
        self._punchSound = bs.getSound('punch01')
        self._swishSound = bs.getSound('punchSwish')
        self._errorSound = bs.getSound('error')
        self._maskTexture = bs.getTexture('characterIconMask')
        self._vPos = vPos
        self._lobby = weakref.ref(lobby)
        self._player = player
        self._inited = False
        self._dead = False
        
        self.glowDict = {}
        self.markers = ['"',"'","^","%",";","`"]

        # load available profiles either from the local config or from the remote device..
        self.reloadProfiles()
        
        # note: this is just our local index out of available teams; *not* the team ID!
        self._selectedTeamIndex = self.getLobby().nextAddTeam

        # store a persistent random character index; we'll use this for the '_random' profile
        # lets use their inputDevice id to seed it.. this will give a persistent character
        # for them between games and will distribute characters nicely if everyone is random
        try: inputDeviceID = self._player.getInputDevice().getID()
        except Exception,e:
            print 'ERROR: exception getting inputDeviceID for lobby-chooser creation:',e
            inputDeviceID = 0
            import traceback
            traceback.print_stack()

        # we want the first device that asks for a chooser to always get spaz as a random character..
        global gRandomCharIndexOffset
        if gRandomCharIndexOffset is None:
            # scratch that.. we now kinda accomplish the same thing with account profiles
            # so lets just be fully random here..
            gRandomCharIndexOffset = random.randrange(1000)

        # to calc our random index we pick a random character out of our unlocked list and then
        # locate that character's index in the full list
        self._randomCharacterIndex = (inputDeviceID+gRandomCharIndexOffset)%len(self.characterNames)
        
        self._randomColor,self._randomHighlight = bsUtils.getPlayerProfileColors(None)

        global gAccountProfileDeviceID
        
        # attempt to pick an initial profile based on what's been stored for this input device
        try:
            inputDevice = self._player.getInputDevice()
            name = inputDevice.getName()
            uniqueID = inputDevice.getUniqueIdentifier()
            self.profileName = bs.getConfig()['Default Player Profiles'][name+' '+uniqueID]
            self.profileIndex = self.profileNames.index(self.profileName)

            # if this one is __account__ and is local and we havn't marked anyone as the account-profile device yet,
            # mark this guy as it. (prevents the next joiner from getting the account profile too)
            if (self.profileName == '__account__' and not inputDevice.isRemoteClient() and gAccountProfileDeviceID is None):
                gAccountProfileDeviceID = inputDeviceID

        # well hmm that didn't work.. pick __account__, _random, or some other random profile..
        except Exception:

            profileNames = self.profileNames
            
            # we want the first local input-device in the game to latch on to the account profile
            if not inputDevice.isRemoteClient() and not inputDevice.isControllerApp():
                if gAccountProfileDeviceID is None and '__account__' in profileNames:
                    gAccountProfileDeviceID = inputDeviceID

            # if this is the designated account-profile-device, try to default to the account profile
            if inputDeviceID == gAccountProfileDeviceID and '__account__' in profileNames:
                self.profileIndex = profileNames.index('__account__')
            else:
                # if this is the controller app, it defaults to using a random profile
                # (since we can pull the random name from the app)
                if inputDevice.isControllerApp():
                    self.profileIndex = profileNames.index('_random')
                else:
                    # if its a client connection, for now just force the account profile if possible..
                    # (need to provide a way for clients to specify/remember their default profile)
                    if inputDevice.isRemoteClient() and '__account__' in profileNames:
                        self.profileIndex = profileNames.index('__account__')
                    else:
                        global gRandProfileIndex
                        # cycle through our non-random profiles once; after that, everyone gets random.
                        while gRandProfileIndex < len(profileNames) and profileNames[gRandProfileIndex] in ('_random','__account__','_edit'):
                            gRandProfileIndex += 1
                        if gRandProfileIndex < len(profileNames):
                            self.profileIndex = gRandProfileIndex
                            gRandProfileIndex += 1
                        else:
                            self.profileIndex = profileNames.index('_random')
                    
            self.profileName = profileNames[self.profileIndex]
            
        self.characterIndex = self._randomCharacterIndex
        self._color = self._randomColor
        self._highlight = self._randomHighlight
        self.ready = False
        self._textNode = bs.newNode('text',
                                    delegate=self,
                                    attrs={'position':(-100,self._vPos),
                                           'maxWidth':160,
                                           'shadow':0.5,
                                           'vrDepth':-20,
                                           'hAlign':'left',
                                           'vAlign':'center',
                                           'vAttach':'top'})

        bsUtils.animate(self._textNode,'scale',{0:0,100:1.0})
        self.icon = bs.newNode('image',
                               owner=self._textNode,
                               attrs={'position':(-130,self._vPos+20),
                                      'maskTexture':self._maskTexture,
                                      'vrDepth':-10,
                                      'attach':'topCenter'})

        bsUtils.animateArray(self.icon,'scale',2,{0:(0,0),100:(45,45)})

        self._setReady(False)

        # set our initial name to '<choosing player>' in case anyone asks..
        self._player.setName(bs.Lstr(resource='choosingPlayerText').evaluate(),real=False)

        self.getGlowingColors()
        
        self.updateFromPlayerProfile()
        self.updatePosition()
        self._inited = True

    def getTeam(self):
        """ return the selected team """
        return self._lobby()._teams[self._selectedTeamIndex]()

    def getLobby(self):
        return self._lobby()
        
    def getGlowingColors(self):
        try:
            for i in self.profileNames:
                for m in self.markers:
                    if m in i.encode('utf-8') and "," in i.encode("utf-8"):
                        code = i.encode("utf-8").split(",")
                        result = []
                        if len(code) > 4:
                            if code[0] in self.markers:
                                result.append(code[0])
                                for c in [1, 2]: result.append(min(float(code[c]), 10) if float(code[c]) > 0 else max(-10, float(code[c])))
                                for d in [3, 4]: result.append(bool(int(code[d])))
                        elif len(code) == 4:
                            marker = ("").join([i for i in code[0] if i not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]])
                            if marker in self.markers:
                                result.append(marker)
                                for c in [0, 1]:
                                    code[c] = code[c].replace(marker, '')
                                    result.append(min(float(code[c]), 10) if float(code[c]) > 0 else max(-10, float(code[c])))
                                for d in [2, 3]: result.append(bool(int(code[d])))
                        if len(result) == 5: self.glowDict.update({result[0]: result[1:]})
        except Exception as E: print(str(E))

    def updateFromPlayerProfile(self):
        try:
            self.profileName = self.profileNames[self.profileIndex]
            character = self.profiles[self.profileName].get('character', 'Spaz')
            if character not in self.characterNames and character in bsSpaz.appearances: self.characterNames.append(character)
            self.characterIndex = self.characterNames.index(character)
            marker = self.profileName.encode('utf-8')[0] if self.profileName.encode('utf-8')[0] in self.markers else None
            if marker is not None:
                glow = self.glowDict.get(marker, [1, 1, 0, 0])
                cM, hM, stabilizeC, stabilizeH = glow[0], glow[1], glow[2], glow[3]
                self._color, self._highlight = bsUtils.getPlayerProfileColors(self.profileName, profiles=self.profiles)
                
                if not stabilizeC: self._color = (self._color[0]*cM, self._color[1]*cM, self._color[2]*cM)
                else:
                    m = max(self._color)
                    self._color = tuple([i*cM if i == m else i for i in list(self._color)])

                if not stabilizeH: self._highlight = (self._highlight[0]*hM, self._highlight[1]*hM, self._highlight[2]*hM)
                else:
                    m = max(self._highlight)
                    self._highlight = tuple([i*hM if i == m else i for i in list(self._highlight)])
            else: self._color, self._highlight = bsUtils.getPlayerProfileColors(self.profileName, profiles=self.profiles)
        except Exception as E:
            self.characterIndex = self._randomCharacterIndex
            self._color = self._randomColor
            self._highlight = self._randomHighlight
            print(str(E))
        self._updateIcon()
        self._updateText()

    def reloadProfiles(self):
        # re-construct our profile index and other stuff since the profile list might have changed

        inputDevice = self._player.getInputDevice()
        isRemote = inputDevice.isRemoteClient()
        isTestInput = True if (inputDevice is not None and inputDevice.getName().startswith('TestInput')) else False
        
        # pull this player's list of unlocked characters
        if isRemote:
            # FIXME - pull this from remote player (but make sure to filter it to ones we've got)
            self.characterNames = ['Spaz']
        else:
            self.characterNames = self.getLobby().characterNamesLocalUnlocked
        
        # if we're a local player, pull our local profiles from the config..
        # otherwise ask the remote-input-device for its profile list
        if isRemote:
            self.profiles = inputDevice._getPlayerProfiles()
        else:
            try:
                self.profiles = dict(bs.getConfig()['Player Profiles'])
            except Exception as e:
                print 'EXC pulling local profiles'
                self.profiles = {}

        # these may have come over the wire from an older (non-unicode/non-json) version..
        # ..make sure they conform to our standards (unicode strings, no tuples, etc)
        self.profiles = bsUtils.jsonPrep(self.profiles)

        # filter out any characters we're unaware of
        for p in self.profiles.items():
            if p[1].get('character','') not in bsSpaz.appearances:
                p[1]['character'] = 'Spaz'
        
        # add in a random one so we're ok even if there's no user-created profiles
        self.profiles['_random'] = {}

        # for local devices, add it an 'edit' option which will pop up the profile window
        if not isRemote and not isTestInput:
            self.profiles['_edit'] = {}
            
        # build a sorted name list we can iterate through
        self.profileNames = self.profiles.keys()
        self.profileNames.sort(key=lambda x:x.lower())
            
        try:
            self.profileIndex = self.profileNames.index(self.profileName)
        except Exception:
            self.profileIndex = 0
            self.profileName = self.profileNames[self.profileIndex]

    def updatePosition(self):
        # hmmm this shouldnt be happening..
        if not self._textNode.exists():
            'Err: chooser text nonexistant..'
            import traceback
            traceback.print_stack()
            return
        spacing = 350
        offs = spacing*-0.5*len(self.getLobby()._teams) + spacing*self._selectedTeamIndex + 250
        if len(self.getLobby()._teams) > 1: offs -= 35
        curPosition = self._textNode.position
        bsUtils.animateArray(self._textNode,'position',2,{0:self._textNode.position,100:(-100+offs,self._vPos+23)})
        bsUtils.animateArray(self.icon,'position',2,{0:self.icon.position,100:(-130+offs,self._vPos+22)})
        
    def getCharacterName(self):
        return self.characterNames[self.characterIndex]
    
    def _doNothing(self):
        pass

    def _getName(self,full=False):
        nameRaw = name = self.profileNames[self.profileIndex]
        clamp = False
        if name == '_random':
            try: inputDevice = self._player.getInputDevice()
            except Exception: inputDevice = None
            if inputDevice is not None:
                name = inputDevice._getDefaultPlayerName()
            else:
                name = 'Invalid'
            if not full:
                clamp = True
        elif name == '__account__':
            try: inputDevice = self._player.getInputDevice()
            except Exception: inputDevice = None
            if inputDevice is not None:
                name = inputDevice._getAccountName(full)
            else:
                name = 'Invalid'
            if not full:
                clamp = True
        elif name == '_edit':
            # FIXME - this causes problems as an Lstr, but its ok to explicitly translate for now
            # since this is only shown on the host.
            name = bs.Lstr(resource='createEditPlayerText',fallbackResource='editProfileWindow.titleNewText').evaluate()
        else:
            # if we have a regular profile marked as global with an icon, use it (for full only)
            if full:
                try:
                    if self.profiles[nameRaw].get('global',False):
                        icon = bs.uni(self.profiles[nameRaw]['icon'] if 'icon' in self.profiles[nameRaw] else bs.getSpecialChar('logo'))
                        name = icon+name
                except Exception:
                    bs.printException('Error applying global icon')
            else:
                # we now clamp non-full versions of names so there's at least some hope of reading them in-game
                clamp = True
        try:
            for i in self.markers:
                if i in name:
                    name = name.replace(i,"")
        except:
            pass 
        if clamp:
            # in python < 3.5 some unicode chars can have length 2, so we need
            # to convert to raw int vals for safe trimming
            nameChars = bs.uniToInts(name)
            if len(nameChars) > 10:
                name = bs.uniFromInts(nameChars[:10])+'...'
        return name

    def _setReady(self,ready):

        import bsInternal
        
        profileName = self.profileNames[self.profileIndex]

        # handle '_edit' as a special case
        if profileName == '_edit' and ready:
            import bsUI
            with bs.Context('UI'):
                bsUI.PlayerProfilesWindow(inMainMenu=False)
                # give their input-device UI ownership too
                # (prevent someone else from snatching it in crowded games)
                bsInternal._setUIInputDevice(self._player.getInputDevice())
            return
        
        if not ready:
            self._player.assignInputCall('leftPress',bs.Call(self.handleMessage,bsLobby.ChangeMessage('team',-1)))
            self._player.assignInputCall('rightPress',bs.Call(self.handleMessage,bsLobby.ChangeMessage('team',1)))
            self._player.assignInputCall('bombPress',bs.Call(self.handleMessage,bsLobby.ChangeMessage('character',1)))
            self._player.assignInputCall('upPress',bs.Call(self.handleMessage,bsLobby.ChangeMessage('profileIndex',-1)))
            self._player.assignInputCall('downPress',bs.Call(self.handleMessage,bsLobby.ChangeMessage('profileIndex',1)))
            self._player.assignInputCall(('jumpPress','pickUpPress','punchPress'), bs.Call(self.handleMessage,bsLobby.ChangeMessage('ready',1)))
            self.ready = False
            self._updateText()
            self._player.setName('untitled',real=False)
        else:
            self._player.assignInputCall(('leftPress','rightPress', 'upPress','downPress',
                                          'jumpPress','bombPress','pickUpPress'),self._doNothing)
            self._player.assignInputCall(('jumpPress','bombPress','pickUpPress','punchPress'),
                                         bs.Call(self.handleMessage,bsLobby.ChangeMessage('ready',0)))

            # store the last profile picked by this input for reuse
            inputDevice = self._player.getInputDevice()
            name = inputDevice.getName()
            uniqueID = inputDevice.getUniqueIdentifier()
            try: deviceProfiles = bs.getConfig()['Default Player Profiles']
            except Exception: deviceProfiles = bs.getConfig()['Default Player Profiles'] = {}

            # make an exception if we have no custom profiles and are set to random;
            # in that case we'll want to start picking up custom profiles if/when one is made
            # so keep our setting cleared
            haveCustomProfiles = True if [p for p in self.profiles if p not in ('_random','_edit','__account__')] else False
            if profileName == '_random' and not haveCustomProfiles:
                try: del(deviceProfiles[name+' '+uniqueID])
                except Exception: pass
            else:
                deviceProfiles[name+' '+uniqueID] = profileName
            bs.writeConfig()

            # set this player's short and full name
            self._player.setName(self._getName(),self._getName(full=True),real=True)
            self.ready = True
            self._updateText()

            # inform the session that this player is ready
            bs.getSession().handleMessage(bsLobby.PlayerReadyMessage(self))
                
    def handleMessage(self, msg):

        if isinstance(msg, bsLobby.ChangeMessage):

            # if we've been removed from the lobby, ignore this stuff
            if self._dead:
                print "WARNING: chooser got bsLobby.ChangeMessage after dying"
                return
            
            if not self._textNode.exists():
                bs.printError('got bsLobby.ChangeMessage after nodes died')
                return
            
            if msg.what == 'team':
                if len(self.getLobby()._teams) > 1: bs.playSound(self._swishSound)
                self._selectedTeamIndex = (self._selectedTeamIndex + msg.value) % len(self.getLobby()._teams)
                self._updateText()
                self.updatePosition()
                self._updateIcon()

            elif msg.what == 'profileIndex':
                if len(self.profileNames) == 1:
                    # this should be pretty hard to hit now with automatic local accounts..
                    bs.playSound(bs.getSound('error'))
                else:
                    # pick the next player profile and assign our name and character based on that
                    bs.playSound(self._deekSound)
                    self.profileIndex = (self.profileIndex + msg.value) % len(self.profileNames)
                    self.updateFromPlayerProfile()
                
            elif msg.what == 'character':
                bs.playSound(self._clickSound)
                # update our index in our local list of characters
                self.characterIndex = (self.characterIndex + msg.value) % len(self.characterNames)
                self._updateText()
                self._updateIcon()

            elif msg.what == 'ready':

                forceTeamSwitch = False
                
                # team auto-balance kicks us to another team if we try to
                # join the team with the most players
                if not self.ready:
                    try:
                        if bs.getConfig().get('Auto Balance Teams', False):
                            lobby = self.getLobby()
                            if len(lobby._teams) > 1:
                                session = bs.getSession()
                                # first, calc how many players are on each team
                                # ..we need to count both active players and
                                # choosers that have been marked as ready.
                                teamPlayerCounts = {}
                                for team in lobby._teams:
                                    teamPlayerCounts[team().getID()] = len(team().players)
                                for chooser in lobby.choosers:
                                    if chooser.ready:
                                        teamPlayerCounts[chooser.getTeam().getID()] += 1
                                largestTeamSize = max(teamPlayerCounts.values())
                                smallestTeamSize = min(teamPlayerCounts.values())
                                # force switch if we're on the biggest team and there's a smaller one available
                                if largestTeamSize != smallestTeamSize and teamPlayerCounts[self.getTeam().getID()] >= largestTeamSize:
                                    forceTeamSwitch = True
                    except Exception:
                        bs.printException('auto balance error')

                if forceTeamSwitch:
                    bs.playSound(self._errorSound)
                    self.handleMessage(bsLobby.ChangeMessage('team', 1))
                else:
                    bs.playSound(self._punchSound)
                    self._setReady(msg.value)

    def _updateText(self):

        if self.ready:
            # once we're ready, we've saved the name, so lets ask the system for it
            # so we get appended numbers and stuff
            text = bs.Lstr(value=self._player.getName(full=True))
            text = bs.Lstr(value='${A} (${B})',subs=[('${A}',text),('${B}',bs.Lstr(resource='readyText'))])
        else:
            text = bs.Lstr(value=self._getName(full=True))

        canSwitchTeams = len(self.getLobby()._teams) > 1

        # flash as we're coming in
        finColor = bs.getSafeColor(self.getColor())+(1,)
        if not self._inited:
            bsUtils.animateArray(self._textNode,'color',4,{150:finColor,250:(2,2,2,1),350:finColor})
        else:
            # blend if we're in teams mode; switch instantly otherwise
            if canSwitchTeams:
                bsUtils.animateArray(self._textNode,'color',4,{0:self._textNode.color,100:finColor})
            else:
                self._textNode.color = finColor

        self._textNode.text = text

    def getColor(self):
        if self.profileNames[self.profileIndex] == '_edit':
            val = (0,1,0)
        if self.getLobby()._useTeamColors:
            val =  self.getLobby()._teams[self._selectedTeamIndex]().color
        else:
            val = self._color
        if len(val) != 3:
            print 'getColor: ignoring invalid color of len',len(val)
            val = (0,1,0)
        return val

    def getHighlight(self):
        if self.profileNames[self.profileIndex] == '_edit':
            return (0,1,0)
        # if we're using team colors we wanna make sure our highlight color
        # isn't too close to any other team's color
        highlight = list(self._highlight)
        if self.getLobby()._useTeamColors:
            for i,teamRef in enumerate(self.getLobby()._teams):
                team = teamRef()
                if i != self._selectedTeamIndex:
                    # find the dominant component of this team's color
                    # and adjust ours so that the component is not super-dominant
                    maxVal = 0
                    maxIndex = 0
                    for j in range(3):
                        if team.color[j] > maxVal:
                            maxVal = team.color[j]
                            maxIndex = j
                    thatColorForUs = highlight[maxIndex]
                    ourSecondBiggest = max(highlight[(maxIndex+1)%3], highlight[(maxIndex+2)%3])
                    diff = (thatColorForUs-ourSecondBiggest)
                    if diff > 0:
                        highlight[maxIndex] -= diff * 0.6
                        highlight[(maxIndex+1)%3] += diff * 0.3
                        highlight[(maxIndex+2)%3] += diff * 0.2
        return highlight

    def getPlayer(self):
        return self._player

    def _updateIcon(self):
        if self.profileNames[self.profileIndex] == '_edit':
            tex = bs.getTexture('black')
            tintTex = bs.getTexture('black')
            self.icon.color = (1,1,1)
            self.icon.texture = tex
            self.icon.tintTexture = tintTex
            self.icon.tintColor = (0,1,0)
            return

        try:
            texName = bsSpaz.appearances[self.characterNames[self.characterIndex]].iconTexture
            tintTexName = bsSpaz.appearances[self.characterNames[self.characterIndex]].iconMaskTexture
        except Exception:
            bs.printException('Error updating char icon list')
            texName = 'neoSpazIcon'
            tintTexName = 'neoSpazIconColorMask'
        
        tex = bs.getTexture(texName)
        tintTex = bs.getTexture(tintTexName)

        self.icon.color = (1,1,1)
        self.icon.texture = tex
        self.icon.tintTexture = tintTex
        c = self.getColor()
        c2 = self.getHighlight()

        canSwitchTeams = len(self.getLobby()._teams) > 1

        # if we're initing, flash
        if not self._inited:
            bsUtils.animateArray(self.icon,'color',3,{150:(1,1,1),250:(2,2,2),350:(1,1,1)})

        # blend in teams mode; switch instantly in ffa-mode
        if canSwitchTeams:
            bsUtils.animateArray(self.icon,'tintColor',3,{0:self.icon.tintColor,100:c})
        else:
            self.icon.tintColor = c

        self.icon.tint2Color = c2

        # store the icon info the the player
        self._player._setIconInfo(texName,tintTexName,c,c2)

bsLobby.Chooser = Chooser