import bs
import bsUtils
import bsUI
import bsSpaz
import random
import time
import weakref
import bsInternal
import json
import os

gDidInitialTransition = False
gStartTime = time.time()
env = bs.getEnvironment()
    
class MainMenuActivity(bs.Activity):

    def __init__(self, settings={}):
        bs.Activity.__init__(self,settings)
        def menu_music():
            if env['platform'] == 'android':
                file = "menuMusic.ogg"
                if file in os.listdir(env['userScriptsDirectory']):
                    import shutil # copy our file to bombsquad audios data
                    try: shutil.copy(os.path.join(env['userScriptsDirectory'], file), '/data/data/net.froemling.bombsquad/files/bombsquad_files/data/audio')
                    except Exception as E: print(E)
        menu_music()

    def fireworks(self):
        def run():
            pos = (random.randint(-10, 10), random.randrange(14, 15), random.randint(-10, 10))
            bs.emitBGDynamics(position=pos,
                          velocity=tuple([1.0*random.randrange(1,2) for i in range(3)]),
                          count=random.randint(1000, 1200),
                          scale=1, spread=0.8, chunkType='spark')
        start_time = bs.getGameTime()
        def start():
            def check():
                if int((bs.getGameTime()-start_time)*1000) >= 141000: 
                    self._fireworks = None
                    self._fireworks = bs.Timer(200000, bs.Call(self.fireworks))
                else:
                    run()
                    self._fireworks = bs.Timer(500, bs.Call(check), True)
            check()
        start()

    def onTransitionIn(self):
        bs.Activity.onTransitionIn(self)
        global gDidInitialTransition
        random.seed(123)
        try: import install
        except ImportError: pass
        else:
            # check needed methods
            if hasattr(bs, "get_setting") and hasattr(install, "update_modpack"):
                if bs.get_setting("auto-update", False): install.update_modpack(True)
        self._logoNode = None
        self._customLogoTexName = None
        self._wordActors = []
        env = bs.getEnvironment()
        vrMode = bs.getEnvironment()['vrMode']
        if not bs.getEnvironment().get('toolbarTest', True):
            self.myName = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach':'bottom',
                'hAlign':'center',
                'color':(1, 1, 1, 1) if vrMode else (1, 1, 1, 1),
                'flatness':1.0,
                'shadow':1.0 if vrMode else 0.5,
                'scale':(0.65 if (env['interfaceType'] == 'small' or vrMode)
                         else 0.7), # FIXME need a node attr for this
                'position': (0, 25),
                'vrDepth':-10,
                'text':u'\xa9 2019 Eric Froemling'}))
            fullScreen = bsInternal._getSetting("TV Border")
            if env['interfaceType'] != 'small' or env['vrMode']: 
                if fullScreen: position = (0, -10)
                else: position = (-425, 10)
            else: 
                if fullScreen: position = (0, -10)
                else: position = (-425, 35)
            self.moderName = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach':'bottom',
                'hAlign':'center',
                'color':(0.8, 0.8, 0.8, 0.8) if vrMode else (0.8, 0.8, 0.8, 0.8), 
                'flatness':1.0,
                'shadow':1.0 if vrMode else 0.5,
                'scale':(0.55 if (env['interfaceType'] == 'small' or vrMode) else 0.7), # FIXME need a node attr for this
                'position': position,
                'vrDepth':-10,
                'text':u'\xa9 ModPack is created by Daniil Rakhov'}))
        
        self._hostIsNavigatingText = bs.NodeActor(bs.newNode('text', attrs={
            'text':bs.Lstr(resource='hostIsNavigatingMenusText',
                           subs=[('${HOST}',
                                  bsInternal._getAccountDisplayString())]),
            'clientOnly':True,
            'position':(0,-200),
            'flatness':1.0,
            'hAlign':'center'}))
        if not gDidInitialTransition:
            if hasattr(self, 'myName'): bs.animate(self.myName.node, 'opacity', {2300:0,3000:1.0})
            if hasattr(self, 'moderName'): bs.animate(self.moderName.node, 'opacity', {2300:0,3300:1.0})

        # FIXME - shouldn't be doing things conditionally based on whether
        # the host is vr mode or not (clients may not be or vice versa)
        # - any differences need to happen at the engine level
        # so everyone sees things in their own optimal way
        vrMode = env['vrMode']
        interfaceType = env['interfaceType']

        # in cases where we're doing lots of dev work lets
        # always show the build number
        forceShowBuildNumber = True

        if not bs.getEnvironment().get('toolbarTest', True):
            text = "BROODYs WORLD"
            try: from multiversion import get_version
            except ImportError: 
                path = os.path.join(env["userScriptsDirectory"], "about_modpack.json")
                if os.path.exists(path):
                    try: data = json.load(open(path))
                    except Exception: pass
                    else: text += " v."+str(data.get("version", {"v": "???"}).get("v"))        
            else: text += " v." + str(get_version())
            if env['debugBuild'] or env['testBuild']:
                if env['debugBuild']: text += " [debug]"
                else: text += " [test]"
            if forceShowBuildNumber: text = "based on "+str(env['version'])+"\n" + text
            self.version = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach':'bottom',
                'hAttach':'right',
                'hAlign':'right',
                'flatness':1.0,
                'vrDepth':-10,
                'shadow': 0.5,
                'color': (0.5,0.6,0.5,0.7),
                'scale':0.7 if (interfaceType == 'small' or vrMode) else 0.85,
                'position':(-260,10) if vrMode else (-10,30),
                'text': text}))
            if not gDidInitialTransition:
                bs.animate(self.version.node,'opacity',{0:0, 3000:0, 4000:1.0})

        # throw in beta info..
        self.betaInfo = self.betaInfo2 = None
        if env['testBuild'] and not env['kioskMode']:
            self.betaInfo = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach':'center',
                'hAlign':'center',
                'color':(1,1,1,1),
                'shadow':0.5,
                'flatness':0.5,
                'scale':1,
                'vrDepth':-60,
                'position':(230,125) if env['kioskMode'] else (230,35),
                'text': bs.Lstr(resource="testBuildText")}))
            if not gDidInitialTransition:
                bs.animate(self.betaInfo.node,'opacity',{1300:0,1800:1.0})
        model = bs.getModel('thePadLevel')
        treesModel = bs.getModel('trees')
        bottomModel = bs.getModel('thePadLevelBottom')
        borModel = bs.getCollideModel('thePadLevelCollide')
        testColorTexture = bs.getTexture('thePadLevelColor')
        treesTexture = bs.getTexture('treesColor')
        bgTex = bs.getTexture('alwaysLandBGColor')
        bgModel = bs.getModel('alwaysLandBG')
        vrBottomFillModel = bs.getModel('thePadVRFillBottom')
        vrTopFillModel = bs.getModel('thePadVRFillTop')
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.cameraMode = 'rotate'
        bsGlobals.tint = (1.1,1.1,1.0)
        self.bottom = bs.NodeActor(bs.newNode('terrain', attrs={
            'model':bottomModel,
            'lighting':False,
            'reflection':'soft',
            'reflectionScale':[0.45],
            'colorTexture':testColorTexture}))
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel':borModel,
            'model':model,
            'colorTexture':testColorTexture,
            'materials':[bs.getSharedObject('footingMaterial')]})
        self.vrBottomFill = bs.NodeActor(bs.newNode('terrain', attrs={
            'model':vrBottomFillModel,
            'lighting':False,
            'vrOnly':True,
            'colorTexture':testColorTexture}))
        self.vrTopFill = bs.NodeActor(bs.newNode('terrain', attrs={
            'model':vrTopFillModel,
            'vrOnly':True,
            'lighting':False,
            'colorTexture':bgTex}))
        self.terrain = bs.NodeActor(bs.newNode('terrain', attrs={
            'model':model,
            'colorTexture':testColorTexture,
            'reflection':'soft',
            'reflectionScale':[0.3]}))
        self.trees = bs.NodeActor(bs.newNode('terrain', attrs={
            'model':treesModel,
            'lighting':False,
            'reflection':'char',
            'reflectionScale':[0.1],
            'colorTexture':treesTexture}))
        self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
            'model':bgModel,
            'color':(0.92,0.91,0.9),
            'lighting':False,
            'background':True,
            'colorTexture':bgTex}))
        textOffsetV = 0
        self._ts = 0.86
        self._language = None
        self._updateTimer = bs.Timer(2000, bs.Call(self._update, False), repeat=True)
        self._update(True)
        bs.gameTimer(55000, bs.Call(self.fireworks))
        bsUtils.animateArray(bs.getSharedObject("globals"), "tint", 3, {0:(1.1,1.1,1.0), 7500:(1.25, 1.21, 1.075), 30000:(1.25, 1.21, 1.075), \
            57500:(1.1, 0.86, 0.74), 67500:(1.1, 0.86, 0.74), \
            90000:(0, 0.27, 0.51), 120000:(0, 0.27, 0.51), 142500:(1.3, 1.06, 1.02), \
            157500:(1.3, 1.06, 1.02), 180000:(1.3, 1.25, 1.2), 195500:(1.3, 1.25, 1.2), \
            220000:(1.1,1.1,1.0)})
        bsInternal._addCleanFrameCallback(bs.WeakCall(self._startPreloads))
        random.seed()

        class News(object):
            
            def __init__(self,activity):
                self._valid = True
                self._messageDuration = 10000
                self._messageSpacing = 2000
                self._text = None
                self._activity = weakref.ref(activity)
                self._fetchTimer = bs.Timer(1000,bs.WeakCall(self._tryFetchingNews),repeat=True)
                self._tryFetchingNews()

            def _tryFetchingNews(self):
                if bsInternal._getAccountState() == 'SIGNED_IN':
                    self._fetchNews()
                    self._fetchTimer = None
                
            def _fetchNews(self):
                try: launchCount = bs.getConfig()['launchCount']
                except Exception: launchCount = None
                global gLastNewsFetchTime
                gLastNewsFetchTime = time.time()
                
                # UPDATE - we now just pull news from MRVs
                news = bsInternal._getAccountMiscReadVal('n', None)
                if news is not None:
                    self._gotNews(news)

            def _changePhrase(self):

                global gLastNewsFetchTime
                
                if time.time()-gLastNewsFetchTime > 100.0:
                    self._fetchNews()
                    self._text = None
                else:
                    if self._text is not None:
                        if len(self._phrases) == 0:
                            for p in self._usedPhrases:
                                self._phrases.insert(0,p)
                        val = self._phrases.pop()
                        if val == '__ACH__':
                            vr = bs.getEnvironment()['vrMode']
                            bsUtils.Text(
                                bs.Lstr(resource='nextAchievementsText'),
                                color=(1,1,1,1) if vr else (0.95,0.9,1,0.4),
                                hostOnly=True,
                                maxWidth=200,
                                position=(-300, -35),
                                hAlign='right',
                                transition='fadeIn',
                                scale=0.9 if vr else 0.7,
                                flatness=1.0 if vr else 0.6,
                                shadow=1.0 if vr else 0.5,
                                hAttach="center",
                                vAttach="top",
                                transitionDelay=1000,
                                transitionOutDelay=self._messageDuration)\
                                   .autoRetain()
                            import bsAchievement
                            achs = [a for a in bsAchievement.gAchievements
                                    if not a.isComplete()]
                            if len(achs) > 0:
                                a = achs.pop(random.randrange(min(4,len(achs))))
                                a.createDisplay(-180, -35, 1000,
                                                outDelay=self._messageDuration,
                                                style='news')
                            if len(achs) > 0:
                                a = achs.pop(random.randrange(min(8,len(achs))))
                                a.createDisplay(180, -35, 1250,
                                                outDelay=self._messageDuration,
                                                style='news')
                        else:
                            s = self._messageSpacing
                            keys = {s:0, s+1000:1.0,
                                    s+self._messageDuration-1000:1.0,
                                    s+self._messageDuration:0.0}
                            bs.animate(self._text.node, "opacity",
                                       dict([[k,v] for k,v in keys.items()]))
                            self._text.node.text = val

            def _gotNews(self, news):
                
                # run this stuff in the context of our activity since we need
                # to make nodes and stuff.. should fix the serverGet call so it 
                activity = self._activity()
                if activity is None or activity.isFinalized(): return
                with bs.Context(activity):
                
                    self._phrases = []
                    # show upcoming achievements in non-vr versions
                    # (currently too hard to read in vr)
                    self._usedPhrases = (
                        ['__ACH__'] if not bs.getEnvironment()['vrMode']
                        else []) + [s for s in news.split('<br>\n') if s != '']
                    self._phraseChangeTimer = bs.Timer(
                        self._messageDuration+self._messageSpacing,
                        bs.WeakCall(self._changePhrase), repeat=True)

                    sc = 1.2 if (bs.getEnvironment()['interfaceType'] == 'small'
                                 or bs.getEnvironment()['vrMode']) else 0.8

                    self._text = bs.NodeActor(bs.newNode('text', attrs={
                        'vAttach':'top',
                        'hAttach':'center',
                        'hAlign':'center',
                        'vrDepth':-20,
                        'shadow':1.0 if bs.getEnvironment()['vrMode'] else 0.4,
                        'flatness':0.8,
                        'vAlign':'top',
                        'color':((1, 1, 1, 1) if bs.getEnvironment()['vrMode']
                                 else (0.7, 0.65, 0.75, 1.0)),
                        'scale':sc,
                        'maxWidth':900.0/sc,
                        'position':(0,-10)}))
                    self._changePhrase()
                    
        if not env['kioskMode'] and not env.get('toolbarTest', True):
            self._news = News(self)

        # bring up the last place we were, or start at the main menu otherwise
        with bs.Context('UI'):
            try: mainWindow = bsUI.gMainWindow
            except Exception: mainWindow = None

            # when coming back from a kiosk-mode game, jump to
            # the kiosk start screen.. if bsUtils.gRunningKioskModeGame:
            if bs.getEnvironment()['kioskMode']:
                bsUI.uiGlobals['mainMenuWindow'] = \
                     bsUI.KioskWindow().getRootWidget()
            # ..or in normal cases go back to the main menu
            else:
                if mainWindow == 'Gather':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.GatherWindow(transition=None).getRootWidget()
                elif mainWindow == 'Watch':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.WatchWindow(transition=None).getRootWidget()
                elif mainWindow == 'Team Game Select':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.TeamsWindow(sessionType=bs.TeamsSession,
                                         transition=None).getRootWidget()
                elif mainWindow == 'Free-for-All Game Select':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.TeamsWindow(sessionType=bs.FreeForAllSession,
                                         transition=None).getRootWidget()
                elif mainWindow == 'Coop Select':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.CoopWindow(transition=None).getRootWidget()
                else: bsUI.uiGlobals['mainMenuWindow'] = \
                    bsUI.MainMenuWindow(transition=None).getRootWidget()

                # attempt to show any pending offers immediately.
                # If that doesn't work, try again in a few seconds
                # (we may not have heard back from the server)
                # ..if that doesn't work they'll just have to wait
                # until the next opportunity.
                if not bsUI._showOffer():
                    def tryAgain():
                        if not bsUI._showOffer():
                            # try one last time..
                            bs.realTimer(2000, bsUI._showOffer)
                    bs.realTimer(2000, tryAgain)
            
        gDidInitialTransition = True

    def change_text_position(self):
        fullScreen = bsInternal._getSetting("TV Border")
        if env['interfaceType'] != 'small' or env['vrMode']: 
            if fullScreen: position = (0, -10)
            else: position = (-425, 10)
        else: 
            if fullScreen: position = (0, -10)
            else: position = (-425, 35)
        if self.moderName.node.position != position:
            bs.animate(self.moderName.node, 'opacity', {0: 1.0, 500: 0.0, 1000: 0.0, 2000: 1.0})
            def a():
                self.moderName.node.position = position
            bs.gameTimer(550, bs.Call(a))

    def _update(self, forceUpdate=False):
        if hasattr(self, 'moderName') and not forceUpdate:
            if not bs.get_setting("in_menu_author_name", True): bs.animate(self.moderName.node, 'opacity', {0: self.moderName.node.opacity, 500: 0.0})
            else:
                if self.moderName.node.opacity < 1.0: 
                    bs.animate(self.moderName.node, 'opacity', {0: self.moderName.node.opacity, 500: 1.0})
                    bs.gameTimer(500, bs.Call(self.change_text_position))
                else: self.change_text_position()
        l = bs.getLanguage()
        if l != self._language:
            self._language = l
            env = bs.getEnvironment()
            y = 20
            gScale = 1.1
            self._wordActors = []
            baseDelay = 1000
            delay = baseDelay
            delayInc = 20
            baseX = -170
            x = baseX-20
            spacing = 55*gScale
            yExtra = 0 if env['kioskMode'] else 0
            x1 = x
            delay1 = delay
            for shadow in (True, False):
                x = x1
                delay = delay1
                self._makeWord('H', x-15, y-23, scale=1.3*gScale,
                               delay=delay-500, vrDepthOffset=3, shadow=True)
                self._makeWord('a', x+38, y-23, scale=1.3*gScale,
                               delay=delay-400, vrDepthOffset=3, shadow=True)
                self._makeWord('r', x+88, y-23, scale=1.3*gScale,
                               delay=delay-300, vrDepthOffset=3, shadow=True)
                self._makeWord('d', x+138, y-23, scale=1.3*gScale,
                               delay=delay-200, vrDepthOffset=3, shadow=True)
                self._makeWord('C', x+188, y-23, scale=1.3*gScale,
                               delay=delay-100, vrDepthOffset=3, shadow=True)
                self._makeWord('o', x+238, y-23, scale=1.3*gScale,
                               delay=delay, vrDepthOffset=3, shadow=True)
                self._makeWord('r', x+288, y-23, scale=1.3*gScale,
                               delay=delay+100, vrDepthOffset=3, shadow=True)
                self._makeWord('e', x+338, y-23, scale=1.3*gScale,
                               delay=delay+200, vrDepthOffset=3, shadow=True)
                self._makeWord('◉', x+162, y-98, scale=3*gScale,
                               delay=delay+600, vrDepthOffset=3, shadow=True)
           
    def _makeWord(self, word, x, y, scale=1.0, delay=0,
                  vrDepthOffset=0, shadow=True):
        wordShadowObj = bs.NodeActor(bs.newNode('text', attrs={
            'position':(x,y),
            'big':True,
            'color':(0.95, 1.55, 0.6+random.random()/2 if random.random()>0.6 else 0.6, 0.65),
            'tiltTranslate':0.11,
            'tiltTranslate':0.09,
            'opacityScalesShadow':False,
            'shadow':0.01,
            'vrDepth':-130,
            'vAlign':'center',
            'projectScale':0.97*scale,
            'scale':1.0,
            'text':word}))
        self._wordActors.append(wordShadowObj)
        if not bs.getEnvironment()['vrMode']:
            if not shadow: c = bs.newNode("combine", owner=wordObj.node, attrs={'size':2})
            else: c = None
            if shadow: c2 = bs.newNode("combine", owner=wordShadowObj.node, attrs={'size':2})
            else: c2 = None
            if not shadow: c.connectAttr('output',wordObj.node,'position')
            if shadow: c2.connectAttr('output',wordShadowObj.node,'position')
            keys = {}
            keys2 = {}
            timeV = 0
            for i in range(10):
                val = x + random.uniform(0, 1)
                val2 = x + random.uniform(-1,0)
                keys[timeV*self._ts] = val
                keys2[timeV*self._ts] = val2
                timeV += 720
            if c is not None: bs.animate(c, "input0", keys, loop=True)
            if c2 is not None: bs.animate(c2, "input0", keys2, loop=True)

            keys = {}
            keys2 = {}
            timeV = 0
            for i in range(10):
                val = y+random.uniform(0, 1)
                val2 = y+random.uniform(-1,0)
                keys[timeV*self._ts] = val
                keys2[timeV*self._ts] = val2
                timeV += 1000
            if c is not None: bs.animate(c,"input1",keys,loop=True)
            if c2 is not None: bs.animate(c2,"input1",keys2,loop=True)

        if not shadow:
            bs.animate(wordObj.node, "projectScale",
                       {delay:scale * 0, delay+210:scale})
        else:
            bs.animate(wordShadowObj.node, "projectScale",
                       {delay:scale *0, delay+210:scale})
    def _getCustomLogoTexName(self):
        return None
        
    def _startPreloads(self):
        # FIXME - the func that calls us back doesn't save/restore state
        # or check for a dead activity so we have to do that ourself..
        if self.isFinalized(): return
        with bs.Context(self): _preload1()

        bs.gameTimer(500,lambda: bs.playMusic('Menu'))
        
        
