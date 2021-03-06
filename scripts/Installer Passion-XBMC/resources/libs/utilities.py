"""
Module de partage des fonctions et des constantes

"""

#En gros seul les fonctions et variables de __all__ vont etre importees lors du "import *"
#The public names defined by a module are determined by checking the module's namespace
#for a variable named __all__; if defined, it must be a sequence of strings which are names defined
#or imported by that module. The names given in __all__ are all considered public and are required to exist.
#If __all__ is not defined, the set of public names includes all names found in the module's namespace
#which do not begin with an underscore character ("_"). __all__ should contain the entire public API.
#It is intended to avoid accidentally exporting items that are not part of the API (such as library modules
#which were imported and used within the module).
__all__ = [
    # public names
    "copy_dir",
    "copy_inside_dir",
    "SYSTEM_PLATFORM",
    "parse_rss_xml",
    "set_web_navigator",
    "is_playable_media",
    "getUserSkin",
    "getSkinColors",
    "get_default_hex_color",
    "getSkinsListing",
    "add_pretty_color",
    "bold_text",
    "italic_text",
    "set_xbmc_carriage_return",
    "unescape",
    "strip_off",
#    "strip_off_CSV",
    "Settings",
    "get_infos_path",
    "replaceStrs",
    "set_cache_thumb_name",
    ]

#Modules general
import os
import re
import sys
import time
import htmllib
from traceback import print_exc

import elementtree.ElementTree as ET

#modules XBMC
import xbmc
import xbmcgui

# Modules Custom
import shutil2


#REPERTOIRE RACINE ( default.py )
CWD = os.getcwd().rstrip( ";" )

BASE_SETTINGS_PATH = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "settings.txt" )
RSS_FEEDS_XML = os.path.join( CWD, "resources", "RssFeeds.xml" )

BASE_THUMBS_PATH = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "Thumbnails" )


def copy_dir( dirname, destination, overwrite=True ):
    if not overwrite and os.path.isdir( destination ):
        shutil2.rmtree( destination )
    shutil2.copytree( dirname, destination, overwrite=overwrite )


def copy_inside_dir( dirname, destination, overwrite=True ):
    list_dir = os.listdir( dirname )
    for file in list_dir:
        src = os.path.join( dirname, file )
        dst = os.path.join( destination, file )
        if os.path.isfile( src ):
            if not os.path.isdir( os.path.dirname( dst ) ):
                os.makedirs( os.path.dirname( dst ) )
            if not overwrite and os.path.isfile( dst ):
                os.unlink( dst )
            shutil2.copyfile( src, dst, overwrite=overwrite )
        elif os.path.isdir( src ):
            if not overwrite and os.path.isdir( dst ):
                shutil2.rmtree( dst )
            shutil2.copytree( src, dst, overwrite=overwrite )


def set_cache_thumb_name( path ):
    try:
        fpath = path
        # make the proper cache filename and path so duplicate caching is unnecessary
        filename = xbmc.getCacheThumbName( fpath )
        thumbnail = os.path.join( BASE_THUMBS_PATH, filename[ 0 ], filename )
        preview_pic = os.path.join( BASE_THUMBS_PATH, "originals", filename[ 0 ], filename )
        # if the cached thumbnail does not exist check for dir does not exist create dir
        if not os.path.isdir( os.path.dirname( preview_pic ) ):
            os.makedirs( os.path.dirname( preview_pic ) )
        if not os.path.isdir( os.path.dirname( thumbnail ) ):
            os.makedirs( os.path.dirname( thumbnail ) )
        return thumbnail, preview_pic
    except:
        print_exc()
        return "", ""

def get_system_platform():
    """ fonction: pour recuperer la platform que xbmc tourne """
    platform = "unknown"
    if xbmc.getCondVisibility( "system.platform.linux" ):
        platform = "linux"
    elif xbmc.getCondVisibility( "system.platform.xbox" ):
        platform = "xbox"
    elif xbmc.getCondVisibility( "system.platform.windows" ):
        platform = "windows"
    elif xbmc.getCondVisibility( "system.platform.osx" ):
        platform = "osx"
    return platform

SYSTEM_PLATFORM = get_system_platform()


