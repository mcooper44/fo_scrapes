import requests
from bs4 import BeautifulSoup
import re

# url is build from..
# base + type + geo
# other components are used to narrow scope
BASE = 'https://www.kijiji.ca/'
# pick one type
TYPE_r = 'b-for-rent/' # base
TYPE_c = 'b-apartments-condos/' # long term rent
# pick one city
GEO = 'kitchener-waterloo/'
# pick target
ONE_BED_BASE = 'one-bedroom-basement/'

# limits results to 23km radius from region centre
SCOPE = 'c30349001l1700212?sort=dateDesc&radius=23.0&address=Kitchener%2C+Waterloo+Regional+Municipality%2C+ON&ll=43.4516395%2C-80.4925337'

MAIN_STR = BASE + TYPE_r + GEO + SCOPE

AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0'

HEADER = {'User-Agent': AGENT}

link = 'https://www.kijiji.ca/v-apartments-condos/kitchener-waterloo/fantastic-2-bedroom-2-bathroom-for-rent-in-kitchener/1676802832'


def get_page(url=MAIN_STR):
    '''
    make a request to get the result
    using the requests library
    '''

    result = requests.get(url)
    if result.status_code != 200:
        print('no result')
        return None
    else:
        return result


def parse_result(request):
    '''
    take the result created by the requests library
    and parse it using Beautiful Soup, returning 
    the soup object
    '''
    return BeautifulSoup(request.text, 'html.parser')


def test_listing():
    '''
    grab a listing and test the functions
    to parse the page and pull out the key
    features we are looking for
    '''
    page = get_page(link)
    data = parse_result(page)
    dl_features = get_l_details_dl(data)
    h4_features = get_l_details_h4(data)
    t_features = get_l_title_details(data)
    return dl_features, h4_features, t_features


def get_listings(data):
    '''
    parses the listing page of 40 results
    '''
    cards = [f'listing-card-list-item-{n}' for n in range(0,40)]
    listings = data.find_all('li', attrs={'data-testid': cards})
    listing_lu = {n: listings[n].find_all('p', attrs={'data-testid': ['listing-price', 
                                                                      'listing-location', 
                                                                      'listing-proximity', 
                                                                      'listing-description', 
                                                                      'listing-link']}) for n in range(0, len(listings))}
    link_lu = {n: listings[n].find_all('a', attrs={'data-testid': ['listing-description', 
                                                                   'listing-link']}) for n in range(0, len(listings))}
    # link_lu[0][0]['href']
    return listing_lu, link_lu


def get_l_details_dl(data):
    '''
    https://stackoverflow.com/questions/32475700/using-beautifulsoup-to-extract-specific-dl-and-dd-list-elements
    VALIDATED
    '''
    d = None
    if data:
        d = data.find_all('dl')
    k, v = [], []
    for dl in d:
        for dt in dl.find_all('dt'):
            k.append(dt.text.strip())
        for dd in dl.find_all('dd'):
            v.append(dd.text.strip())
    return dict(zip(k,v))


def get_l_details_h4(data):
    '''
    Extract the listing features from the
    individual listing
    '''
    h = None
    _struct = {}
    if data:
        h = data.select('h4') # headings
    else:
        print('no headings')
        return None
    for h4 in h: # print the Heading
        #print(h4.text)
        heading = h4.text
        _struct[heading] = []
        ul = h4.parent.select('ul') # check the parent
        if len(ul) > 0: 
            # Utilities uses SVG's in a UL
            svg = ul[0].select('svg', attrs={'aria-label': True})
            if svg: # we have labels
                for tag in svg:
                    _struct[heading].append(tag['aria-label'])
                    #print('-', tag['aria-label'])
            # if li are present - iterate through them
            li = ul[0].select('li')
            if li and not svg:
                for l in li:
                    if len(l) > 0:
                        _struct[heading].append(l.text)
                        #print('-', l.text)
            else:
                # just one element ul
                _struct[heading].append(ul[0].text)
                #print('-', ul[0].text)
    return _struct


def get_l_title_details(data):
    '''
    Extract the title, price, price note and address 
    from the individual listing page
    '''
    details = ['price', 'util_headline',
               'title_str', 'addresss']
    detail_str = []
    r_price = re.compile('priceWrapper')
    r_add = re.compile('locationContainer')
    price = data.find_all('div', {'class': r_price})
    if price:
        for s in price[0]:
            detail_str.append(s.text)
    # add title string
    detail_str.append(price[0].parent.select('h1')[0].text)
    # find address
    address = data.find_all('div', {'class': r_add})
    detail_str.append(address[1].select('span')[0].text)
    # add address
    #detail_str.append(address[0].text)
    # zip labels and values into a dictionary
    return dict(zip(details, detail_str))