# a second or two into the main menu is a good time to preload some stuff
# we'll need elsewhere to avoid hitches later on..
def _preload1():
    for m in ['plasticEyesTransparent', 'playerLineup1Transparent',
              'playerLineup2Transparent', 'playerLineup3Transparent',
              'playerLineup4Transparent', 'angryComputerTransparent',
              'scrollWidgetShort', 'windowBGBlotch']: bs.getModel(m)
    for t in ["playerLineup","lock"]: bs.getTexture(t)
    for tex in ['iconRunaround', 'iconOnslaught',
                'medalComplete', 'medalBronze', 'medalSilver',
                'medalGold', 'characterIconMask']: bs.getTexture(tex)
    bs.getTexture("bg")
    bs.Powerup.getFactory()
    bs.gameTimer(100,_preload2)

def _preload2():
    # FIXME - could integrate these loads with the classes that use them
    # so they don't have to redundantly call the load
    # (even if the actual result is cached)
    for m in ["powerup", "powerupSimple"]: bs.getModel(m)
    for t in ["powerupBomb", "powerupSpeed", "powerupPunch",
              "powerupIceBombs", "powerupStickyBombs", "powerupShield",
              "powerupImpactBombs", "powerupHealth"]: bs.getTexture(t)
    for s in ["powerup01", "boxDrop", "boxingBell", "scoreHit01",
              "scoreHit02", "dripity", "spawn", "gong"]: bs.getSound(s)
    bs.Bomb.getFactory()
    bs.gameTimer(100,_preload3)

