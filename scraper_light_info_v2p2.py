# Step 0 : Download chromedriver -> https://chromedriver.chromium.org/downloads
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

import pandas as pd
import os
import sys
from selenium.webdriver.common.keys import Keys
from url_parser import parse_url, get_url, get_base_url
from datetime import date
from datetime import timedelta
from confing import target_townhouse,target_house,target_appt
# V2.2 -> scrap data using filter to get more info

# Application path
application_path = "/Users/paul-emile/Documents/PythonProject/scraping/"
file_name = 'real_estate_data_v2p2.csv'
file_path = os.path.join(application_path,file_name)
target_links = [target_townhouse,target_house,target_appt]
property_types = ['Row /Town House', 'House', 'Appartement']



def scrape_page(df):


    #get html container with their xpath
    containers = driver.find_elements(by="xpath",value="//div[@class='cardCon']")

    # We iterate through the containers to get the info
    for container in containers:
        try:
            link = container.find_element(by="xpath",value='./span/div/a').get_attribute("href")
        except:
            link = ""
            #print(container.find_element(by="xpath",value='./span/div').page_source
        try:
            lat_long = container.find_element(by="xpath",value='./span/div').get_attribute("data-value")#data_value
        except:

            id,lat,long = 0,0,0
        else:
            # string processing
            id,lat,long = lat_long.split('_')
        try:
            image = container.find_element(by="xpath",value='./span/div/a/div/img').get_attribute("src")
        except:
            image = ""
        try:
            price = container.find_element(by="xpath",value='./span/div/a/div/div/div').text
        except:
            price = 0
        try:
            address = container.find_element(by="xpath",value='./span/div/a/div/div/div[3]').text
        except:
            address = ""
        try:
            bedrooms = container.find_element(by="xpath",value='./span/div/a/div/div/div[4]/div/div/div').text
        except:
            bedrooms = 0
        try :
            listed_since = container.find_element(by="xpath",value='./span/div/div[2]/div[2]').text
        except:
            posted = today - timedelta(days=float(8))
        else:
            time_number,time_unit,since = listed_since.split(' ')#depend the language
            print(time_number,time_unit)
            if time_unit == 'min':
                posted = today - timedelta(minutes=float(time_number))
            elif time_unit == 'hours':
                posted = today - timedelta(hours=float(time_number))
            elif time_unit == 'days':
                posted = today - timedelta(days=float(time_number))
            else:# more than 7 days ago
                posted = today- timedelta(days=float(8))
            print(posted)
        try :#In case we don't have a bathroom
            bathrooms = container.find_element(by="xpath",value='./span/div/a/div/div/div[4]/div[2]/div/div').text
        except:
            bathrooms = 0


        try:
            bedrooms,smaller_rooms = bedrooms.split(' + ')
        except:
            smaller_rooms = 0

        if isinstance(price,str):
            try:
                price = float(price.replace('$','').replace(' ','').replace(',','').replace('/ac',''))
            except:
                pass
        #create a new row
        new_row = pd.DataFrame({'id':[id],'link':[link],
                                        'image':[image],
                                        'posted':[posted],
                                        'price':[price],
                                        'address':[address],
                                        'lat':[lat],
                                        'long':[long],
                                        'bedrooms':[bedrooms],
                                        'smaller_rooms':[smaller_rooms],
                                        'bathrooms':[bathrooms],
                                        })
        #print(new_row)
        df = pd.concat([df,new_row],ignore_index=True)




    print(df.shape[0])
    df.to_csv(file_path,index=False)

    # locate the next page button and click on it
    next_page_link = driver.find_element(by="xpath",value='//div[@id="mapSidebarFooterCon"]/span/div/a[3]')
    next_page_link.click()

    # wait a bit
    time.sleep(1)
    return df

len_df = df.shape[0]


def reset_first_page(driver):
    try:
        elmt = driver.find_element(by="xpath",value=("//ul[@class='select2-results__options']/li"))
        elmt.click()

    except:
        pass
def get_max_page(driver):
    try:
        max_page = driver.find_element(by="xpath",value=('//div[@class="paginationDetailsPageDtlCon"]/span[2]')).text
    except:
        max_page = 0
    else:
        if max_page =='50+':
            return 50-1
        else:
            try:
                return int(max_page)-1
            except:
                return 0

def find_in_fragment(key_word,fragment):
    pos_start = fragment.find(key_word)
    fragment_slice = fragment[pos_start+len(key_word):]
    pos_end = fragment_slice.find('&')
    value = fragment_slice[:pos_end]
    return value

