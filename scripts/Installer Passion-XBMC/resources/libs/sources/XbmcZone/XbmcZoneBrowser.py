﻿"""
XbmcZoneBrowser: this module allows browsing of server content on the web server of Passion-XBMC.org
Module inspired from Dan Dar3 excellent work on the XBMC Zone Installer (thank you to him)
"""

# Modules general
import os
import sys
import urllib
from xml.dom import minidom #TODO: replace minidom by ET
from threading import Thread
from traceback import print_exc

# Modules custom
import Item
from utilities import *
#from CONSTANTS import *
from pil_util import makeThumbnails
from Browser import Browser, History, ImageQueueElement

import XbmcZoneItemInstaller

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__
LANGUAGE_IS_FRENCH = sys.modules[ "__main__" ].LANGUAGE_IS_FRENCH

SPECIAL_SCRIPT_DATA = sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA

    
class XbmcZoneBrowser(Browser):
    """
    Browse the item on the HTTP server of www.xbmczone.com
    """
    def __init__( self, *args, **kwargs  ):
        Browser.__init__( self, *args, **kwargs )
        self.curList = []  # Current list of item/category
        
        #self.racineDisplayList  = [ Item.TYPE_SCRIPT, Item.TYPE_PLUGIN ]
        self.racineDisplayList  = [ Item.TYPE_NEW, Item.TYPE_SCRIPT_CAT, Item.TYPE_PLUGIN ]

        # Create History instance in order to store browsing history
        self.history = History()

    def reset( self ):
        """
        Reset the browser (back to start page)
        """
        Browser.reset()

    def _mapType_Server2Local( self, serverType ):
        """
        Convert type string used on the server by local type
        """
        mapTypeSrv2Local = {"Script"         : Item.TYPE_SCRIPT ,
                            "Plugin"         : Item.TYPE_PLUGIN,
                            "Music Plugin"   : Item.TYPE_PLUGIN_MUSIC,
                            "Picture Plugin" : Item.TYPE_PLUGIN_PICTURES ,
                            "Program Plugin" : Item.TYPE_PLUGIN_PROGRAMS ,
                            "Video Plugin"   : Item.TYPE_PLUGIN_VIDEO }
        try:
            result = mapTypeSrv2Local[serverType]
        except:
            print sys.exc_info()
            print_exc()
            print_exc()
            result = None
        return result

    def _mapType_Local2Server( self, localType ):
        """
        Convert type string used locally by the one used on the server
        """
        mapTypeLocal2Srv = { Item.TYPE_SCRIPT          : "Script",
                             Item.TYPE_PLUGIN          : "Plugin",
                             Item.TYPE_PLUGIN_MUSIC    : "Music Plugin",
                             Item.TYPE_PLUGIN_PICTURES : "Picture Plugin",
                             Item.TYPE_PLUGIN_PROGRAMS : "Program Plugin",
                             Item.TYPE_PLUGIN_VIDEO    : "Video Plugin",
                             Item.TYPE_SCRIPT_CAT      : "Script" }
        try:
            result = mapTypeLocal2Srv[localType]
        except:
            print sys.exc_info()
            print_exc()
            print_exc()
            result = None
        return result

    def _createRootList(self):
        """
        Create and return the root list (all type available)
        Returns list and name of the list
        """
        list = []
        listTitle = _( 10 )

        # List the main categorie at the root level
        for cat in self.racineDisplayList:   
            item = {}
            #item['id']                = ""
            item['name']              = Item.get_type_title( cat )
            #item['parent']            = self.type
            item['downloadurl']       = None
            item['type']              = 'CAT'
            item['xbmc_type']         = cat
            item['cattype']           = cat
            item['previewpictureurl'] = None
            item['description']       = Item.get_type_title( cat )
            item['language']          = ""
            item['version']           = ""
            item['author']            = ""
            item['date']              = ""
            item['added']             = ""
            item['thumbnail']         = Item.get_thumb( cat )
            item['previewpicture']    = ""#Item.get_thumb( cat )
            item['image2retrieve']    = False # Temporary patch for reseting the flag after download (would be better in the thread in charge of the download)

            list.append(item)
            print item
            
        return listTitle, list

    def _createCatList( self, typeList):
        """
        Create and return the list of plugin categories
        Returns list and name of the list
        """
        categoryURL = {Item.TYPE_PLUGIN     : "http://www.xbmczone.com/installer/addon_categories.asp?type=Plugin",
                       Item.TYPE_SCRIPT_CAT : "http://www.xbmczone.com/installer/addon_categories.asp?type=Script"}
        list = []
        listTitle = Item.get_type_title( typeList )
        
        # Get page (XML)...
        usock = urllib.urlopen( categoryURL[ typeList ] )
        dom   = minidom.parse( usock )
        usock.close()
        

        # Add 'All' category
        item = {}
        item['cattype']   = self._mapType_Local2Server( typeList )
        item['name']      = _(2201)
        item['catname']      = "All"
        if self._mapType_Local2Server( typeList ) == "Script":
            item['xbmc_type'] = Item.TYPE_SCRIPT
        else: # Plugins
            item['xbmc_type'] = Item.TYPE_PLUGIN_VIDEO # Temporary patch ALL is not video plugin
        item['description']       = ""
        item['downloadurl']       = None
        item['type']              = 'CAT'
        item['previewpictureurl'] = None
        item['language']          = ""
        item['version']           = ""
        item['author']            = ""
        item['date']              = ""
        item['added']             = ""
        item['thumbnail']         = Item.get_thumb( item['xbmc_type'] )
        item['previewpicture']    = ""#Item.get_thumb( item['xbmc_type'] )
        item['image2retrieve']    = False # Temporary patch for reseting the flag after download (would be better in the thread in charge of the download)
        list.append(item)
        
        # Parse XML...
        for category in dom.getElementsByTagName('Category') :
            item = {}
            for child in category.childNodes:
                if child.localName == "Type" :
                    #type = child.childNodes[0].data
                    item['cattype'] = child.childNodes[0].data
                    #TODO: find cleaner solution for defining xbmc_type
                    if item['cattype'] == "Script":
                        #item['xbmc_type'] = self._mapType_Server2Local( child.childNodes[0].data )
                        item['xbmc_type'] = Item.TYPE_SCRIPT
                    
                elif child.localName == "Name" :
                    try:
                        item['name']    = child.childNodes[0].data
                        item['catname'] = child.childNodes[0].data
                        #item['xbmc_type'] = self._mapType_Server2Local( child.childNodes[0].data.decode("utf8") )
                        #TODO: find cleaner solution for defining xbmc_type
                        if "Plugin" in item['name']:
                            item['xbmc_type'] = self._mapType_Server2Local( child.childNodes[0].data )
                    except:
                        item['name']    = ""
                        item['catname'] = ""
                elif child.localName == "Description" :
                    try:
                        item['description'] = child.childNodes[0].data
                    except:
                        item['description'] = ""
            # Add entry...