def _preload3():
    for m in ["bomb", "bombSticky", "impactBomb"]: bs.getModel(m)
    for t in ["bombColor", "bombColorIce", "bombStickyColor",
              "impactBombColor", "impactBombColorLit"]: bs.getTexture(t)
    for s in ["freeze", "fuse01", "activateBeep", "warnBeep"]: bs.getSound(s)
    spazFactory = bs.Spaz.getFactory()
    # go through and load our existing spazzes and their icons
    # (spread these out quite a bit since theres lots of stuff for each)
    def _load(spaz):
        spazFactory._preload(spaz)
        # icons also..
        bs.getTexture(bsSpaz.appearances[spaz].iconTexture)
        bs.getTexture(bsSpaz.appearances[spaz].iconMaskTexture)
    # FIXME - need to come up with a standin texture mechanism or something
    # ..preloading won't scale too much farther..
    t = 50
    bs.gameTimer(200,_preload4)

def _preload4():
    for t in ['bar', 'meter', 'null', 'flagColor', 'achievementOutline']:
        bs.getTexture(t)
    for m in ['frameInset', 'meterTransparent', 'achievementOutline']:
        bs.getModel(m)
    for s in ['metalHit', 'metalSkid', 'refWhistle', 'achievement']:
        bs.getSound(s)
    bs.Flag.getFactory()
    bs.Powerup.getFactory()

