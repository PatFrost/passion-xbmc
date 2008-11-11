
# script constants
__script__ = "Installeur-Passion"
__plugin__ = "Unknown"
__author__ = "Team Passion-XBMC"
__url__    = "http://passion-xbmc.org/index.php"
__svn_url__ = "http://code.google.com/p/passion-xbmc/source/browse/#svn/trunk/Scripts/Installeur-Passion"
__credits__ = "Team XBMC, http://xbmc.org/"
__platform__  = "xbmc media center"
__date__    = "11-11-2008"
__version__ = "1.0.0dev"
__svn_revision__ = 0


import os
import sys
import ConfigParser

import xbmc
import xbmcgui

from resources.libs.script_log import *


# INITIALISATION CHEMIN RACINE
ROOTDIR = os.getcwd().replace( ";", "" )

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
__language__ = xbmc.Language( ROOTDIR, "french" ).getLocalizedString

DIALOG_PROGRESS = xbmcgui.DialogProgress()


def MAIN():
    LOG( LOG_INFO, str( "*" * 85 ) )
    LOG( LOG_INFO, "Lanceur".center( 85 ) )
    LOG( LOG_INFO, str( "*" * 85 ) )

    # INITIALISATION CHEMINS DE FICHIER LOCAUX
    fichier = os.path.join(ROOTDIR, "resources", "conf.cfg")
    config = ConfigParser.ConfigParser()
    config.read(fichier)

    if not config.getboolean('InstallPath','pathok'):
        # GENERATION DES INFORMATIONS LOCALES
        DIALOG_PROGRESS.update( -1, __language__( 32101 ), __language__( 32110 ) )
        from resources.libs import CONF
        CONF.SetConfiguration()

    # VERIFICATION DE LA MISE A JOUR 
    DIALOG_PROGRESS.update( -1, __language__( 32102 ), __language__( 32110 ) )
    from resources.libs import CHECKMAJ
    CHECKMAJ.go()

    config.read(fichier)

    dialog_error = False
    if not config.getboolean('Version','UPDATING'):
        try:
            # LANCEMENT DU SCRIPT
            from resources.libs import INSTALLEUR
            INSTALLEUR.go()
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info() )
            dialog_error = True
    else:
        # LANCEMENT DE LA MISE A JOUR
        try:
            scriptmaj = config.get('Version','SCRIPTMAJ')
            xbmc.executescript(scriptmaj)

            #from resources.libs import INSTALLEUR
            #INSTALLEUR.go()
        except:
            LOG( LOG_ERROR, "default : Exception pendant le chargement et/ou La mise a jour" )
            EXC_INFO( LOG_ERROR, sys.exc_info() )
            dialog_error = True

    DIALOG_PROGRESS.close()

    if dialog_error: xbmcgui.Dialog().ok( __language__( 32111 ), __language__( 32112 ) )


if __name__ == "__main__":
    try:
        DIALOG_PROGRESS.create( __language__( 32000 ), "", "" )
        MAIN()
    except:
        EXC_INFO( LOG_ERROR, sys.exc_info() )
        DIALOG_PROGRESS.close()