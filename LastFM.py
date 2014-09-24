import xbmcaddon
import os
import xbmc
import sys
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson
from Utils import *
import urllib

lastfm_apikey = '6c14e451cd2d480d503374ff8c8f4e2b'
googlemaps_key_old = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
Addon_Data_Path = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % xbmcaddon.Addon().getAddonInfo('id')).decode("utf-8"))
base_url = 'http://ws.audioscrobbler.com/2.0/?api_key=%s&format=json&' % (lastfm_apikey)


def HandleLastFMEventResult(results):
    events = []
    if results is None:
        return []
    if "events" in results:
        if "@attr" in results["events"]:
            if int(results["events"]["@attr"]["total"]) == 1:
                results['events']['event'] = [results['events']['event']]
            for event in results['events']['event']:
                artists = event['artists']['artist']
                if isinstance(artists, list):
                    my_arts = ' / '.join(artists)
                else:
                    my_arts = artists
                lat = ""
                lon = ""
                try:
                    if event['venue']['location']['geo:point']['geo:long']:
                        lon = event['venue']['location']['geo:point']['geo:long']
                        lat = event['venue']['location']['geo:point']['geo:lat']
                        search_string = lat + "," + lon
                    elif event['venue']['location']['street']:
                        search_string = urllib.quote_plus(event['venue']['location']['city'] + " " + event['venue']['location']['street'])
                    elif event['venue']['location']['city']:
                        search_string = urllib.quote_plus(event['venue']['location']['city'] + " " + event['venue']['name'])
                    else:
                        search_string = urllib.quote_plus(event['venue']['name'])
                except:
                    search_string = ""
                googlemap = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&maptype=roadmap&center=%s&zoom=13&markers=%s&size=640x640&key=%s' % (search_string, search_string, googlemaps_key_old)
                event = {'date': event['startDate'][:-3],
                         'name': event['venue']['name'],
                         'id': event['venue']['id'],
                         'venue_id': event['venue']['id'],
                         'street': event['venue']['location']['street'],
                         'eventname': event['title'],
                         'website': event['website'],
                         'description': cleanText(event['description']),
                         'postalcode': event['venue']['location']['postalcode'],
                         'city': event['venue']['location']['city'],
                         'country': event['venue']['location']['country'],
                         'geolat': event['venue']['location']['geo:point']['geo:lat'],
                         'geolong': event['venue']['location']['geo:point']['geo:long'],
                         'lat': event['venue']['location']['geo:point']['geo:lat'],
                         'lon': event['venue']['location']['geo:point']['geo:long'],
                         'artists': my_arts,
                         'googlemap': googlemap,
                         'artist_image': event['image'][-1]['#text'],
                         'thumb': event['image'][-1]['#text'],
                         'venue_image': event['venue']['image'][-1]['#text'],
                         'headliner': event['artists']['headliner']}
                events.append(event)
    elif "error" in results:
        Notify("Error", results["message"])
    else:
        log("Error in HandleLastFMEventResult. JSON query follows:")
     #   prettyprint(results)
    return events


def HandleLastFMAlbumResult(results):
    albums = []
    log("starting HandleLastFMAlbumResult")
    if results is None:
        return []
    if 'topalbums' in results:
        for album in results['topalbums']['album']:
            album = {'artist': album['artist']['name'],
                     'mbid': album['mbid'],
                     'thumb': album['image'][-1]['#text'],
                     'name': album['name']}
            albums.append(album)
    else:
        log("No Info in JSON answer:")
        prettyprint(results)
    return albums


def HandleLastFMShoutResult(results):
    shouts = []
    log("starting HandleLastFMShoutResult")
    if results is None:
        return []
    for shout in results['shouts']['shout']:
        newshout = {'comment': shout['body'],
                    'author': shout['author'],
                    'date': shout['date'][4:]}
        shouts.append(newshout)
    return shouts


