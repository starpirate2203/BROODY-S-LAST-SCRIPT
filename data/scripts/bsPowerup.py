import bs
import random
import bsUtils 
import bsInternal

defaultPowerupInterval = 8000
gSettingsEnabled = hasattr(bs, "get_settings")

class PowerupMessage(object):    
    def __init__(self,powerupType,sourceNode=bs.Node(None)):
        
        self.powerupType = powerupType
        self.sourceNode = sourceNode

class PowerupAcceptMessage(object):
    """
    category: Message Classes

    Inform a bs.Powerup that it was accepted.
    This is generally sent in response to a bs.PowerupMessage
    to inform the box (or whoever granted it) that it can go away.
    """
    pass

class _TouchedMessage(object):
    pass

class PowerupFactory(object):
    def __init__(self):
        self._lastPowerupType = None

        self.model = bs.getModel("powerup")
        self.modelSimple = bs.getModel("powerupSimple")

        self.texBomb = bs.getTexture("powerupBomb")
        self.texJumpingBomb = bs.getTexture("eggTex3")
        self.texPunch = bs.getTexture("powerupPunch")
        self.texYellowShield = bs.getTexture("coin") 
        self.texKillLaKillBomb = bs.getTexture("black")
        self.texPoisonBomb = bs.getTexture("black")
        self.texSpeedPunch = bs.getTexture("achievementSuperPunch") 
        self.texPandoraBox = bs.getTexture("black")
        self.texMultiBombs = bs.getTexture("logo") 
        self.texFireworkBomb = bs.getTexture("eggTex1") 
        self.texIceBombs = bs.getTexture("powerupIceBombs")
        self.texStickyBombs = bs.getTexture("powerupStickyBombs")
        self.texTpBombs = bs.getTexture("bombStickyColor")
        self.texShield = bs.getTexture("powerupShield")
        self.texImpactBombs = bs.getTexture("powerupImpactBombs")
        self.texHealth = bs.getTexture("powerupHealth")
        self.texLandMines = bs.getTexture("powerupLandMines")
        self.texCurse = bs.getTexture("powerupCurse")
        self.texBalls = bs.getTexture("achievementOutline")
        self.texUnb = bs.getTexture("puckColor")
        self.texDirt = bs.getTexture('nub')

        self.healthPowerupSound = bs.getSound("healthPowerup")
        self.powerupSound = bs.getSound("ooh")
        self.powerdownSound = bs.getSound("pixie2")
        self.dropSound = bs.getSound("boxDrop")

        # material for powerups
        self.powerupMaterial = bs.Material()

        # material for anyone wanting to accept powerups
        self.powerupAcceptMaterial = bs.Material()

        # pass a powerup-touched message to applicable stuff
        self.powerupMaterial.addActions(
            conditions=(("theyHaveMaterial",self.powerupAcceptMaterial)),
            actions=(("modifyPartCollision","collide",True),
                     ("modifyPartCollision","physical",False),
                     ("message","ourNode","atConnect",_TouchedMessage())))

        # we dont wanna be picked up
        self.powerupMaterial.addActions(
            conditions=("theyHaveMaterial",
                        bs.getSharedObject('pickupMaterial')),
            actions=( ("modifyPartCollision","collide",True)))

        self.powerupMaterial.addActions(
            conditions=("theyHaveMaterial",
                        bs.getSharedObject('footingMaterial')),
            actions=(("impactSound",self.dropSound,0.5,0.1)))

        self._powerupDist = []
        for p,freq in getDefaultPowerupDistribution():
            for i in range(int(freq)):
                self._powerupDist.append(p)

    def getRandomPowerupType(self,forceType=None,excludeTypes=[]):
        """
        Returns a random powerup type (string).
        See bs.Powerup.powerupType for available type values.

        There are certain non-random aspects to this; a 'curse' powerup,
        for instance, is always followed by a 'health' powerup (to keep things
        interesting). Passing 'forceType' forces a given returned type while
        still properly interacting with the non-random aspects of the system
        (ie: forcing a 'curse' powerup will result
        in the next powerup being health).
        """
        t = None
        if forceType: t = forceType
        else:
            if self._lastPowerupType == 'curse': t = 'health'
            else:
                while True:
                    if len(self._powerupDist) > 0:
                        t = self._powerupDist[
                            random.randint(0, len(self._powerupDist)-1)]
                        if t not in excludeTypes:
                            break
                    else: break
        self._lastPowerupType = t if t is not None else "health"
        return t if t is not None else 'pass'

