import logging
import os
import re
import urllib

from steam import WebAPI

import common

log = logging.getLogger(__name__)

_api = WebAPI( key=common.STEAM['key'] )
_mod_url = "https://steamcommunity.com/sharedfiles/filedetails/?id={}"


_params = {
    # the parts that we're interested in
    "search_text": "", # required
    "requiredtags": [], # required
    "numperpage": 1, # optional

    # static 'settings'
    "query_type": 3, # required, this corresponds to the 'relevance' search mode.
    "return_tags": True, # required, we want to get tags back so we can show the Alpha number.
    "appid": 294100, # required
    "creator_appid": 294100, # required
    "match_all_tags": True, # optional
    "cache_max_age_seconds": 120, # optional

    # stuff we don't use, but the API requires
    "page": 1, # required
    "child_publishedfileid": "", # required
    "days": 7, # required
    "excludedtags": "", # required
    "filetype": "0", # required
    "ids_only": False, # required
    "include_recent_votes_only": False, # required
    "omitted_flags": "", # required
    "required_flags": "", # required
    "required_kv_tags": "{}", # required
    "return_children": False, # required
    "return_for_sale_data": False, # required
    "return_kv_tags": False, # required
    "return_metadata": True, # optional
    "return_playtime_stats": False, # required
    "return_previews": False, # required
    "return_short_description": False, # required
    "return_vote_data": False, # required
    "totalonly": False, # required
}

_tag_regex = re.compile( r"\d\.(\d{2})" )
def _tagsToAlpha( tags ):
    for tag in tags:
        match = _tag_regex.match( tag['tag'] )
        log.debug( "tag regex: %s, %s", tag['tag'], match )
        if match:
            return "A" + match.group(1)    

_alpha_regex = re.compile( r"(\d{2})" )
def alphaToTag( alphastring ):
    match = _alpha_regex.search( str( alphastring ) )
    log.debug( "alpha regex: %s, %s", str( alphastring ), match )
    if match:
        return "0." + match.group(0)

def _findAuthor( mod, authors):
    for author in authors:
        if author['steamid'] == mod['creator']:
            return author 
    log.error( "no author found for mod %s", mod['title'].encode("ascii", "replace"))

def search( query, count = 1, tags = [] ):
    # allow calling with a ModRequest, as well as directly
    try:
        _params['search_text'] = query.query
        _params['numperpage'] = query.count
        _params['requiredtags'] = query.tags
    except AttributeError: 
        _params['search_text'] = query
        _params['numperpage'] = count
        _params['requiredtags'] = tags

    # raw response
    log.debug( "search for %s files matching '%s' with tags [%s]", _params['search_text'], _params['numperpage'], ", ".join(_params['requiredtags']))
    raw_mods = _api.IPublishedFileService.QueryFiles(**_params)

    # get list of mods
    try:
        mods = raw_mods['response']['publishedfiledetails']
        log.info( "found %s results for %s files matching '%s' with tags [%s]", len(mods), _params['numperpage'], _params['search_text'], ", ".join(_params['requiredtags']))
    except:
        log.info( "found NO RESULTS for %s files matching '%s' with tags [%s]", _params['numperpage'], _params['search_text'], ", ".join(_params['requiredtags']))      
        return []
    
    # get list of authors
    authorIds = ",".join([ mod['creator'] for mod in mods ])
    raw_authors = _api.ISteamUser.GetPlayerSummaries( steamids = authorIds )
    authors = raw_authors['response']['players']

    # generate a list of Mod objects
    return [ Mod( mod, _findAuthor( mod, authors ) ) for mod in mods ]

class Mod:
    def __init__( self, mod, author ):
        self.title = mod['title'].encode("utf-8", "replace")
        self.url = _mod_url.format( mod['publishedfileid'] ).encode("utf-8", "replace")
        self.authorName = author['personaname'].encode("utf-8", "replace")
        self.authorUrl = author['profileurl'].encode("utf-8", "replace")
        self.alpha = _tagsToAlpha( mod['tags'] )
                
    def __repr__( self ):
        return "[{}] {} by {}".format( self.alpha, self.title, self.authorName ) 
    
    def __len__( self ):
        return 1


class ModRequest:
    '''
    Simple wrapper for search term + count
    '''
    def __init__( self, mod, query, count = 1, tags = [] ):
        if isinstance( count, basestring ):
            count = int( count )
        if count > common.MAX_RESULTS:
            count = common.MAX_RESULTS
        self.mod = mod
        self.query = query
        self.count = count
        self.tags = list( tags )
        if self.mod:
            self.tags.append( "Mod" )
        else: 
            self.tags.append( "Scenario" )

    def getUrl( self ):
        params = dict( common.STEAM_WORKSHOP_PARAMS )
        params['requiredtags[]'] = self.tags
        params['searchtext'] = self.query
        return common.STEAM_WORKSHOP_URL.format( params = urllib.urlencode( params, True ) )

    @classmethod
    def fromQuery( cls, request ):
        mod = True
        count = 1

        if isinstance( request, basestring ):
            return [ cls( True, request ) ]

        if not isinstance( request, tuple ):
            log.error( "bad request: %s", request )
            return []

        # e.g. link{0: mod|scenario}: {2: query string}
        if len(request) == 2:
            mod = request[0] == "mod"
            return [ cls( mod, request[1] ) ]

        # e.g. link{0: count}{1: mod|scenario}s: {2: query string}
        if len(request) == 3:
            count = request[0] if request[0] else 1
            mod = request[1] == "mod"
            parts = re.split( r',', request[2] )
            return [ cls( mod, part.strip(), count ) for part in parts if part.strip() ]

    def __repr__( self ):
        return "Request for {} {}s matching {}".format( self.count, "mod" if self.mod else "scenario", self.query )

if __name__ == '__main__':
    print search( "FluffierThanThou", 10 )