def HandleLastFMTrackResult(results):
    log("starting HandleLastFMTrackResult")
   # prettyprint(results)
    if results is None:
        return []
    if "wiki" in results['track']:
        summary = cleanText(results['track']['wiki']['summary'])
    else:
        summary = ""
    TrackInfo = {'playcount': str(results['track']['playcount']),
                 'Thumb': str(results['track']['playcount']),
                 'summary': summary}
    return TrackInfo


def HandleLastFMArtistResult(results):
    if results is None:
        return []
    artists = []
    log("starting HandleLastFMArtistResult")
    for artist in results['artist']:
        if 'name' in artist:
            listeners = int(artist.get('listeners', 0))
            artist = {'Title': artist['name'],
                      'name': artist['name'],
                      'mbid': artist['mbid'],
                      'Thumb': artist['image'][-1]['#text'],
                      'Listeners': format(listeners, ",d")}
            artists.append(artist)
    return artists


def GetEvents(id, pastevents=False):
    if pastevents:
        url = 'method=artist.getpastevents&mbid=%s' % (id)
    else:
        url = 'method=artist.getevents&mbid=%s' % (id)
    results = Get_JSON_response(base_url, url, 1)
    return HandleLastFMEventResult(results)


def GetTopArtists():
    results = Get_JSON_response(base_url, "method=chart.getTopArtists&limit=100")
    return HandleLastFMArtistResult(results['artists'])


def GetAlbumShouts(artistname, albumtitle):
    url = 'method=album.GetAlbumShouts&artist=%s&album=%s' % (urllib.quote_plus(artistname), urllib.quote_plus(albumtitle))
    results = Get_JSON_response(base_url, url)
    return HandleLastFMShoutResult(results)


def GetArtistShouts(artistname):
    url = 'method=artist.GetShouts&artist=%s' % (urllib.quote_plus(artistname))
    results = Get_JSON_response(base_url, url)
    return HandleLastFMShoutResult(results)


def GetImages(mbid):
    url = 'method=artist.getimages&mbid=%s' % (id)
    results = Get_JSON_response(base_url, url, 0)
    prettyprint(results)
    return HandleLastFMEventResult(results)


def GetTrackShouts(artistname, tracktitle):
    url = 'method=album.GetAlbumShouts&artist=%s&track=%s' % (urllib.quote_plus(artistname), urllib.quote_plus(tracktitle))
    results = Get_JSON_response(base_url, url)
    return HandleLastFMShoutResult(results)


def GetEventShouts(eventid):
    url = 'method=event.GetShouts&event=%s' % (eventid)
    results = Get_JSON_response(base_url, url)
    return HandleLastFMShoutResult(results)


def GetArtistTopAlbums(mbid):
    url = 'method=artist.gettopalbums&mbid=%s' % (mbid)
    results = Get_JSON_response(base_url, url)
    return HandleLastFMAlbumResult(results)


def GetSimilarById(m_id):
    url = 'method=artist.getsimilar&mbid=%s&limit=400' % (m_id)
    results = Get_JSON_response(base_url, url)
    if results is not None and "similarartists" in results:
        return HandleLastFMArtistResult(results['similarartists'])


def GetNearEvents(tag=False, festivalsonly=False, lat="", lon=""):
    if festivalsonly:
        festivalsonly = "1"
    else:
        festivalsonly = "0"
    url = 'method=geo.getevents&festivalsonly=%s&limit=40' % (festivalsonly)
    if tag:
        url = url + '&tag=%s' % (urllib.quote_plus(tag))
    if lat:
        url = url + '&lat=%s&long=%s' % (lat, lon)  # &distance=60
    results = Get_JSON_response(base_url, url, 0.5)
    return HandleLastFMEventResult(results)


def GetVenueEvents(id=""):
    url = 'method=venue.getevents&venue=%s' % (id)
    results = Get_JSON_response(base_url, url, 0.5)
    return HandleLastFMEventResult(results)


def GetTrackInfo(artist="", track=""):
    url = 'method=track.getInfo&artist=%s&track=%s' % (urllib.quote_plus(artist), urllib.quote_plus(track))
    results = Get_JSON_response(base_url, url)
    return HandleLastFMTrackResult(results)

