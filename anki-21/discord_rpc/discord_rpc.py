#
#   Author: Kamoshi
#

from anki.hooks import addHook, wrap
from anki import version as anki_version
from aqt import mw
from aqt.utils import showInfo

from . import rpc
import time

############# SETUP #############

currentDeckID = None

client_id = '529708440407506946'
client = rpc.DiscordIpcClient.for_platform(client_id)

start_time = int(time.time()) # Epoch time in seconds on app start

############# SETUP #############

def updateActivity(state, details, display_time):
    """Updates the activity to match what the user is doing"""
    activity = {
        "details" : state,
        "assets": {
            "large_image": "icon"
        }
    }
    if details:
        activity["state"] = details
    if display_time:
        activity["timestamps"] = {}
        activity["timestamps"]["start"] = display_time
    client.set_activity(activity)

def getCardsToString(deckID):
    """Get number of cards in the deck to learn"""
    if deckID:
        deckName = mw.col.decks.name(deckID)
        for deck in mw.col.sched.deckDueList():
            name = deck[0]
            if name.startswith(deckName):
                toRev = deck[2]
                toLea = deck[3]
                toNew = deck[4]
        return "R: " + str(toRev) + " | L: " + str(toLea) + " | N: " + str(toNew)
        

# ANKI STATE CHANGE
def afterStateChangeEvent(state, oldState):
    """ Invoked after anki state changes """
    if state == "deckBrowser" or state == "overview":
        currentDeckID = None
        if oldState != "deckBrowser" and oldState != "overview":
            updateActivity("Browsing decks", None, None)
            
    elif state == "review":
        currentDeckID = mw.col.decks.current()['id']
        deckName = mw.col.decks.name(currentDeckID)
        start_time = int(time.time())
        string = getCardsToString(currentDeckID)
        updateActivity(deckName, string, start_time)
    else:
        currentDeckID = None
        # updateActivity("Unknown state", None, None)


# STATE CHANGE HOOK
# States:
#   -> overview
#   -> deckBrowser
#   -> resetRequired
#   -> review
#   -> sync
#   -> profileManager
#   -> startup
addHook("afterStateChange", afterStateChangeEvent)
