#################################
##### Name: Samuel Owen
##### Uniqname: owensam
#################################

from bs4 import BeautifulSoup
import requests
import os
import json
from secrets import key # file that contains your API key
import pickle


class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category, name, address, zipcode, phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self):
         '''Returns a formatted string representation of itself

    Parameters
    ----------

    Returns
    -------
    str
    '''
         return self.name + ' (' + (str(self.category)) + ')' + ': ' +self.address + ' ' + self.zipcode


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    url = 'https://www.nps.gov/index.htm'
    #'https://www.nps.gov/index.htm'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html5lib')
    #print(soup.prettify())
    state_dict = {}
    x = soup.findAll('ul', {'class', 'dropdown-menu SearchBar-keywordSearch'})[0]
    for state in x.findAll('a'):
        state_dict[state.text] = 'https://www.nps.gov' + state['href'] # prints state names
    return state_dict
    #     site_dict = {}
    #     response = requests.get('https://www.nps.gov' + state['href']) # prints state names
    #     soup = BeautifulSoup(response.text, 'html.parser')
    #     parks_parent = soup.find('ul', id='list_parks')
    #     # print(parks_parent)
    #     parks_list = parks_parent.find_all('li', class_='clearfix')
    #     #print(parks_list)
    #     p_list = []
    #     for i in parks_list: # this for loop creates keys site_dict
    #         a = i.find_all('h3')
    #         p_list.append(a)
    #     h_list = []
    #     for i in range(len(p_list)): # this one creates the values for site_dict
    #         #print(p_list[i][0])
    #         a = p_list[i][0].find('a', href=True)
    #         h_list.append(a['href'])
    #     for key, value in zip(p_list, h_list): # this for loop adds them all to a dictionary
    #         site_dict[key[0].text] = value
    #     state_dict[state.text] = site_dict
    # with open('data/proj_cache.json', 'w') as f:
    #     json.dump(state_dict, f)
    # return state_dict
    #print(state_lst2)

