# -*- coding: utf-8 -*-
"""
Passion-XBMC Gallery Explorer Beta 2
Auteurs : Seb & Frost
"""

import urllib,sys,os
import xbmcplugin,xbmcgui,xbmc
import csv
import string
from elementtree import ElementTree as ET

#On définit le type du plugin
xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="Pictures" )

#Etat des variables initiales
SiteUrl = "http://passion-xbmc.org/"
BaseUrl = SiteUrl + "galleryexplorer.php?cat="
RootDir = os.getcwd().replace(';','')


urllib.urlcleanup()

_ = xbmc.getLocalizedString
ENCODING = ( "", "iso-8859-1", "UTF-8", )[ 2 ]

def _unicode( s, encoding="utf-8" ):
    """ customized unicode, don't raise UnicodeDecodeError exception, return no unicode str instead """
    try: s = unicode( s, encoding )
    except: pass
    return s

def download_as(url,folder=""):
    """
    propose un choix de noms de fichiers et / ou une saisie au clavier
    """
    dlpath=url.split('|')[0]
    picname=(url.split('|')[1])  
    choice=[picname,"folder.jpg","default.tbn","%s-fanart.jpg"%picname.split('.')[0],_(30010)]
    newpicname = xbmcgui.Dialog().select(_(30009),choice)
    print newpicname
    if newpicname == 4:
        keyboard = xbmc.Keyboard(picname,_(30009))
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            newpicname=keyboard.getText()
            url=url=preparesaving(dlpath,newpicname)
        del keyboard 
    else:
        url=preparesaving(dlpath,choice[newpicname]) 
    download_picture(url,folder) 

def download_picture(url,folder=""):
    """
    télécharge une image, si pas de paramètre, affichage d'une fenêtre de browse
    """
    print "folder = %s"%folder
    if folder == "":
        folder = xbmcgui.Dialog().browse(0,_(30002),'pictures','',True,)
    if os.path.exists(folder):
        dl_path = url.split('|')[0]
        file = os.path.join(folder,url.split('|')[1])
        urllib.urlretrieve( dl_path, file)
        # downloader sans erreur , on le dit par popup
        xbmcgui.Dialog().ok( _(30005), file )
    else:
        xbmcgui.Dialog().ok( _(30006), _(30007) )


def preparesaving(path,title):
    #concatène l'url à passer en paramètre et ajoute l'extension au nom  
    try:
        ext = title.split('.')[1]
        return path + '|' + title
    except:
        #ext = path[len(SiteUrl):].split('.')[1]
        ext = '.' + path[len(path)-3:]
        return path + '|' + title + ext
        
def show_icones(cat=0):
    """
    Affichage
    """
    ok=True
    dico = fetchgallery(cat)
    indice = 0
    for id in dico['id']:
        IconeImage = dico['thumbnail'][indice]
        if dico['type'][indice] == 'PIC':
            PictureName = dico['title'][indice]       
            url = dico['image'][indice]
           
            #On affiche la liste des icones de la galerie
            item=xbmcgui.ListItem(_unicode(PictureName),iconImage=IconeImage,thumbnailImage=IconeImage)
            
            ##On ajoute les boutons au menu contextuel
            ##Enregistrer..
            c_items = [ ( _(30003), 'XBMC.RunPlugin(%s?download_path=%s)' % ( sys.argv[ 0 ], preparesaving(dico['image'][indice],PictureName)) ) ]
            ###Enregistrer sous...
            c_items += [ ( _(30004), 'XBMC.RunPlugin(%s?download_as=%s)' % ( sys.argv[ 0 ], preparesaving(dico['image'][indice],PictureName)) ) ]

             ##Définir commme fond d'écran
            #c_items += [ ( _(30011), 'XBMC.RunPlugin(%s?skinsettings=%s)' % ( sys.argv[ 0 ], dico['image'][indice]) ) ]


            item.addContextMenuItems( c_items)
            
            ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=False,totalItems=len(dico['id'])) 
        else:
            CatName = dico['title'][indice]
            
            if IconeImage != 'None':
                item=xbmcgui.ListItem(_unicode(CatName),iconImage=IconeImage,thumbnailImage=IconeImage)
            else:
                item=xbmcgui.ListItem(_unicode(CatName))#,'','')
            
            #Définir commme fond d'écran
            c_items = [ ( _(30011), 'XBMC.RunPlugin(%s?set_screensaver=%s)' % ( sys.argv[ 0 ],id) ) ]
            #c_items = [ ( _(30011), 'XBMC.RunPlugin(%s?set_screensaver=%s)' % ( os.path.join(RootDir, 'screensaver.py',id) ) ]
            
            item.addContextMenuItems( c_items)
            
            #listitem.addContextMenuItems('Save...',)
            url=sys.argv[0]+"?cat="+id
            
            ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=True,totalItems=len(dico['id']))     
        indice = indice + 1
    
    return ok

def set_home_background_imgage(url):
    # fonction pour PM3.HD seulement
    if xbmc.getSkinDir().lower() != "pm3.hd":
        # on a pas d'affaire ici return 
        return
 
    list = [ "Video", "Music", "Pictures", "Programs", "Weather", "Scripts", "Settings" ]
    #ici on mets un dialog select pour choisir la section video, picture, etc
    selected = xbmcgui.Dialog().select( "Arrières-plans de l'accueil", list )
 
    # s'il y a une reponse avec le dialog select on continu la fonction
    if selected != -1:
        # si l'options activer le background est pas activer, on l'active
        if xbmc.getCondVisibility( "!Skin.HasSetting(Home_Enable_Custom_Back_%s)" % list[selected] ):
            xbmc.executebuiltin( "Skin.ToggleSetting(Home_Enable_Custom_Back_%s)" % list[selected] )
        builtin = "Skin.SetPath(Home_Custom_Back_%s_Folder,%s)"% ( selected,)
        xbmc.executebuiltin(builtin) 

print "PARAM = %s"%sys.argv[2]

if "cat=" in sys.argv[2]:
    show_icones(sys.argv[2].split('cat=')[1])
    ##paramètre 'cat' : on liste l'image correspondante
    
elif  "download_path=" in sys.argv[2]:
    if xbmcplugin.getSetting( "SAVE" ) == "true":
        download_picture(sys.argv[2].split('download_path=')[1],xbmcplugin.getSetting( "PATH" ))
    else:
        download_picture(sys.argv[2].split('download_path=')[1],xbmcplugin.getSetting(''))

elif "download_as=" in sys.argv[2]:
    if xbmcplugin.getSetting( "SAVE" ) == "true":
        download_as(sys.argv[2].split('download_as=')[1],xbmcplugin.getSetting( "PATH" ))
    else:
        download_as(sys.argv[2].split('download_as=')[1],xbmcplugin.getSetting(''))

elif "skinsettings=" in sys.argv[2]:       
    set_home_background_image(sys.argv[2].split('skinsettings=')[1])

elif "slideshow=" in sys.argv[2]:
    print "ici 1"
    cmd = 'XBMC.RunPlugin(%s?slideshow==%s)' % ( os.path.join(RootDir, 'screensaver.py',id) )
    xbmc.executebuiltin(cmd)
    show_pics(sys.argv[2].split('slideshow=')[1])

elif "set_screensaver=" in sys.argv[2]:
    set_screensaver(sys.argv[2])
        
else:
    #pas de paramètres : début du plugin
    show_icones()
    
xbmcplugin.endOfDirectory(int(sys.argv[1]))

 
 
        
