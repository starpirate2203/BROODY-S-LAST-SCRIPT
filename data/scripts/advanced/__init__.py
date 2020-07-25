from .text import *
from .settings import get_setting, set_setting, Settings, \
    gSettingsPath, get_settings, _gData, get_settings, \
    reload_settings, rewrite_settings, check_settings_file, \
    save_settings, write_log, set_settings
from .servers import *
import bs, bsInternal

def get_nickname_by_client_id(clientID=-1):
    roster, activity = bsInternal._getGameRoster(), bsInternal._getForegroundHostActivity()
    nickname, is_account = None, False
    if not isinstance(clientID, int): raise ValueError("clientID must be integer.")
    if len(roster) > 0:
        client = [i for i in roster if i["clientID"] == clientID]
        client = client[0] if len(client) > 0 else None
        if client is not None:
            if len(client["players"]) > 0: nickname = ("/").join([i["name"][:10]+"..." if len(i["name"]) > 10 else i["name"] for i in client["players"]])
            else: nickname, is_account = client["displayString"], True
    elif clientID == -1:
        if len(activity.players) > 0: nickname = ("/").join([i.getName() for i in activity.players])
        else: nickname, is_account = bsInternal._getAccountName(), True
    return nickname