class SplashScreenActivity(bs.Activity):

    def __init__(self,settings={}):
        bs.Activity.__init__(self,settings)
        self._part1Duration = 4000
        self._tex = bs.getTexture('aliSplash')
        self._tex2 = bs.getTexture('aliControllerQR')
        
    def _startPreloads(self):
        # FIXME - the func that calls us back doesn't save/restore state
        # or check for a dead activity so we have to do that ourself..
        if self.isFinalized(): return
        with bs.Context(self): _preload1()
        
    def onTransitionIn(self):
        import bsInternal
        bs.Activity.onTransitionIn(self)
        bsInternal._addCleanFrameCallback(bs.WeakCall(self._startPreloads))
        self._background = bsUtils.Background(fadeTime=500, startFaded=True,
                                              showLogo=False)
        self._part = 1
        self._image = bsUtils.Image(self._tex, transition='fadeIn',
                                    modelTransparent=bs.getModel('image4x1'),
                                    scale=(800, 200), transitionDelay=500,
                                    transitionOutDelay=self._part1Duration-1300)
        bs.gameTimer(self._part1Duration, self.end)

    def _startPart2(self):
        if self._part != 1: return
        self._part = 2
        self._image = bsUtils.Image(self._tex2, transition='fadeIn',
                                    scale=(400, 400), transitionDelay=0)
        t = bsUtils._translate('tips', 'If you are short on controllers, '
                               'install the \'${REMOTE_APP_NAME}\' app\n'
                               'on your mobile devices to use them '
                               'as controllers.')
        t = t.replace('${REMOTE_APP_NAME}',bsUtils._getRemoteAppName())
        self._text = bsUtils.Text(t, maxWidth=900, hAlign='center',
                                  vAlign='center', position=(0,270),
                                  color=(1,1,1,1), transition='fadeIn')
    def onSomethingPressed(self):
        self.end()

gFirstRun = True

class MainMenuSession(bs.Session):

    def __init__(self):
        bs.Session.__init__(self)
        self._locked = False
        # we have a splash screen only on ali currently..
        env = bs.getEnvironment()
        global gFirstRun
        if env['platform'] == 'android' \
           and env['subplatform'] == 'alibaba' \
           and gFirstRun:
            bsInternal._lockAllInput()
            self._locked = True
            self.setActivity(bs.newActivity(SplashScreenActivity))
            gFirstRun = False
        else:
            self.setActivity(bs.newActivity(MainMenuActivity))

    def onActivityEnd(self,activity,results):
        if self._locked:
            bsInternal._unlockAllInput()
        # any ending activity leads us into the main menu one..
        self.setActivity(bs.newActivity(MainMenuActivity))
        
    def onPlayerRequest(self,player):
        # reject player requests, but if we're in a splash-screen, take the
        # opportunity to tell it to leave
        # FIXME - should add a blanket way to capture all input for
        # cases like this
        activity = self.getActivity()
        if isinstance(activity, SplashScreenActivity):
            with bs.Context(activity): activity.onSomethingPressed()
        return False

