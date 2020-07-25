from bsSpaz import *

t = Appearance("Tntman")

t.colorTexture = "tnt"
t.colorMaskTexture = "tnt"

t.iconTexture = "logo"
t.iconMaskTexture = "logo"

t.headModel = "tnt"
t.torsoModel = "buttonNull"
t.pelvisModel = "buttonNull"
t.upperArmModel = "buttonNull"
t.foreArmModel = "buttonNull"
t.handModel = "boxingGlove"
t.upperLegModel = "buttonNull"
t.lowerLegModel = "buttonNull"
t.toesModel = "buttonNull"

t.jumpSounds=["spazJump01",
              "spazJump02",
              "spazJump03",
              "spazJump04"]
t.attackSounds=["spazAttack01",
                "spazAttack02",
                "spazAttack03",
                "spazAttack04"]
t.impactSounds=["spazImpact01",
                "spazImpact02",
                "spazImpact03",
                "spazImpact04"]
t.deathSounds=["spazDeath01"]
t.pickupSounds=["spazPickup01"]
t.fallSounds=["spazFall01"]

t.style = 'bones'

t = Appearance("Bombman")

t.colorTexture = "bombColor"
t.colorMaskTexture = "bombColor"

t.iconTexture = "glow"
t.iconMaskTexture = "null"

t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)

t.headModel = "bomb"
t.torsoModel = "warriorTorso"
t.pelvisModel = "warriorPelvis"
t.upperArmModel = "warriorUpperArm"
t.foreArmModel = "warriorForeArm"
t.handModel = "warriorHand"
t.upperLegModel = "warriorUpperLeg"
t.lowerLegModel = "warriorLowerLeg"
t.toesModel = "warriorToes"
warriorSounds = ['warrior1', 'warrior2', 'warrior3', 'warrior4']
warriorHitSounds = ['warriorHit1', 'warriorHit2']
t.attackSounds = warriorSounds
t.jumpSounds = warriorSounds
t.impactSounds = warriorHitSounds
t.deathSounds=["warriorDeath"]
t.pickupSounds = warriorSounds
t.fallSounds=["warriorFall"]

t.style = 'bones'

t = Appearance("Bagged Taobao")

t.colorTexture = "robotColor"
t.colorMaskTexture = "robotColorMask"

t.iconTexture = "bombButton"
t.iconMaskTexture = "logo"

t.headModel = "aliHead"
t.torsoModel = "buttonNull"
t.pelvisModel = "buttonNull"
t.upperArmModel = "buttonNull"
t.foreArmModel = "buttonNull"
t.handModel = "boxingGlove"
t.upperLegModel = "buttonNull"
t.lowerLegModel = "buttonNull"
t.toesModel = "buttonNull"

t.jumpSounds=["spazJump01",
              "spazJump02",
              "spazJump03",
              "spazJump04"]
t.attackSounds=["spazAttack01",
                "spazAttack02",
                "spazAttack03",
                "spazAttack04"]
t.impactSounds=["spazImpact01",
                "spazImpact02",
                "spazImpact03",
                "spazImpact04"]
t.deathSounds=["spazDeath01"]
t.pickupSounds=["spazPickup01"]
t.fallSounds=["spazFall01"]

t.style = 'bunny'