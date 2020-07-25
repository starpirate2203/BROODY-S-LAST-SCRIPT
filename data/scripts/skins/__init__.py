from .setup import *
from .prefix import PermissionEffect
import bs
import bsInternal
import bsSpaz

gSettingsEnabled = hasattr(bs, "get_settings")

def __init__(self, color=(1, 1, 1), highlight=(0.5, 0.5, 0.5), character="Spaz", player=None, powerupsExpire=True):
    a = bsInternal._getForegroundHostActivity()
    if player is None: player = bs.Player(None)
    if gSettingsEnabled: settings = bs.get_settings()
    else: settings = {}
    if a is not None:
        with bs.Context(a):
            account = player.getInputDevice()._getAccountName(True)
            skin = settings.get("skins", {}).get(account, None)
            if skin is not None:
                character_name = get_unformat_skin_name(skin)
                if character_name is not None and character_name in bsSpaz.appearances.keys():
                    character = character_name
    bsSpaz.Spaz.__init__(self, color=color, highlight=highlight, character=character, sourcePlayer=player,
                  startInvincible=True, powerupsExpire=powerupsExpire)
    self.lastPlayerAttackedBy = None
    self.lastAttackedTime = 0
    self.lastAttackedType = None
    self.heldCount = 0
    self.lastPlayerHeldBy = None
    self._player = player
    if skin not in ["invincible"]:
        prefixes = settings.get("prefixes", {})
        vips, admins, hosts = settings.get("vips", []), settings.get("admins", []), settings.get("hosts", [])
        profiles = self._player.getInputDevice()._getPlayerProfiles()
        if profiles == [] or profiles == {}: profiles = bs.getConfig()['Player Profiles']
        if prefixes.get(account) is not None:
            prefix_info = prefixes[account]
            if isinstance(prefix_info, list): prefix_info = {prefix_info[0]: prefix_info[1]}
            PermissionEffect(owner=self.node, prefix=prefix_info.values()[0], prefixAnim={0: self.node.color, 5000: self.node.highlight, 10000: self.node.color}, type=prefix_info.keys()[0])
        elif settings.get("admins_prefix", True):
            if account in vips or account in admins or account in hosts:
                anim = {0: (0, 1, 1), 2500: (1, 0, 1), 5000: (0, 1, 1)}
                if account in hosts: prefix = 'Host'
                elif account in admins: prefix = 'Admin'
                elif account in vips: prefix, anim = 'VIP', {0: (1, 1, 0), 2500: (1, 0.75, 0), 5000: (1, 1, 0)}
                PermissionEffect(owner=self.node, prefix=prefix, prefixAnim=anim)
    if player.exists():
        playerNode = bs.getActivity()._getPlayerNode(player)
        self.node.connectAttr('torsoPosition', playerNode, 'position')
        check_skin(account, self.node)

bsSpaz.PlayerSpaz.__init__ = __init__
