
import fivehundredpxutils
import fivehundredpxutils.xbmc

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

__addon__       = xbmcaddon.Addon()
__addonname__   = __addon__.getAddonInfo('name')

from fivehundredpx.client import FiveHundredPXAPI

_CONSUMER_KEY = 'LvUFQHMQgSlaWe3aRQot6Ct5ZC2pdTMyTLS0GMfF'
_RPP = int(xbmcplugin.getSetting(fivehundredpxutils.xbmc.addon_handle, 'rpp'))
API = FiveHundredPXAPI()


class Image(object):
    def __init__(self, photo_json):
        self.name = photo_json['name']
        self.thumb_url = photo_json['images'][0]['url']
        self.url = photo_json['images'][1]['url']
        self.userid = photo_json['user']['username']
        self.userfullname = photo_json['user']['fullname']

    def __repr__(self):
        return str(self.__dict__)


def feature():
    params = fivehundredpxutils.xbmc.addon_params
    feature = params['feature']
    category = params.get('category', None)
    page = int(params.get('page', 1))

    resp = API.photos(feature=feature, only=category, rpp=_RPP, consumer_key=_CONSUMER_KEY, image_size=[2, 4], page=page)

    for image in map(Image, resp['photos']):
        fivehundredpxutils.xbmc.add_image(image)

    if resp['current_page'] != resp['total_pages']:
        next_page = page + 1
        url = fivehundredpxutils.xbmc.encode_child_url('feature', feature=feature, category=category, page=next_page)
        fivehundredpxutils.xbmc.add_dir('Next page', url)

    fivehundredpxutils.xbmc.end_of_directory()


def search():
    def getTerm():
        kb = xbmc.Keyboard(heading='Search 500px')
        kb.doModal()
        text = kb.getText()
        return text if kb.isConfirmed() and text else None

    params = fivehundredpxutils.xbmc.addon_params

    if 'term' not in params:
        term = getTerm()
        if term == None:
            return
        page = 1
    else:
        term = params['term']
        page = int(params.get('page', 1))

    resp = API.photos_search(term=term, rpp=_RPP, consumer_key=_CONSUMER_KEY, image_size=[2, 4], page=page)
    
    if (resp['total_items'] == 0):
        xbmc.executebuiltin('Notification(%s, %s)' % (__addonname__, "Your search returned no matches."))
        return
    
    for image in map(Image, resp['photos']):
        fivehundredpxutils.xbmc.add_image(image)

    if resp['current_page'] != resp['total_pages']:
        next_page = page + 1
        if 'ctxsearch' in params:
            url = fivehundredpxutils.xbmc.encode_child_url('search', term=term, page=next_page, ctxsearch=True)
        else:
            url = fivehundredpxutils.xbmc.encode_child_url('search', term=term, page=next_page)
        fivehundredpxutils.xbmc.add_dir('Next page', url)

    fivehundredpxutils.xbmc.end_of_directory()


def features():
    features = (
        "editors",
        "popular",
        "upcoming",
        "fresh_today",
        "fresh_yesterday",
        "fresh_week"
    )

    for feature in features:
        url = fivehundredpxutils.xbmc.encode_child_url('categories', feature=feature)
        fivehundredpxutils.xbmc.add_dir(feature, url)

    url = fivehundredpxutils.xbmc.encode_child_url('search')
    fivehundredpxutils.xbmc.add_dir('Search', url)

    fivehundredpxutils.xbmc.end_of_directory()


def categories():
    categories = {
        'Uncategorized': 0,
        'Abstract': 10,
        'Animals': 11,
        'Black and White': 5,
        'Celebrities': 1,
        'City and Architecture': 9,
        'Commercial': 15,
        'Concert': 16,
        'Family': 20,
        'Fashion': 14,
        'Film': 2,
        'Fine Art': 24,
        'Food': 23,
        'Journalism': 3,
        'Landscapes': 8,
        'Macro': 12,
        'Nature': 18,
        'Nude': 4,
        'People': 7,
        'Performing Arts': 19,
        'Sport': 17,
        'Still Life': 6,
        'Street': 21,
        'Transportation': 26,
        'Travel': 13,
        'Underwater': 22,
        'Urban Exploration': 27,
        'Wedding': 25,
    }

    params = fivehundredpxutils.xbmc.addon_params
    feature = params['feature']

    url = fivehundredpxutils.xbmc.encode_child_url('feature', feature=feature)
    fivehundredpxutils.xbmc.add_dir('All', url)

    for category in sorted(categories):
        url = fivehundredpxutils.xbmc.encode_child_url('feature', feature=feature, category=category)
        fivehundredpxutils.xbmc.add_dir(category, url)

    fivehundredpxutils.xbmc.end_of_directory()


try:
    modes = {
        'feature': feature,
        'categories': categories,
        'search': search,
    }

    params = fivehundredpxutils.xbmc.addon_params
    mode_name = params['mode']
    modes[mode_name]()
except KeyError:
    features()