#            listitem = xbmcgui.ListItem( category.replace("Plugin", ""), iconImage="DefaultFolder.png" )
#            xbmcplugin.addDirectoryItem( handle = int(sys.argv[ 1 ]), url = sys.argv[ 0 ] + '?action=plugin-list&category=%s' % urllib.quote( category ), listitem=listitem, isFolder=True)

            #item['parent']            = Item.TYPE_PLUGIN
            item['downloadurl']       = None
            item['type']              = 'CAT'
            item['previewpictureurl'] = None
            item['language']          = ""
            item['version']           = ""
            item['author']            = ""
            item['date']              = ""
            item['added']             = ""
            item['thumbnail']         = Item.get_thumb( item['xbmc_type'] )
            item['previewpicture']    = ""#Item.get_thumb( item['xbmc_type'] )
            item['image2retrieve']    = False # Temporary patch for reseting the flag after download (would be better in the thread in charge of the download)

            list.append(item)
            print item
            
        return listTitle, list

    def _createLastestList( self ):
        """
        Create and return the list of Lastest addons
        Returns list and name of the list
        """
        xmlURL = "http://www.xbmczone.com/installer/addon_list_edit.asp?category=New"
        listTitle = Item.get_type_title( Item.TYPE_NEW )
        
        # Get page (XML)...
        usock = urllib.urlopen( xmlURL )
        dom   = minidom.parse( usock )
        usock.close()
        
        # Parse XML...
        list = self._createItemList( dom )
        return listTitle, list


    def _createCatItemList( self, categoryItem ) :
        """
        Create the list of item to download based on a category (full category item is passed)
        """
        listTitle = categoryItem['name']
        #addon_zip_url      = "http://xbmczone.com/download.asp?id=%s" % ( params[ "id" ] )
        
