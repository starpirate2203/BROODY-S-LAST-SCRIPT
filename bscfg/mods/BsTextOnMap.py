#MadeBySobyDamn
import bs
from bsMap import *
import bsMap
from random import randrange
from settings import *
count = len(texts)


def __init__(self, vrOverlayCenterOffset=None):
        """
        Instantiate a map.
        """
        import bsInternal
        bs.Actor.__init__(self)
        self.preloadData = self.preload(onDemand=True)
        def text():
                t = bs.newNode('text',
                       attrs={ 'text':'',
                              'scale':0.5554,
                              'maxWidth':0,
                              'position':(-600,20),
                              'shadow':0.9,
                              'flatness':1.0,
                              'color':(3,0,0),
                              'hAlign':'left',
                              'vAttach':'bottom'})
                bs.animate(t,'opacity',{0:1.0})
                t = bs.newNode('text',
                       attrs={ 'text':'',
                              'scale':0.5554,
                              'maxWidth':0,
                              'position':(600,20),
                              'shadow':0.9,
                              'flatness':1.0,
                              'color':(0,0,3),
                              'hAlign':'right',
                              'vAttach':'bottom'})
                bs.animate(t,'opacity',{0:1.0})
                t = bs.newNode('text',
                       attrs={ 'text':'TYPE /superman TO LEARN FLYIN',
                              'scale':0.7,
                              'maxWidth':0,
                              'position':(-600,20),
                              'shadow':0.9,
                              'flatness':1.0,
                              'color':(3,1,1),
                              'hAlign':'left',
                              'vAttach':'bottom'})
                bs.animate(t,'opacity',{0:0.85})
                t = bs.newNode('text',
                       attrs={ 'text':'TYPE /help TO GET INFO',
                              'scale':0.7,
                              'maxWidth':0,
                              'position':(600,20),
                              'shadow':0.9,
                              'flatness':1.0,
                              'color':(3,1,1),
                              'hAlign':'right',
                              'vAttach':'bottom'})
                bs.animate(t,'opacity',{0:0.85})
                t = bs.newNode('text',
                       attrs={ 'text':u'\ue02f|BROODYs HOUSE PARTY|\ue02f',
                              'scale':0.7554,
                              'maxWidth':0,
                              'position':(11,-60),
                              'shadow':1.3,
                              'flatness':1.0,
                              'color':(1,1,1),
                              'hAlign':'center',
                              'vAttach':'top'})
                bs.animate(t,'opacity',{0:1.0})
                t = bs.newNode('text',
                       attrs={ 'text':u'TYPE /contact TO CONTACT BROODY',
                              'scale':0.5,
                              'maxWidth':0,
                              'position':(11,-80),
                              'shadow':0.9,
                              'flatness':1.0,
                              'color':(1,1,1),
                              'hAlign':'center',
                              'vAttach':'top'})
                bs.animate(t,'opacity',{0:0.65})
                t = bs.newNode('text',
                       attrs={ 'text':u'',
                              'scale':0.6,
                              'maxWidth':0,
                              'position':(11,95),
                              'shadow':0.9,
                              'flatness':1.0,
                              'color':(1,1,1),
                              'hAlign':'center',
                              'vAttach':'bottom'})
                bs.animate(t,'opacity',{0:0.8})
        def recurringText():
                t = bs.newNode('text',
                       attrs={ 'text':texts[randrange(count)],
                              'scale':0.95,
                              'maxWidth':0,
                              'position':(0,120),
                              'shadow':1,
                              'flatness':1.0,
                              'hAlign':'center',
                              'vAttach':'bottom'})
                bs.animate(t,'opacity',{0: 0.0,500: 1.0,6500: 1.0,7000: 0.0})
                multiColor = {0:((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0)),500:((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0)),1000:((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0)),1500:((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0)),2000:((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0)),2500:((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0)),3000:((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0)),3500:((0+random.random()*1.0),(0+random.random()*1.0),(0+random.random()*1.0))}
                bsUtils.animateArray(t,'color',3,multiColor,True)
                bs.gameTimer(7000,t.delete)
        bs.gameTimer(10,bs.Call(text))
	import settings
	if settings.enableCoinSystem == 0:
		bs.gameTimer(10,bs.Call(recurringText))
		bs.gameTimer(7000,bs.Call(recurringText),repeat = True)
        
        # set some defaults
        bsGlobals = bs.getSharedObject('globals')
        # area-of-interest bounds
        aoiBounds = self.getDefBoundBox("areaOfInterestBounds")
        if aoiBounds is None:
            print 'WARNING: no "aoiBounds" found for map:',self.getName()
            aoiBounds = (-1,-1,-1,1,1,1)
        bsGlobals.areaOfInterestBounds = aoiBounds
        # map bounds
        mapBounds = self.getDefBoundBox("levelBounds")
        if mapBounds is None:
            print 'WARNING: no "levelBounds" found for map:',self.getName()
            mapBounds = (-30,-10,-30,30,100,30)
        bsInternal._setMapBounds(mapBounds)
        # shadow ranges
        try: bsGlobals.shadowRange = [
                self.defs.points[v][1] for v in 
                ['shadowLowerBottom','shadowLowerTop',
                 'shadowUpperBottom','shadowUpperTop']]
        except Exception: pass
        # in vr, set a fixed point in space for the overlay to show up at..
        # by default we use the bounds center but allow the map to override it
        center = ((aoiBounds[0]+aoiBounds[3])*0.5,
                  (aoiBounds[1]+aoiBounds[4])*0.5,
                  (aoiBounds[2]+aoiBounds[5])*0.5)
        if vrOverlayCenterOffset is not None:
            center = (center[0]+vrOverlayCenterOffset[0],
                      center[1]+vrOverlayCenterOffset[1],
                      center[2]+vrOverlayCenterOffset[2])
        bsGlobals.vrOverlayCenter = center
        bsGlobals.vrOverlayCenterEnabled = True
        self.spawnPoints = self.getDefPoints("spawn") or [(0,0,0,0,0,0)]
        self.ffaSpawnPoints = self.getDefPoints("ffaSpawn") or [(0,0,0,0,0,0)]
        self.spawnByFlagPoints = (self.getDefPoints("spawnByFlag")
                                  or [(0,0,0,0,0,0)])
        self.flagPoints = self.getDefPoints("flag") or [(0,0,0)]
        self.flagPoints = [p[:3] for p in self.flagPoints] # just want points
        self.flagPointDefault = self.getDefPoint("flagDefault") or (0,1,0)
        self.powerupSpawnPoints = self.getDefPoints("powerupSpawn") or [(0,0,0)]
        self.powerupSpawnPoints = \
            [p[:3] for p in self.powerupSpawnPoints] # just want points
        self.tntPoints = self.getDefPoints("tnt") or []
        self.tntPoints = [p[:3] for p in self.tntPoints] # just want points
        self.isHockey = False
        self.isFlying = False
        self._nextFFAStartIndex = 0
        
bsMap.Map.__init__ = __init__