def get_site_instance(site_url):
    '''Make an instance from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    url = 'https://www.nps.gov' + site_url + 'index.htm'
    #print(url)
    response = requests.get(url)
    if response.text:
        soup = BeautifulSoup(response.text, 'html.parser')

        category = soup.find('span', class_='Hero-designation').text
        #print(category)

        name = soup.find('a', class_='Hero-title').text
        #print(name)

        try:
            city = soup.find(itemprop='addressLocality').text
        except:
            city = 'None'
        #print(city)

        try:
            state = soup.find(itemprop='addressRegion').text
        except:
            state = 'None'
        #print(state)

        address = city + ', ' + state
        #print(address)

        try:
            zipcode = soup.find(itemprop='postalCode').text
        except:
            zipcode = 'None'
        #print(zipcode)

        try:
            phone = soup.find(itemprop='telephone').text
        except:
            phone = "None"
        #print(phone)
        x = NationalSite(category, name, address, zipcode, phone)

        return x

    else:
        print(response)

def get_sites_for_state(state_url, state_name):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    if os.path.exists(f"data/{state_name}.json"):
        # Loading cache of data
        with open(f'data/{state_name}.json', 'r') as f:
            return json.load(f)
    else:
        site_dict = {}
        response = requests.get(state_url)


        soup = BeautifulSoup(response.text, 'html.parser')
        parks_parent = soup.find('ul', id='list_parks')
        parks_list = parks_parent.find_all('li',class_='clearfix')
        p_list = []
        for i in parks_list: # this for loop creates keys site_dict
            a = i.find_all('h3')
            p_list.append(a)
        h_list = []
        for i in range(len(p_list)): # this one creates the values for site_dict
            #print(p_list[i][0])
            a = p_list[i][0].find('a', href=True)
            h_list.append(a['href'])
        for key, value in zip(p_list, h_list): # this for loop adds them all to a dictionary
            site_dict[key[0].text] = value
        with open(f'data/{state_name}.json', 'w') as f:
            json.dump(site_dict, f)
        return site_dict


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.

    https://www.mapquestapi.com/search/v2/radius?origin=Denver,+CO&radius=0.15&maxMatches=3&ambiguities=ignore&hostedData=mqap.ntpois|group_sic_code=?|581208&outFormat=json&key=KEY

    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''

    url = f"https://www.mapquestapi.com/search/v2/radius?origin={site_object.address.replace(' ','+')}&radius=10&maxMatches=10&ambiguities=ignore&hostedData=mqap.ntpois|&outFormat=json&key={key}"

    
    results = json.loads(requests.get(url).text)
    print('-'*20+'\n'+f"Places near {site_object.name}"+'\n'+('-'*20))
    for result in results['searchResults']:
        field = result['fields']
        print('-', field['name'], '('+field['group_sic_code_name_ext']+'):', field['address']+',', field['city'])

if __name__ == "__main__":
    # Creating cache of data
    if os.path.exists('data/proj_cache.json'):
        # Loading cache of data
        with open('data/proj_cache.json', 'r') as f:
            state_dict = json.load(f)
    else:
        state_dict = build_state_url_dict()
    
    #test2 = get_sites_for_state('https://www.nps.gov/state/mi/index.htm')
    #test1 = build_state_url_dict()
    # for i in test2:
    #     print(i.info())
    #print(test2)
    user_input = ''
    state_dict = build_state_url_dict()
    while user_input != 'Exit':
        user_input = input('Enter a state name (e.g. Michigan, michigan) or "exit"').title()
        if user_input in state_dict:
            # Running the program
            if os.path.exists(f'data/{user_input}.pkl'):
                print("Using cache")
                with open(f'data/{user_input}.pkl', 'rb') as f:
                    nat_sites = pickle.load(f)
            else:
                print("Fetching")
                site_dict = get_sites_for_state(state_dict[user_input], user_input)
                nat_sites = [get_site_instance(url) for url in site_dict.values()]
                with open(f'data/{user_input}.pkl', 'wb') as f:
                     pickle.dump(nat_sites, f)
            print(f'{"-"*30}\n List of national sites in {user_input}\n{"-"*30}')
            for i in range(len(nat_sites)):
                print(f'[{i+1}] {nat_sites[i].info()}')
            user_sel = ''
            while user_sel not in range(1,1+len(nat_sites)):
                try:
                    user_sel = int(input("Choose a park:"))
                    get_nearby_places(nat_sites[user_sel-1])
                except:
                    print('[Error] Invalid input')

        else:
            print('Not a valid state')

    

    # Requesting user input
    '''
    file1 = open("SoupPretty.txt", "a")
    file1.write(soup.prettify())
    file1.close()
    '''
    # Get site url
    # site_url_tag = soup.find('li', class_='undefined isCurrentPage')
    # site_url_path = site_url_tag.find('a')
    # print(site_url_path)
    '''
    <li class="undefined isCurrentPage" style="display: none;"><a href="/isro/index.htm" class="undefined isCurrentPage"><span>Park Home</span></a></li>
    '''
    
    # state_dict = build_state_url_dict()

    '''
    <a href="/cach/" id="anch_12">Canyon de Chelly</a>
    '''

    '''
    file1 = open("SoupPretty.txt", "a")
    file1.write(soup.prettify())
    file1.close()
    '''

    '''
    <div class="mailing-address" itemscope="" itemtype="http://schema.org/Place">
          <h4 class="org">
           Mailing Address:
          </h4>
          <div itemprop="address" itemscope="" itemtype="http://schema.org/PostalAddress">
           <p class="adr">
            <span class="street-address" itemprop="streetAddress">
             800 East Lakeshore Drive
            </span>
            <br/>
            <span>
             <span itemprop="addressLocality">
              Houghton
             </span>
             ,
             <span class="region" itemprop="addressRegion">
              MI
             </span>
             <span class="postal-code" itemprop="postalCode">
              49931
    '''
   