#        category_search  = urllib.unquote( self.params[ "category" ] )        
#        where_to_install = os.path.join( xbmczone_constants.XBMC_HOME_PATH, "scripts" )
#        script_icon      = "DefaultScript.png"

        # Get XML data...
        usock = urllib.urlopen( "http://www.xbmczone.com/installer/addon_list.asp?type=%s&category=%s" %  ( urllib.quote( categoryItem['cattype'] ) , urllib.quote( categoryItem['catname'] ) ) )
        dom   = minidom.parse( usock )
        usock.close()
        
        # Parse XML...
        list = self._createItemList( dom )
        return listTitle, list
            


    def _createItemList( self, dom ) :
        """
        Parse XML and create the list of item defined in the XML file
        """
        list = []
        # Parse XML...
        for category_node in dom.getElementsByTagName('Addon') :
            item = {}
            for child in category_node.childNodes:
                # Type
                if child.localName == "Type" :
                    type = child.firstChild.data
                    #item['xbmc_type'] = self._mapType_Server2Local( child.firstChild.data.decode("utf8") )
                    #TODO: find cleaner solution for defining xbmc_type
                    if type == "Script":
                        item['xbmc_type'] = self._mapType_Server2Local( type )
                # Category
                elif child.localName == "Category" :
                    try:
                        category = child.firstChild.data
                    except:
                        category = None
                    item['cattype'] = category
                    #TODO: find cleaner solution for defining xbmc_type
                    if "Plugin" in category:
                        item['xbmc_type'] = self._mapType_Server2Local( category )
                # ID
                elif child.localName == "ID" :
                    try:
                        id = child.firstChild.data
                    except:
                        id = 0
                    item['downloadurl'] = "http://xbmczone.com/download.asp?id=%s" % ( id )
                # Name
                elif child.localName == "Name" :
                    try:
                        item['name'] = child.firstChild.data
                    except:
                        item['name'] = ""
                # File Name
                elif child.localName == "FileName" :
                    try:
                        item['filename'] = child.firstChild.data
                    except:
                        item['filename'] = ""
                # Version
                elif child.localName == "Version" :
                    #version = child.firstChild.data
                    try:
                        item['version'] = child.firstChild.data
                    except:
                        item['version'] = ""
                # Author
                elif child.localName == "Author" :
                    try:
                        item['author'] = child.firstChild.data
                    except:
                        item['author'] = ""
                # Date
                elif child.localName == "Date" :
                    try:
                        date          = child.firstChild.data
                        date_elements = date.split("/")
                        #item_date     = "%s-%s-%s" % ( date_elements[1].zfill(2), date_elements[0].zfill(2), date_elements[2] )                    
                        item['date']  = "%s-%s-%s" % ( date_elements[1].zfill(2), date_elements[0].zfill(2), date_elements[2] )                    
                    except:
                        item['date']  = ""
                # Description
                elif child.localName == "Description" :
                    try:
                        item['description'] = child.firstChild.data
                    except:
                        item['description'] = ""
                # Instructions