def getDefaultPowerupDistribution(all=False):
    if gSettingsEnabled: settings = bs.get_settings()
    else: settings = {}
    powerups_all = {'tripleBombs': 3, 'iceBombs': 3, \
        'punch': 3, 'impactBombs': 3, 'shield': 2, \
        'landMines': 2, 'stickyBombs': 3, \
        'health': 2, 'curse': 1, 'yellowShield': 1, \
        'speedPunch': 1, 'fireworkBombs': 1, \
        'killLaKillBombs': 2, 'jumpingBombs': 1, \
        'tpBombs': 1, 'poisonBombs': 1, \
        'pandoraBox': 1, 'unbreakable': 1, \
        'dirtBombs': 1, 'multiBombs': 1}
    exclude_powerups = settings.get("exclude_powerups", [])
    active_powerups = powerups_all.keys()
    if not all:
        if settings.get("disable_powerups", False): active_powerups = []
        elif len(exclude_powerups) > 0: active_powerups = [i for i in powerups_all if i not in exclude_powerups]
    return tuple([(i) if i[0] in active_powerups else (i[0], 0) for i in powerups_all.items()])

class Powerup(bs.Actor):
    def __init__(self,position=(0,1,0), powerupType='tripleBombs', expire=True):
        
        bs.Actor.__init__(self)
        factory = self.getFactory()

        if gSettingsEnabled: settings = bs.get_settings()
        else: settings = {}

        self.powerupType = powerupType;
        self._powersGiven = False
        if powerupType == 'tripleBombs': tex = factory.texBomb
        elif powerupType == 'multiBombs': tex = factory.texMultiBombs
        elif powerupType == 'punch': tex = factory.texPunch
        elif powerupType == 'speedPunch':tex = factory.texSpeedPunch
        elif powerupType == 'fireworkBombs':tex = factory.texFireworkBomb
        elif powerupType == 'killLaKillBombs': tex = factory.texKillLaKillBomb
        elif powerupType == 'poisonBombs': tex = factory.texPoisonBomb
        elif powerupType == 'pandoraBox': tex = factory.texPandoraBox
        elif powerupType == 'yellowShield': tex = factory.texYellowShield
        elif powerupType == 'jumpingBombs': tex = factory.texJumpingBomb
        elif powerupType == 'tpBombs': tex = factory.texTpBombs
        elif powerupType == 'iceBombs': tex = factory.texIceBombs
        elif powerupType == 'impactBombs': tex = factory.texImpactBombs
        elif powerupType == 'landMines': tex = factory.texLandMines
        elif powerupType == 'stickyBombs': tex = factory.texStickyBombs
        elif powerupType == 'shield': tex = factory.texShield
        elif powerupType == 'health': tex = factory.texHealth
        elif powerupType == 'curse': tex = factory.texCurse
        elif powerupType == 'unbreakable': tex = factory.texUnb
        elif powerupType == 'dirtBombs': tex = factory.texDirt
        elif powerupType == 'pass': return
        else: raise Exception("invalid powerupType: "+str(powerupType))

        if len(position) != 3: raise Exception("expected 3 floats for position")
        
        if powerupType == 'poisonBombs':
            refScale = (0,3,0)
            ref = 'soft'
        elif powerupType == 'pandoraBox':
            ref = 'soft'
            refScale = (1,1,1)
        elif powerupType == 'dirtBombs':
            ref = 'soft'
            refScale = (1, 0.4, 0.16)
        else:
            refScale = [0.95]
            ref = 'powerup'
        self.node = bs.newNode('prop',
            delegate=self,
            attrs={'body':'box',
                   'position':position,
                   'model':factory.model,
                   'lightModel':factory.modelSimple,
                   'shadowSize':0.48,
                   'colorTexture':tex,
                   'reflection':ref,
                   'reflectionScale':refScale,
                   'materials':(factory.powerupMaterial, bs.getSharedObject('objectMaterial'))})
        if powerupType == 'pandoraBox':
            bsUtils.animateArray(self.node, 'reflectionScale', 3, {0:(1,1,1), 1500:(5,5,5), 3000:(-5,-5,-5), 4500:(1,1,1)}, True)

        if settings.get("powerup_lighting", True):
            self.light = bs.newNode('light', owner=self.node, attrs={'position':position,'intensity': 0,'radius': 0, 'color': (random.random()*2.45,random.random()*2.45,random.random()*2.45)})
            self.node.connectAttr('position', self.light, 'position')
            bs.animate(self.light, "radius", {0:0, 140:0.04, 200:0.09, 400:0.078})
            bs.animate(self.light, "intensity", {0:1.0, 1000:1.8, 2000:1.0}, loop = True)
            bsUtils.animateArray(self.light, "color", 3, {0:(self.light.color[0], self.light.color[1], self.light.color[2]), 1000:(self.light.color[0]-0.4, self.light.color[1]-0.4, self.light.color[2]-0.4), 1500:(self.light.color[0], self.light.color[1], self.light.color[2])}, True)

        if settings.get("timer_the_disappearance_of_the_powerup", True):
            self.powerupHurt = bs.newNode('shield', owner=self.node, attrs={'color':(1,1,1), 'radius':0.1, 'hurt':1, 'alwaysShowHealthBar':True})
            self.node.connectAttr('position',self.powerupHurt, 'position')
            bs.animate(self.powerupHurt, 'hurt', {0:0, defaultPowerupInterval-1000:1})
        bs.gameTimer(defaultPowerupInterval-1000, bs.Call(self.do_delete))
        
        curve = bs.animate(self.node,"modelScale",{0:0,140:1.6,200:1})
        bs.gameTimer(200, curve.delete)

        if expire:
            bs.gameTimer(defaultPowerupInterval-2500,
                         bs.WeakCall(self._startFlashing))
            bs.gameTimer(defaultPowerupInterval-1000,
                         bs.WeakCall(self.handleMessage, bs.DieMessage()))

    @classmethod
    def getFactory(cls):
        activity = bs.getActivity()
        if activity is None: raise Exception("no current activity")
        try: return activity._sharedPowerupFactory
        except Exception:
            f = activity._sharedPowerupFactory = PowerupFactory()
            return f

    def _startFlashing(self):
        if self.node.exists(): 
            self.node.flashing = True

    def do_delete(self):
        if self.node is not None and self.node.exists():
            if hasattr(self, "light") and self.light.exists(): 
                bs.animate(self.light, "radius", {0:0.078, 100:0})
                bs.gameTimer(100, self.light.delete)
            if hasattr(self, "powerupHurt") and self.powerupHurt.exists():
                bs.gameTimer(100, self.powerupHurt.delete)
        
    def handleMessage(self, msg):
        self._handleMessageSanityCheck()

        if isinstance(msg, PowerupAcceptMessage):
            factory = self.getFactory()
            if self.powerupType == 'health':
                bs.playSound(factory.healthPowerupSound, 3,
                             position=self.node.position)
            bs.playSound(factory.powerupSound, 3, position=self.node.position)
            self._powersGiven = True
            self.handleMessage(bs.DieMessage())

        elif isinstance(msg, _TouchedMessage):
            if not self._powersGiven:
                node = bs.getCollisionInfo("opposingNode")
                if node is not None and node.exists():
                    node.handleMessage(PowerupMessage(self.powerupType,sourceNode=self.node))

        elif isinstance(msg, bs.DieMessage):
            if self.node.exists():
                if (msg.immediate): self.node.delete()
                else:
                    curve = bs.animate(self.node, "modelScale", {0:1,100:0})
                    bs.gameTimer(100, self.node.delete)

        elif isinstance(msg ,bs.OutOfBoundsMessage):
            self.handleMessage(bs.DieMessage())

        elif isinstance(msg, bs.HitMessage):
            if msg.hitType == 'punch':
                if self.powerupType == 'curse':
                    bs.Blast(position=self.node.position, velocity=(0,0,0), blastRadius=1,blastType="normal", sourcePlayer=None, hitType='explosion',hitSubType='normal').autoRetain()
                    self.handleMessage(bs.DieMessage())
            else:
                self.handleMessage(bs.DieMessage())
        else:
            bs.Actor.handleMessage(self, msg)
