###########################################
# written with inspiration from:          #
# https://youtu.be/ZFoQleFUH9Y            #
# this is more of a learning script for   #
# wrapping my brain around some basic     #
# web scraping.                           #
# it brute forces its way through an      #
# embedded map to find all the locations  #
# listed on the map, which is a challenge #
# because the map limits the number of    #
# results to the 10 locations that are    #
# closest to the postal code you input    #
###########################################

import requests
import shapely.geometry
import pyproj
import json
#import time
#from random import randint
#import sys
import csv

# used to generate grid of points
GRID_STEPS = 100000
SW_P = (-97.63, 42.92)
NE_P = (-67.76, 53.55)
o_rad = 10000

# what we will bounce some geopoints off
URL = "https://feedontario.ca/wp-admin/admin-ajax.php"

HEADERS = {
  'Connection': 'keep-alive',
  'Accept': '*/*',
  'DNT': '1',
  'X-Requested-With': 'XMLHttpRequest',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'Origin': 'https://feedontario.ca',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://feedontario.ca/need-help/find-a-food-bank/',
  'Accept-Language': 'en-CA,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
  'Cookie': '_ga=GA1.2.1884631263.1613509517; _gid=GA1.2.1026196759.1613509517; _gat_UA-90118119-2=1'
        }

def gen_grid(point_sw=SW_P, point_ne=NE_P, steps=GRID_STEPS):
    '''
    generates a 2d grid given a bounding box of sw and ne tuple points
    and a grid size measured in metres

    adapted from:
    https://stackoverflow.com/questions/40342355/how-can-i-generate-a-regular-geographic-grid-using-python

    thank you internet

    since the sql string that fetches local providers given a set of lat and
    lng, limits it to the closest 10 no matter what the distance parameter
    is, we need to develop a grid of coordinate tuples that will overlay the
    target area and then filter out the unique locations from the redudant
    results

    '''
    
    # Set up projections
    p_ll = pyproj.Proj(init='epsg:4326')
    p_mt = pyproj.Proj(init='epsg:3857') # metric; same as EPSG:900913

    # Create corners of rectangle to be transformed to a grid
    sw = shapely.geometry.Point(point_sw)
    ne = shapely.geometry.Point(point_ne)

    stepsize = steps # grid step size in metres

    # Project corners to target projection
    transformed_sw = pyproj.transform(p_ll, p_mt, sw.x, sw.y) # Transform NW point to 3857
    transformed_ne = pyproj.transform(p_ll, p_mt, ne.x, ne.y) # .. same for SE

    # Iterate over 2D area
    gridpoints = []
    x = transformed_sw[0]
    while x < transformed_ne[0]:
        y = transformed_sw[1]
        while y < transformed_ne[1]:
            p = shapely.geometry.Point(pyproj.transform(p_mt, p_ll, x, y))
            gridpoints.append(p)
            y += stepsize
        x += stepsize
    
    return gridpoints

def get_payload(lng, lat):
    '''
    loads a lat long pair into the payload
    looking at the json response when the payload is POSTed
    it documents a sql string that the wp plugin uses to calculate adjacent 
    providers but has a limit 10 parameter 
    '''
    payload=f"action=csl_ajax_search&address=N2H+1T6&formdata=addressInput%3DN2H%2B1T6&lat={lat}&lng={lng}&options%5Bdistance_unit%5D=km&options%5Bdropdown_style%5D=none&options%5Bignore_radius%5D=0&options%5Bimmediately_show_locations%5D=0&options%5Binitial_radius%5D={o_rad}&options%5Blabel_directions%5D=Directions&options%5Blabel_email%5D=Email&options%5Blabel_fax%5D=Fax&options%5Blabel_phone%5D=Phone&options%5Blabel_website%5D=Website&options%5Bloading_indicator%5D=&options%5Bmap_center%5D=555+Richmond+Street+West%2C+Toronto%2C+Ontario&options%5Bmap_center_lat%5D=43.6463654&options%5Bmap_center_lng%5D=-79.4023122&options%5Bmap_domain%5D=maps.google.ca&options%5Bmap_end_icon%5D=http%3A%2F%2Foafb.ca%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbulb_azure.png&options%5Bmap_home_icon%5D=http%3A%2F%2Foafb.ca%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbox_yellow_home.png&options%5Bmap_region%5D=ca&options%5Bmap_type%5D=roadmap&options%5Bno_autozoom%5D=0&options%5Buse_sensor%5D=false&options%5Bzoom_level%5D=12&options%5Bzoom_tweak%5D=1&radius={o_rad}"
    return payload

def get_response(url, headers, payload):
    
    return requests.request("POST", url, headers=headers, data=payload)

def parse_response(r_json):
    '''
    takes the json formatted data returned from the request
    and extracts the data we want to keep from it
    stacks it into a dictionary keyed off the id number that the
    database uses to keep track of sites
    and returns the dictionary
    '''
    rsp = r_json['response']
    # should contain up to 10 locations from the database
    holding = {}
    for point in rsp:
        #print(f'parsing resp. {point["data"]["sl_id"]}')
        sl_id = point['data']['sl_id']
        holding[sl_id] = point['data']
    return holding

def write_dcsv(d, h, wh=False):
    
    with open('fo_sites.csv', 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=h)
        if wh:
            writer.writeheader()
        writer.writerow(d)

if __name__ == "__main__":
    point_data = []
    write_header = True
    cycle = 0
    # generate a grid of lat, lng pairs
    gpoints = gen_grid()
    print(f'made {len(gpoints)} points')
    # go through the points and probe the api endpoint
    for ps in gpoints:
        pload = get_payload(ps.x, ps.y)
        response = get_response(URL, HEADERS, pload)
        response_text = json.loads(response.text)
        # parse the text and look for programs
        current_d = parse_response(response_text)
        # use set operations to parse out new keys
        key_set = set(current_d.keys())
        #print(key_set)
        new_keys = key_set.difference(set(point_data))
        # add new keys to the point_data dictionary
        if len(new_keys) > 0: 
            heading = list(current_d[list(current_d.keys())[0]].keys())
            for nk in new_keys:
                print(nk)
                point_data.append(nk)
                write_dcsv(current_d[nk], heading, write_header)
                write_header = False
        #else:
            #print(f'no new keys for points {ps.x}, {ps.y}\nJust {len(key_set)}')
        # have a nap
        #r_nap = randint(1,4)
        #print(f'sleeping for {r_nap}')
        cycle += 1 
        #time.sleep(r_nap)
    
    print(f'scrape op complete.\n{len(point_data)} locations identified.\nOver {cycle} iterations')