#                elif child.localName == "Instructions" :
#                    if child.firstChild != None :
#                        instructions = child.firstChild.data
#                    else :
#                        instructions = ""
                
            # Add entry...
            item['type']              = 'FIC'
            item['previewpictureurl'] = None
            item['language']          = ""
            item['added']             = ""
            item['thumbnail']         = Item.get_thumb( item['xbmc_type'] )
            item['previewpicture']    = ""#Item.get_thumb( item['xbmc_type'] )
            item['image2retrieve']    = False # Temporary patch for reseting the flag after download (would be better in the thread in charge of the download)
            
#            # Set image
#            self._setDefaultImages( item )
            
            list.append(item)
            print item
            
        return list


    def _getList( self, listItem=None ):
        """
        Retrieves list matching to a specific list Item
        """
        # Check type of selected item
        list = []
        curCategory = None
        #TODO: manage exception
        try:            
            if listItem != None:
                if listItem['type'] == 'CAT':
                    if listItem['xbmc_type'] == Item.TYPE_PLUGIN:
                        # root plugin case
                        curCategory, list = self._createCatList( Item.TYPE_PLUGIN )
                    elif listItem['xbmc_type'] == Item.TYPE_SCRIPT_CAT:
                        curCategory, list = self._createCatList( Item.TYPE_SCRIPT_CAT )
                    elif listItem['xbmc_type'] == Item.TYPE_NEW:
                        curCategory, list = self._createLastestList()
                    else:
                        # List of item to download case                  
                        curCategory, list = self._createCatItemList( listItem )
                else:
                    # Return the current list
                    #TODO: start download here?
                    print "This is not a category but an item (download)"
                    list = None
            else: # listItem == None 
                # 1st time (init), we display root list
                # List the main categorie at the root level
                curCategory, list = self._createRootList()
        except Exception, e:
            print "Exception during getNextList"
            print e
            print sys.exc_info()
            print_exc()
            print_exc()
            
        return curCategory, list


    def getNextList( self, index=0 ):
        """
        Returns the list of item (dictionary) on the server depending on the location we are on the server
        Retrieves list of the items and information about each item
        Other possible name: down
        """
        # Check type of selected item
        list = []
        #TODO: manage exception
        try:            
            if len(self.curList)> 0 :
                # Retrieve the list for the selected item
                self.curCategory, list = self._getList( self.curList[index] )
                self.history.push(self.curCategory, self.curList[index], "LIST_ITEM")
            else: # len(self.curList)<= 0 
                # 1st time (init), we display root list
                self.curCategory, list = self._getList()
                self.history.push(self.curCategory, None, "LIST_ITEM")
        except Exception, e:
            print "Exception during getNextList"
            print e
            print sys.exc_info()
            print_exc()
            print_exc()
        #TODO: find better solution, temporary fix for the case of empty list, with current implementation of hetPrevList backward is not possible when list is empty    
        if len( list ) > 0:
            # Replace current list
            self.curList = list
            
        return self.curList

    def getPrevList( self ):
        """
        Returns the list (up) of item (dictionary) on the server depending on the location we are on the server
        Go to previous page/list 
        Other possible name: Up
        """
        list = []
        #TODO: cover case of empty list
        item = self.curList[0] # We have to check the info one of the items in the list (why not the 1st?)

        try:
            # delete current page from history (we are going to load the previous one)
            self.history.pop()

            # Get previous entry (the one we gonna reload) but since we did a pop this is the current
            #previousIndex, previousHdl, previousHdlType, previousTitleLabel = self.history.getPrevious()
            previousCategory, previousItem, previousHdlType = self.history.getCurrent()
            
            # Get the list
            self.curCategory, list = self._getList( previousItem )

        except Exception, e:
            print "Exception during getPrevList"
            print e
            print sys.exc_info()
            print_exc()
            print_exc()
        # Replace current list
        self.curList = list
        return list

    def _downloadImage( self, picname ):
        """
        Download picture from the server, save it, create the thumbnail and return path of it
        """
        print "_downloadImage %s"%picname
        try:
        
            filetodlUrl = picname # image path on FTP server
            print "filetodlUrl"
            print filetodlUrl
            thumbnail, localFilePath = set_cache_thumb_name( picname )
            print thumbnail
            print localFilePath
