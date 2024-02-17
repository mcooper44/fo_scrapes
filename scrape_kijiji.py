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
    cards = cards = [f'listing-card-list-item-{n}' for n in range(0,40)]
    soup = BeautifulSoup(result, 'html.parser')
    listings = soup.find_all('li', attrs={'data-testid': cards})
    listing_lu = {n: listings[n].find_all('p', attrs={'data-testid': ['listing-price', 
                                                                      'listing-location', 
                                                                      'listing-proximity', 
                                                                      'listing-description', 
                                                                      'listing-link']}) for n in range(0, len(listings))}
    link_lu = {n: listings[n].find_all('a', attrs={'data-testid': ['listing-description', 
                                                                   'listing-link']}) for n in range(0, len(listings))}
    # link_lu[0][0]['href']