def parse_rss_xml( xml_path=RSS_FEEDS_XML ):
    """ fonction: pour parser le fichier RssFeeds.xml """
    feeds = {}
    try:
        feed = open( xml_path )
        tree = ET.parse( feed )
        feed.close()
        for elems in tree.getroot():
            try:
                urlset, title, feed = elems.getiterator()
                urlset = urlset.attrib.get( "id" )
                if urlset:
                    feeds[ urlset ] = {
                        "updateinterval": int( feed.attrib.get( "updateinterval", "30" ) ),
                        "title": title.text,
                        "feed": feed.text,
                        }
            except:
                print_exc()
        del tree
    except:
        print_exc()
    return feeds


def set_web_navigator( navigator="" ):
    """ fonction: pour parcourir le navigateur web """
    mask = ( "", ".bat|.exe", )[ ( SYSTEM_PLATFORM == "windows" ) ]
    browser_path = xbmcgui.Dialog().browse( 1, sys.modules[ "__main__" ].__language__( 520 ), "files", mask, False, False, navigator )
    if browser_path:
        title = os.path.basename( browser_path ).split( "." )[ 0 ].title()
        keyboard = xbmc.Keyboard( title, sys.modules[ "__main__" ].__language__( 521 ) )
        keyboard.doModal()
        if keyboard.isConfirmed():
            title = keyboard.getText()
        return title, browser_path


def is_playable_media( filename, media="picture" ):
    """
    getSupportedMedia(media) -- Returns the supported file types for the specific media as a string.
    media          : string - media type
    *Note, media type can be (video, music, picture).
           The return value is a pipe separated string of filetypes (eg. '.mov|.avi').
           You can use the above as keywords for arguments and skip certain optional arguments.
           Once you use a keyword, all following arguments require the keyword.
    example:
      - mTypes = xbmc.getSupportedMedia('video')
    """
    media_types = xbmc.getSupportedMedia( media ).split( "|" )
    try:
        return os.path.splitext( filename )[ 1 ].lower() in media_types
    except:
        print_exc()
        # si on arrive ici le retour est automatiquement None


def getUserSkin():
    """ FONCTION POUR RECUPERER LE THEME UTILISE PAR L'UTILISATEUR """
    # get user preference skin settings
    try: skin_setting = Settings().get_settings().get( "current_skin", "Default.HD" )
    except: skin_setting = "Default.HD"
    current_skin = xbmc.getSkinDir()
    if skin_setting != "Default.HD" and os.path.exists( os.path.join( CWD, "resources", "skins", skin_setting ) ):
        current_skin = skin_setting
    #if not current_skin: current_skin = xbmc.getSkinDir()
    force_fallback = os.path.exists( os.path.join( CWD, "resources", "skins", current_skin ) )
    if not force_fallback: current_skin = "Default.HD"
    return current_skin, force_fallback


def getSkinColors():
    """ FONCTION POUR RECUPERER LES COULEURS THEME """
    try:
        current_skin, force_fallback = getUserSkin()
        current_skin = os.path.join( CWD, "resources", "skins", current_skin )
        colors_file = os.path.join( current_skin, "colors", "colors.xml" )
        if os.path.exists( colors_file ):
            colors = re.compile( '<color name="(.*?)">(.*?)</color>' ).findall( file( colors_file, "r" ).read() )
            return colors
    except:
        print_exc()


def get_default_hex_color( default="Default" ):
    default_hex_color = "FFFFFFFF"
    try:
        default_hex_color = dict( getSkinColors() ).get( default, "FFFFFFFF" )
        #print default, default_hex_color
    except TypeError:
        pass
    except:
        print_exc()
    return default_hex_color


def getSkinsListing():
    skins_dir = os.path.join( CWD, "resources", "skins" )
    skins = [ skin for skin in os.listdir( skins_dir ) if ".svn" not in skin and os.path.isdir( os.path.join( skins_dir, skin ) ) ]
    del skins[ skins.index( "Default.HD" ) ]
    return [ "Default.HD" ] + sorted( skins, key=lambda l: l.lower() )


#NOTE: CE CODE PEUT ETRE REMPLACER PAR UN CODE MIEUX FAIT
def add_pretty_color( word, start="all", end=None, color=None ):
    """ FONCTION POUR METTRE EN COULEUR UN MOT OU UNE PARTIE """
    try:
        if color and start == "all":
            pretty_word = "[COLOR=" + color + "]" + word + "[/COLOR]"
        else:
            pretty_word = []
            for letter in word:
                if color and letter == start:
                    pretty_word.append( "[COLOR=" + color + "]" )
                elif color and letter == end:
                    pretty_word.append( letter )
                    pretty_word.append( "[/COLOR]" )
                    continue
                pretty_word.append( letter )
            pretty_word = "".join( pretty_word )
        return pretty_word
    except:
        print_exc()
        return word