#            loc = urllib.URLopener()
#            loc.retrieve(filetodlUrl, localFilePath)   
            ftp = ftplib.FTP( self.host, self.user, self.password )
            localFile = open( localFilePath, "wb" )
            try:
                ftp.retrbinary( 'RETR ' + filetodlUrl, localFile.write )
            except:
                print "_downloaddossier: Exception - Impossible de telecharger le fichier: %s" % remoteFilePath
                print_exc()
                thumbnail, localFilePath = "", ""
            localFile.close()
            ftp.quit()

            # remove file if size is 0 bytes and report error if exists error
            if localFilePath and os.path.isfile( localFilePath ):
                if os.path.getsize( localFilePath ) <= 0:
                    os.remove( localFilePath )
                    #TODO: create a thumb for the default image?
                    #TODO: return empty and manage default image at the level of the caller
                    thumbnail = "" 
                else:
                    thumb_size = int( self.thumb_size_on_load )
                    thumbnail = makeThumbnails( localFilePath, thumbnail, w_h=( thumb_size, thumb_size ) )
                    if thumbnail == "": thumbnail = localFilePath

#            if thumbnail and os.path.isfile( thumbnail ) and hasattr( listitem, "setThumbnailImage" ):
#                listitem.setThumbnailImage( thumbnail )
            else:
                thumbnail, localFilePath = "", ""
        except Exception, e:
            #TODO: create a thumb for the default image?
            #TODO: return empty and manage default image at the level of the caller
            thumbnail, localFilePath = "", "" 
            print "_downloadImage: Exception - Impossible to download the picture: %s" % picname
            print_exc()
        print "thumbnail = %s"%thumbnail
        print "localFilePath = %s"%localFilePath
        return thumbnail, localFilePath
    
    
    def reloadList( self ):
        """
        Reload and returns the current list
        """
        # Get current categorie id 
        catId = self.curList[0]['parent']
        return self.getNextList(catId)
    
    def getContextMenu( self ):
        """
        Returns the list of the commands available via the context menu
        """
        pass
    
    def getCategoryInfo( self, catId ):
        """
        Retrieves Categorie Name and Install path
        """
        title = ""
        path = ""
##        # Connect to Database
##        conn = sqlite.connect(self.db)
#        c = self.conn.cursor()  
#        try:
##            c.execute('''SELECT A.title, A.path
##                         FROM Install_Paths A, Categories B
##                         WHERE B.id_cat = ? 
##                         AND A.id_path = B.id_path
##                         ''',(catId,))
#            c.execute('''SELECT title, xbmc_type
#                         FROM Categories
#                         WHERE id_cat = ? 
#                         ''',(catId,))
#        except Exception, e:
#            print "getCategoryTitle: exception"
#            print e
#            
#        for row in c:
#            print row
#            title = row[0].encode( "cp1252" )
#            type = row[1].encode( "utf8" )
#        c.close()   
        print "title = %s"%title
        print "type = %s"%type
        return title, type


    def getInfo( self, index ):
        """
        Returns the information about a specific item (dictionnary)
        Returns a dictionnary with the structure:
        {name, description, icon, downloads, file, created, screenshot}
        Chaque index du dictionnaire renvoie à une liste d'occurences.
        Alimenter cette fonction avec l'id du fichier dont on veut obtenir les infos.
        """
                     
