from bs4 import BeautifulSoup
import requests
from time import sleep
import csv
import time

TARGETS = [#'RUB', # Russian Ruble
           #'CAD', # Canadian Dollar
           #'AFA', # Afghan Afghani
           'EUR', # Euro
           'SAR', # Saudi Riyal
           'JPY', # Japanese Yen
           'ISK', # for the PLEX
           'IQD', # Iraqi Dinar
           'CHF'] # Swiss Franc 

def load_target(TARGET):
    '''
    request from https://fxtop.com
    and get a target currency to match against USD
    return None if invalid response or return full response object
    '''
    url = f'https://fxtop.com/en/historical-exchange-rates.php?A=1&C1=USD&C2={TARGET}&YA=1&DD1=01&MM1=01&YYYY1=1953&B=1&P=&I=1&DD2=23&MM2=07&YYYY2=2021&btnOK=Go%21'
    response = requests.get(url)
    if response.status_code != 200:
        return None
    else:
        print(f'retrieved {TARGET} page')
        return response

def parse_response(response, table_index=29):
    '''
    parse the response object and traverse the table containing the
    exchange rate data which should be in the 29th table on the page
    '''
    soup = BeautifulSoup(response.text, 'html.parser')
    all_tables = soup.find_all('table')
    target_table = all_tables[table_index]
    target_as_list = [[td.get_text(strip=True) for td in tr.find_all('td')]
            for tr in target_table.find_all('tr')]
    return target_as_list

def write_values(lst_of_lsts, nation):
    '''
    accepts the output of  the parse_response() function
    and writes the values to a csv file using the nation tag
    as the name of the csv file
    '''
    write_file = f'{nation}.csv'
    with open(write_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(lst_of_lsts)
    print(f'{nation}.csv written')


def main():
    for nation in TARGETS:
        exchange = load_target(nation)
        if exchange:
            history = parse_response(exchange)
            if history:
                write_values(history, nation)
        print('waiting')
        time.sleep(10)

if __name__ == '__main__':
    main()