def bold_text( text ):
    """ FONCTION POUR METTRE UN MOT GRAS """
    return "[B]%s[/B]" % ( text, )


def italic_text( text ):
    """ FONCTION POUR METTRE UN MOT ITALIQUE """
    return "[I]%s[/I]" % ( text, )


def set_xbmc_carriage_return( text ):
    """ only for xbmc """
    text = text.replace( "\r\n", "[CR]" )
    text = text.replace( "\n\n", "[CR]" )
    text = text.replace( "\n",   "[CR]" )
    text = text.replace( "\r\r", "[CR]" )
    text = text.replace( "\r",   "[CR]" )
    text = text.replace( "</br>",   "[CR]" )
    return text


def strip_off( text, by="", xbmc_labels_formatting=False ):
    """ FONCTION POUR RECUPERER UN TEXTE D'UN TAG """
    if xbmc_labels_formatting:
        #text = re.sub( "\[url[^>]*?\]|\[/url\]", by, text )
        text = text.replace( "[", "<" ).replace( "]", ">" )
    return re.sub( "(?s)<[^>]*>", by, text )

def unescape(s):
    """
    remplace les sequences d'echappement par leurs caracteres equivalent
    """
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()

def replaceStrs( s, *args ): 
    """
    Replace all ``(frm, to)`` tuples in `args` in string `s`.
    By Alexander Schmolck ( http://markmail.org/message/r67z77skcqcbo5nr )
    replaceStrs("nothing is better than warm beer", ... ('nothing','warm beer'), ('warm beer','nothing')) 'warm beer is better than nothing'
    """ 
    if args == (): 
        return s 
    mapping = dict([(frm, to) for frm, to in args]) 
    return re.sub("|".join(map(re.escape, mapping.keys())), lambda match:mapping[match.group(0)], s)
    
class Settings:
    """ this function comes from apple movie trailer """
    def _settings_defaults_values( self ):
        defaults = {
            # GENERAL
            "updating": False,
            "pardir_not_hidden": 1,
            "hide_extention": True,
            "update_startup": True,
            "xbmc_xml_update": False,
            "rss_feed": ( "0", "1", )[ ( xbmc.getLanguage().lower() == "french" ) ],
            "script_debug": False,
            "manager_view_mode": 50,
            "main_view_mode": 50,
            "server_shortcut_button": "Passion XBMC",
            # SKINS
            "show_plash": False,
            "current_skin": "Default.HD",
            "skin_colours_path": "default",
            "skin_colours": "",
            "labels_colours": "",
            "thumb_size": ( "512", "192" )[ ( SYSTEM_PLATFORM == "xbox" ) ],
            # SERVEUR FTP
            "host": "xbmc.funtube.fr",
            "user": "anonymous",
            "password": "xxxx",
            # FORUM
            "topics_limit": "5",
            "web_title": "",
            "hide_forum": False,
            "web_navigator": "",
            "win32_exec_wait": False,
            }
        return defaults

    def get_settings( self, defaults=False ):
        """ read settings """
        try:
            settings = {}
            if ( defaults ): raise
            settings_file = open( BASE_SETTINGS_PATH, "r" )
            settings = eval( settings_file.read() )
            settings_file.close()
            if settings:
                settings = self._check_compatibility( settings )
        except:
            settings = self._use_defaults( settings, save=( defaults == False ) )
        return settings

    def _check_compatibility( self, current_settings={} ):
        try:
            if sorted( current_settings.keys() ) != sorted( self._settings_defaults_values().keys() ):
                print "Settings: [added default values for missing settings]"
                return self._use_defaults( current_settings )
        except:
            print_exc()
        return current_settings

    def _use_defaults( self, current_settings=None, save=True ):
        """ setup default values if none obtained """
        #TODO: verifier pourquoi la ligne suivante fait planter XBMC sous Mac
        #print "Settings: [used default settings]"
        settings = {}
        defaults = self._settings_defaults_values()
        for key, value in defaults.items():
            # add default values for missing settings
            settings[ key ] = current_settings.get( key, defaults[ key ] )
        if ( save ):
            ok = self.save_settings( settings )
        return settings

    def save_settings( self, settings ):
        """ save settings """
        try:
            settings_file = open( BASE_SETTINGS_PATH, "w" )
            settings_file.write( repr( settings ) )
            settings_file.close()
            return True
        except:
            print_exc()
            return False