def get_lat_long_min_max(driver):
    url = driver.current_url
    url = parse_url(url)
    fragment = url['fragment']
    lat_min = float(find_in_fragment('LatitudeMin=',fragment))
    lat_max = float(find_in_fragment('LatitudeMax=',fragment))
    long_min = float(find_in_fragment('LongitudeMin=',fragment))
    long_max = float(find_in_fragment('LongitudeMax=',fragment))
    return lat_min,lat_max,long_min,long_max

def move_right(driver):
    lat_min,lat_max,new_long_min,long_max = get_lat_long_min_max(driver)
    elmt = driver.find_element(by="xpath",value=("//div[@id='mapBodyCon']/div/div/div[2]/div[2]"))
    elmt.click()

    while long_max>new_long_min: #the longitude is negative

        action = ActionChains(driver)
        action.key_down(Keys.RIGHT).pause(0.4).key_up(Keys.RIGHT).perform()

        url = driver.current_url
        url = parse_url(url)
        fragment = url['fragment']
        new_long_min = float(find_in_fragment('LongitudeMin=',fragment))
        #print(new_long_min,long_max)

def move_left(driver):
    lat_min,lat_max,long_min,new_long_max = get_lat_long_min_max(driver)
    elmt = driver.find_element(by="xpath",value=("//div[@id='mapBodyCon']/div/div/div[2]/div[2]"))
    elmt.click()

    while new_long_max>long_min: #the longitude is negative

        # elmt.send_keys(Keys.LEFT)
        action = ActionChains(driver)
        action.key_down(Keys.LEFT).pause(1).key_up(Keys.LEFT).perform()

        url = driver.current_url
        url = parse_url(url)
        fragment = url['fragment']
        new_long_max = float(find_in_fragment('LongitudeMax=',fragment))
        #print(new_long_min,long_max)

def move_down(driver):
    lat_min,new_lat_max,long_min,long_max = get_lat_long_min_max(driver)

    elmt = driver.find_element(by="xpath",value=("//div[@id='mapBodyCon']/div/div/div[2]/div[2]"))
    elmt.click()
    while lat_min<new_lat_max:


        action = ActionChains(driver)
        action.key_down(Keys.DOWN).pause(0.4).key_up(Keys.DOWN).perform()

        url = driver.current_url
        url = parse_url(url)
        fragment = url['fragment']
        new_lat_max = float(find_in_fragment('LatitudeMax=',fragment))
        #print(new_long_min,long_max)

def move(driver,LAT_MIN,LONG_MAX,LONG_MIN,moving_from_left_to_right):

    lat_min,lat_max,long_min,long_max = get_lat_long_min_max(driver)
    if lat_max < LAT_MIN:
        #end
        return moving_from_left_to_right,False
    reset_first_page(driver)
    if moving_from_left_to_right:
        print(long_max,LONG_MAX)
        if long_min<LONG_MAX:# we can still move right
            move_right(driver)
            return moving_from_left_to_right,True
        else:
            moving_from_left_to_right = False
            move_down(driver)
            return moving_from_left_to_right,True
    else:
        print('switch')
        print(long_max,LONG_MIN)
        if long_max>LONG_MIN:# we can still move right
            move_left(driver)
            return moving_from_left_to_right,True
        else:
            moving_from_left_to_right = True
            move_down(driver)
            return moving_from_left_to_right,True

for target_link,property_type in zip(target_links,property_types):
    #Target website
    website = target_link
    #chromedriver location
    path = "/Users/paul-emile/Downloads/chromedriver"

    # # Options
    # options = Options()
    # # don't open the browser
    # options.headless=True

    #Initializing Chrome driver
    service = Service(executable_path=path)
    driver = webdriver.Chrome(service = service)

    #Open the web page
    driver.get(website)

    # if we have a captcha at the start, we can do it manually
    import time
    time.sleep(20)


    LONG_MIN = -79.92244 #left
    LONG_MAX = -79.05638  #right
    LAT_MIN = 43.61090
    moving_from_left_to_right = True
    today = date.today()
    # load or create a dataframe
    try:
        df = pd.read_csv(file_path)
    except:
        df = pd.DataFrame()

    need_move = True
    while need_move:
        max_page = get_max_page(driver)

        #print(max_page)

        for i in range(max_page):
            df = scrape_page(df)

        df.drop_duplicates(subset=['address'],inplace=True)
        moving_from_left_to_right,need_move = move(driver,LAT_MIN,LONG_MAX,LONG_MIN,moving_from_left_to_right)
        time.sleep(4)#give the time to laod the page

    df.drop_duplicates(subset=['address'],inplace=True)
    df['property_type'] = property_type
    df.to_csv(file_path,index=False)
    driver.quit()