#        #ici une seule ligne est retournee par la requête
#        #pour chaque colonne fetchee par la requête on alimente un index du dictionnaire
#        dico = {}
#        for row in c:
#            print row
#            dico['id'] = row[0]
#            dico['name'] = (row[1].encode( "cp1252" ) )
#            dico['description'] = unescape( row[2].encode( "cp1252" ) )
#            dico['screenshot'] = row[3]
#            dico['downloads'] = row[4]
#            dico['filename'] = row[5]
#            dico['filesize'] = row[6]
#            dico['created'] = row[7]
#            dico['type']=row[8]
#        return dico
        pass
    
    def _loadData ( self ):
        """
        Load the data for the current page
        """
        pass
    
    def sortByDate( self ):
        """
        Returns current list sorted by date
        """
        pass

    def sortByLang( self ):
        """
        Returns current list sorted by language
        """
        pass
    
    def sortByAuthor( self ):
        """
        Returns current list sorted by author
        """
        pass    
    

    def isCat( self, index ):
        """
        Returns True when selected item is a category
        """
        if ( ( len(self.curList)> 0 ) and ( self.curList[index]['type'] == 'CAT' ) ):
            # Convert index to id
            return True
        else:
            return False
    
    def getInstaller( self, index ):
        """
        Returns an ItemInstaller instance
        """
        itemInstaller = None
        try:            
            if ( ( len(self.curList)> 0 ) and ( self.curList[index]['type'] == 'FIC' ) ):
                # Convert index to id
                name        = self.curList[index]['name']
                xbmc_type   = self.curList[index]['xbmc_type']
                downloadurl = self.curList[index]['downloadurl'].encode('utf8')
                #downloadurl = self.curList[index]['downloadurl']
                filename    = self.curList[index]['filename'].encode('utf8')
                #filename    = self.curList[index]['filename']
                
                # Create the right type of Installer Object
                itemInstaller = XbmcZoneItemInstaller.XbmcZoneItemInstaller( name, xbmc_type, filename, downloadurl )
            else:
                print "getInstaller: error impossible to install a category, it has to be an item "

        except Exception, e:
            print "Exception during getInstaller"
            print e
            print sys.exc_info()
            print_exc()
            print_exc()   
                 
        return itemInstaller

    def applyFilter( self ):
        pass



    def _downloadImage( self, picname ):
        """
        Download picture from the server, save it, create the thumbnail and return path of it
        """
        print "_downloadImage %s"%picname
        try:
        
            filetodlUrl = self.baseURLPreviewPicture + picname
            print "filetodlUrl"            
            print filetodlUrl
            thumbnail, localFilePath = set_cache_thumb_name( picname )
            print thumbnail
            print localFilePath
            loc = urllib.URLopener()
            loc.retrieve(filetodlUrl, localFilePath)   

            # remove file if size is 0 bytes and report error if exists error
            if localFilePath and os.path.isfile( localFilePath ):
                if os.path.getsize( localFilePath ) <= 0:
                    os.remove( localFilePath )
                    #TODO: create a thumb for the default image?
                    #TODO: return empty and manage default image at the level of the caller
                    thumbnail = "" 
                else:
                    thumb_size = int( self.thumb_size_on_load )
                    thumbnail = makeThumbnails( localFilePath, thumbnail, w_h=( thumb_size, thumb_size ) )
                    if thumbnail == "": thumbnail = localFilePath

#            if thumbnail and os.path.isfile( thumbnail ) and hasattr( listitem, "setThumbnailImage" ):
#                listitem.setThumbnailImage( thumbnail )
            else:
                thumbnail, localFilePath = "", ""
        except:
            print "_downloadImage: Exception - Impossible to downlod the picture: %s" % picname
            print_exc()
            #TODO: create a thumb for the default image?
            #TODO: return empty and manage default image at the level of the caller
            thumbnail, localFilePath = "", "" 
        print "thumbnail = %s"%thumbnail
        print "localFilePath = %s"%localFilePath
        return thumbnail, localFilePath

    def close( self ):
        """
        Close browser: i.e close connection, free memory ...
        """
        try: self.cancel_update_Images()
        except: print "XbmcZoneBrowser: error on close (cancel image)"



    