try:
    """
    getRegion(id) -- Returns your regions setting as a string for the specified id.
    id             : string - id of setting to return
    *Note, choices are (dateshort, datelong, time, meridiem, tempunit, speedunit)
           You can use the above as keywords for arguments and skip certain optional arguments.
           Once you use a keyword, all following arguments require the keyword.
    example:
      - date_long_format = xbmc.getRegion('datelong')
    """
    date_short_format = xbmc.getRegion( "dateshort" ).replace( "MM", "M" ).replace( "DD", "D" ).replace( "M", "%m" ).replace( "D", "%d" ).replace( "YYYYY", "%Y" ).replace( "YYYY", "%Y" )
    time_format = xbmc.getRegion( "time" ).replace( "h", "%I" ).replace( "H", "%H" ).replace( "mm", "%M" ).replace( "ss", "%S" ).replace( "xx", "%p" )
    DATE_TIME_FORMAT = date_short_format + " | " + time_format
except:
    DATE_TIME_FORMAT = "%d-%m-%y | %H:%M:%S"


def get_infos_path( path, get_size=False, report_progress=None ):
    # Return the system's ctime which, on some systems (like Unix) is the time of the last change, and, on others (like Windows), is the creation time for path. The return value is a number giving the number of seconds since the epoch (see the time module). Raise os.error if the file does not exist or is inaccessible. New in version 2.3.
    try: c_time = time.strftime( DATE_TIME_FORMAT, time.localtime( os.path.getctime( path ) ) )#.replace( " | 0", " |  " )
    except: c_time = ""

    # Return the time of last access of path. The return value is a number giving the number of seconds since the epoch (see the time module). Raise os.error if the file does not exist or is inaccessible. New in version 1.5.2. Changed in version 2.3: If os.stat_float_times() returns True, the result is a floating point number.
    try: last_access = time.strftime( DATE_TIME_FORMAT, time.localtime( os.path.getatime( path ) ) )#.replace( " | 0", " |  " )
    except: last_access = ""

    # Return the time of last modification of path. The return value is a number giving the number of seconds since the epoch (see the time module). Raise os.error if the file does not exist or is inaccessible. New in version 1.5.2. Changed in version 2.3: If os.stat_float_times() returns True, the result is a floating point number.
    try: last_modification = time.strftime( DATE_TIME_FORMAT, time.localtime( os.path.getmtime( path ) ) )#.replace( " | 0", " |  " )
    except: last_modification = ""

    # Return the size, in bytes, of path. Raise os.error if the file does not exist or is inaccessible. New in version 1.5.2.
    # calculate dir size "os.walk( path, topdown=False )"
    try:
        size = 0
        if os.access( path, os.R_OK ):
            if os.path.isfile( path ):
                try:
                    size += os.path.getsize( path )
                    if report_progress:
                        #print "Size: %s", path
                        report_progress.update( -1, sys.modules[ "__main__" ].__language__( 186 ), path, sys.modules[ "__main__" ].__language__( 361 ) + " %00s KB" % round( size / 1024.0, 2 ) )
                except: pass
            elif get_size:
                for root, dirs, files in os.walk( path ):#, topdown=False ):
                    for file in files:
                        try:
                            fpath = os.path.join( root, file )
                            if os.access( fpath, os.R_OK ):
                                size += os.path.getsize( fpath )
                                if report_progress:
                                    #print "Size: %s", fpath
                                    report_progress.update( -1, sys.modules[ "__main__" ].__language__( 186 ), fpath, sys.modules[ "__main__" ].__language__( 361 ) + " %00s KB" % round( size / 1024.0, 2 ) )
                        except:
                            print "Size: %s" % fpath
        if size <= 0:
            size = ""#"0.0 KB"
        elif size <= ( 1024.0 * 1024.0 ):
            size = "%00s KB" % round( size / 1024.0, 2 )
        elif size >= ( 1024.0 * 1024.0 ):
            size = "%00s MB" % round( size / 1024.0 / 1024.0, 2 )
        else:
            size = "%00s Bytes" % size
    except:
        print_exc()
        size = "0.0 KB"

    return size, c_time, last_access, last_modification
