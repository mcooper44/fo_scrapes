import requests
from bs4 import BeautifulSoup

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


def get_data(url=MAIN_STR):
    result = requests.get(url)
    if result.status_code != 200:
        print('no result')
        return None
    else:
        return result

def get_listings(result):
    cards = [f'listing-card-list-item-{n}' for n in range(0,40)]
    soup = BeautifulSoup(result.text, 'html.parser')
    listings = soup.find_all('li', attrs={'data-testid': cards})
    listing_lu = {n: listings[n].find_all('p', attrs={'data-testid': ['listing-price', 
                                                                      'listing-location', 
                                                                      'listing-proximity', 
                                                                      'listing-description', 
                                                                      'listing-link']}) for n in range(0, len(listings))}
    link_lu = {n: listings[n].find_all('a', attrs={'data-testid': ['listing-description', 
                                                                   'listing-link']}) for n in range(0, len(listings))}
    # link_lu[0][0]['href']
    return listing_lu, link_lu



link = 'https://www.kijiji.ca/v-apartments-condos/kitchener-waterloo/fantastic-2-bedroom-2-bathroom-for-rent-in-kitchener/1676802832'
'''
h = soup.find_all('h4')
for _ in h:
    print(_.find_all(string=True)[0])

# hard to filter out the ul-li becuase ul are used in more than one place

d = soup.find_all('dl')
for _ in d:
    print(_.find_all(string=True)[0])
'''
#this maps the dt to dl

def get_l_details_dl(url=link):
    '''
    https://stackoverflow.com/questions/32475700/using-beautifulsoup-to-extract-specific-dl-and-dd-list-elements
    VALIDATED
    '''
    response = get_data(url)
    data = BeautifulSoup(response.text, 'html.parser')
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

def get_l_details_h4(url=link):
    response = get_data(url)
    data = BeautifulSoup(response.text, 'html.parser')
    h = None
    if data:
        h = data.select('h4') # headings
    else:
        print('no headings')
        return None
    for h4 in h: # print the Heading
        print(h4.text)
        ul = h4.parent.select('ul') # check the parent
        if len(ul) > 0: 
            # Utilities uses SVG's in a UL
            svg = ul[0].select('svg', attrs={'aria-label': True})
            if svg: # we have labels
                for tag in svg:
                    print('-', tag['aria-label'])
            # if li are present - iterate through them
            li = ul[0].select('li')
            if li and not svg:
                for l in li:
                    if len(l) > 0:
                        print('-', l.text)
            else:
                # just one element ul
                print('-', ul[0].text)







