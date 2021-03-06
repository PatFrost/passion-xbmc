
#Modules General
import sys
from traceback import print_exc

#Modules XBMC
from xbmcaddon import Addon

# addon constants
__addonID__   = "repository.xbmc.builds" # get addon id
__settings__  = Addon( __addonID__ ) # get Addon object
__addonName__ = __settings__.getAddonInfo( "name" )


def runAddon():
    api = None
    try:
        if ( "dlprogress" in sys.argv[ 2 ] ):
            from resources.addonAPI.container import DIALOG_DL_PROGRESS
            from xbmc import executebuiltin
            executebuiltin( DIALOG_DL_PROGRESS )

        elif ( "timeline" in sys.argv[ 2 ] ):
            from resources.addonAPI.repo import getChangelog
            from resources.addonAPI.TextViewer import showText
            text = getChangelog()
            showText( "Trac Timeline", text )

        elif ( "action=" in sys.argv[ 2 ] ):
            import resources.addonAPI.action as api

        else:
            import resources.addonAPI.container as api
    except:
        print_exc()

    if api:
        api.Main()


if ( __name__ == "__main__" ):
    runAddon()
