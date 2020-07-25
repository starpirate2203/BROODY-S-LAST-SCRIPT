import bs
import random
import bsUtils

class PermissionEffect(object):
    def __init__(self, owner=None, prefix='', prefixColor=(1, 1, 1), prefixAnim={0: (0, 0, 0), 10: (1, 1, 1)}, prefixAnimate=True, particles=True, type='spark'):
        self.owner = owner
        self.particles_type = type
        self.prefix_string = prefix
        def a():
            self.emit()
        if self.owner is not None:
            if particles: self.timer = bs.Timer(100, bs.Call(a), repeat=True)
            m = bs.newNode('math', owner=self.owner, attrs={'input1': (0, 1.55, 0), 'operation': 'add'})
            self.owner.connectAttr('position', m, 'input2')
            self.prefix = bs.newNode('text', owner=self.owner,
                                     attrs={'text': self.prefix_string, 'inWorld': True, 'shadow': 0.7, 'flatness': 1.0,
                                            'color': prefixColor, 'scale': 0.01, 'hAlign': 'center', 'maxWidth': 100})
            m.connectAttr('output', self.prefix, 'position')
            if prefixAnimate: bsUtils.animateArray(self.prefix, 'color', 3, prefixAnim, True)

    def emit(self):
        if self.owner.exists():
            bs.emitBGDynamics(position=tuple([self.owner.position[i]+random.uniform(-0.3,0.3) for i in range(3)]),
                              velocity=(0, 0, 0),
                              count=10,
                              scale=0.385 + random.uniform(-0.2,0.2),
                              spread=0.05,
                              chunkType=self.particles_type)

