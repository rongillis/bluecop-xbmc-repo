import xbmc
import xbmcplugin
import xbmcgui

import common
import os
import sys
import urllib
import urllib2
import math
import time

from BeautifulSoup import BeautifulStoneSoup

pluginhandle = int(sys.argv[1])

class Main:
    def __init__( self ):
        try:
            perpage = common.args.perpage
        except:
            if 'Popular' in common.args.name or 'Featured' in common.args.name or 'Recently' in common.args.name:
                perpage = common.settings['popperpage']
            else:
                perpage = common.settings['perpage']
        xbmcplugin.setPluginCategory( pluginhandle, category=common.args.name )
        #xbmcplugin.setPluginFanart(pluginhandle, common.args.fanart)
        self.addMenuItems(perpage,common.args.page)
        if common.args.updatelisting == 'true':
            xbmcplugin.endOfDirectory( pluginhandle, cacheToDisc=True, updateListing=True)
        else:
            xbmcplugin.endOfDirectory( pluginhandle, cacheToDisc=True)

    def getTotalCount( self, itemsurl ):
        if '?' in itemsurl:
            itemsurl += '&dp_id=huludesktop&package_id=2&total=1'
        else:
            itemsurl += '?dp_id=huludesktop&package_id=2&total=1'
        html=common.getFEED(itemsurl)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        items = menuitems=tree.findAll('items')
        for counts in items:
            try:
                return int(counts.find('total_count').string)
            except:
                return 0

      
    def addMenuItems( self, perpage, pagenumber ,url=common.args.url ):
        # Get item count for page
        total_count = self.getTotalCount( url )
        # Add Next/Prev Pages
        if int(perpage) < int(total_count):
            if 'Popular' in common.args.name or 'Featured' in common.args.name or 'Recently' in common.args.name:
                popular='true'
            else:
                try:
                    popular = common.args.popular
                except:
                    popular='false'
            current_page = int(pagenumber)
            next_page = int(pagenumber)+1
            prev_page = int(pagenumber)-1         
            npage_begin = int(perpage)*current_page + 1
            npage_end = int(perpage)*next_page
            if total_count < npage_end:
                npage_end = total_count
            if npage_begin < total_count:
                next_name = 'Next Page ('+str(npage_begin)+'-'+str(npage_end)+' of '+str(total_count)+')'
                nextthumb=xbmc.translatePath(os.path.join(common.imagepath,"next.png"))
                common.addDirectory(next_name,url,common.args.mode,page=str(next_page),icon=nextthumb,perpage=perpage,popular=popular,updatelisting='true')
            if prev_page > 0:
                ppage_begin = int(perpage)*(prev_page-1)+1
                ppage_end = int(perpage)*prev_page
                prev_name = 'Previous Page ('+str(ppage_begin)+'-'+str(ppage_end)+' of '+str(total_count)+')'
                prevthumb=xbmc.translatePath(os.path.join(common.imagepath,"prev.png"))
                common.addDirectory(prev_name,url,common.args.mode,page=str(prev_page),icon=prevthumb,perpage=perpage,popular=popular,updatelisting='true')

        # Grab xml item list
        if '?' in url:
            url += '&dp_id=huludesktop&package_id=2&limit='+perpage+'&page='+pagenumber
        else:
            url += '?dp_id=huludesktop&package_id=2&limit='+perpage+'&page='+pagenumber
        html=common.getFEED(url)
        while html == False:
            html=common.getFEED(url)
            time.sleep(2)
        tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        # Find all items in xml
        menuitems=tree.findAll('item')
        del tree
        for item in menuitems:
            
            display=item('display')[0].string.encode('utf-8')
            url='http://m.hulu.com'+item('items_url')[0].string
            mode=item('app_data')[0]('cmtype')[0].string
            
            #Flatten All and Alphabetical
            if display == 'All' and total_count == 1:
                print url
                #common.args.mode = 'All'
                self.addMenuItems(common.settings['allperpage'],common.args.page,url)
                return
            
            displayname = display
            # Skip unwanted menu items
            if mode == 'None' or display == 'Add to queue' or display == 'Subscriptions' or display == 'Recommended':
                continue
            #try:
            #    if 'True' == item.find('is_plus_web_only').string:
            #        isPlus = True
            #        if (common.settings['enable_plus'] == 'false'):
            #            continue
            #except:
            #    isPlus = False
            
            #set Data
            isVideo = False
            art = xbmc.translatePath(os.path.join(common.imagepath,"icon.png"))
            fanart = 'http://assets.huluim.com/companies/key_art_hulu.jpg'
            description = ''
            show_name = ''
            company_name = ''
            duration = ''
            genre = ''
            season_number = 0
            episode_number = 0
            premiered = ''
            year = 0
            rating = 0.0
            votes = ''
            mpaa = ''
            media_type = False
                
            data = item('data')
            if data:
                data = data[0]
                canonical_name      = data('canonical_name')
                show_canonical_name = data('show_canonical_name')
                #Show Only
                if canonical_name:
                    canonical_name = canonical_name[0].string
                    show_name = data('name')[0].string.encode('utf-8')
                    genre_data = data('genre')
                    if genre_data:
                        genre = genre_data[0].string
                    art = "http://assets.hulu.com/shows/key_art_"+canonical_name.replace('-','_')+".jpg"
                #Video Only
                elif show_canonical_name:
                    isVideo = True
                    content_id = data('content_id')[0].string
                    videoid = data('video_id')[0].string
                    canonical_name = show_canonical_name[0].string
                    media_type = data('media_type')[0].string
                    art = data('thumbnail_url_16x9_large')[0].string
                    show_name = data('show_name')[0].string.encode('utf-8')
                    mpaa = data('content_rating')[0].string
                    votes = data('votes_count')[0].string
                    premiered_data = data('original_premiere_date')
                    if premiered_data[0].string:
                        premiered = premiered_data[0].string.replace(' 00:00:00','')
                        year = int(premiered.split('-')[0])
                    season_number_data = data('season_number')
                    if season_number_data[0].string:
                        season_number = int(season_number_data[0].string)
                    episode_number_data = data('episode_number')
                    if episode_number_data[0].string:
                        episode_number = int(episode_number_data[0].string)
                    duration_data = data('duration')
                    if duration_data[0].string:
                        duration = float(duration_data[0].string)
                        hour = int(math.floor(duration / 60 / 60))
                        minute = int(math.floor((duration - (60*60*hour))/ 60))
                        second = int(duration - (60*minute)- (60*60*hour))
                        if hour == 0:
                            duration = str(minute)+':'+str(second)
                        else:
                            duration = str(hour)+':'+str(minute)+':'+str(second)
                #Both Show and Video
                description_data = data('description')
                if description_data:
                    if description_data[0].string:
                        description = unicode(common.cleanNames(description_data[0].string.replace('\n', ' ').replace('\r', ' '))).encode('utf-8')
                rating_data = data('rating')
                if rating_data:
                    if rating_data[0].string:
                        rating = float(rating_data[0].string)*2
                company_name_data = data('company_name')
                if company_name_data:
                    company_name = company_name_data[0].string
                ishd_data = data('has_hd')
                if ishd_data:
                    ishd = ishd_data[0].string
                fanart = "http://assets.hulu.com/shows/key_art_"+canonical_name.replace('-','_')+".jpg"

            #Set displayname and content type    
            if mode == 'SeasonMenu':
                xbmcplugin.setContent(pluginhandle, 'seasons')
                dtotal_count = self.getTotalCount( url )
                #displayname = displayname + ' ('+str(dtotal_count)+')'
                episode_number = dtotal_count
                isVideo = False
            elif mode == 'ShowPage':
                xbmcplugin.setContent(pluginhandle, 'tvshows')
                isVideo = False
            elif common.args.mode == 'ShowPage':
                xbmcplugin.setContent(pluginhandle, 'seasons')
                dtotal_count = self.getTotalCount( url )
                episode_number = dtotal_count
                displayname = displayname + ' ('+str(dtotal_count)+')'
                if dtotal_count == 0:
                    continue
            #Set Networks and Studios fanart
            elif common.args.name == 'Networks' or common.args.name == 'Studios':
                fanart = "http://assets.huluim.com/companies/key_art_"+canonical_name.replace('-','_')+".jpg"
                art = fanart
            #Add Count to Display Name for Non-Show/Episode Lists
            elif common.args.mode == 'Menu' and isVideo == False:
                dtotal_count = self.getTotalCount( url )
                if dtotal_count <> 1:
                    displayname = displayname + ' ('+str(dtotal_count)+')'
                elif dtotal_count == 0:
                    continue
            #Set Final Video Name
            elif isVideo == True:
                url=content_id
                #URL of video
                #url="http://www.hulu.com/watch/"+videoid
                mode = 'TV_play'
                if media_type == 'TV':
                    xbmcplugin.setContent(pluginhandle, 'episodes')
                elif media_type == 'Film':
                    xbmcplugin.setContent(pluginhandle, 'movies')
                    show_name = company_name
                #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_EPISODE)
                if season_number <> 0 and episode_number <> 0:
                    if 'Popular' in common.args.name or 'Featured' in common.args.name or 'Recently' in common.args.name or common.args.popular == 'true':
                        #displayname = unicode(show_name+' - '+str(season_number)+'x'+str(episode_number)+' - '+display).encode('utf-8')
                        displayname = show_name+' - '+str(season_number)+'x'+str(episode_number)+' - '+display
                    else:
                        #displayname = unicode(str(season_number)+'x'+str(episode_number)+' - '+display).encode('utf-8')
                        displayname = str(season_number)+'x'+str(episode_number)+' - '+display
                    if 'True' == ishd:
                        displayname += ' (HD)'
      
            u = sys.argv[0]
            u += '?url="'+urllib.quote_plus(url)+'"'
            u += '&mode="'+urllib.quote_plus(mode)+'"'
            item=xbmcgui.ListItem(displayname, iconImage=art, thumbnailImage=art)
            item.setInfo( type="Video", infoLabels={ "Title":display,
                                                     "Plot":description,
                                                     "Genre":genre,
                                                     "Season":season_number,
                                                     "Episode":episode_number,
                                                     "Duration":duration,
                                                     "premiered":premiered,
                                                     "TVShowTitle":show_name,
                                                     "Studio":company_name,
                                                     "Year":year,
                                                     "MPAA":mpaa,
                                                     "Rating":rating,
                                                     "Votes":votes
                                                     })
            item.setProperty('fanart_image',fanart)

            #Set total count
            if int(perpage) < int(total_count):
                total_items = int(perpage)
            elif int(perpage) < len(menuitems):
                total_items = len(menuitems)
            else:
                total_items = int(total_count)

            if isVideo == False:
                u += '&name="'+urllib.quote_plus(display.replace("'",""))+'"'
                u += '&art="'+urllib.quote_plus(art)+'"'
                u += '&fanart="'+urllib.quote_plus(fanart)+'"'
                u += '&page="1"'
                u += '&popular="false"'
                u += '&updatelisting="false"'
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=True,totalItems=total_items)
            elif isVideo == True:
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=False,totalItems=total_items)

