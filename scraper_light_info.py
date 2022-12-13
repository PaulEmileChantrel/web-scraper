# Step 0 : Download chromedriver -> https://chromedriver.chromium.org/downloads
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

import pandas as pd
import os
import sys

# Application path
application_path = "/Users/paul-emile/Documents/PythonProject/scraping/"
file_name = 'real_estate_data.csv'
file_path = os.path.join(application_path,file_name)

#Target website
website = "https://www.realtor.ca/carte#ZoomLevel=10&Center=43.658183%2C-79.345829&LatitudeMax=44.12234&LongitudeMax=-78.05356&LatitudeMin=43.19041&LongitudeMin=-80.63810&Sort=6-D&PGeoIds=g30_dpz89rm7&GeoName=Toronto%2C%20ON&PropertyTypeGroupID=1&PropertySearchTypeId=0&TransactionTypeId=2&Currency=CAD"
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

# load or create a dataframe
try:
    df = pd.read_csv(file_path)
except:
    df = pd.DataFrame()


def scrape_page(df):
    #get html container with their xpath
    containers = driver.find_elements(by="xpath",value="//div[@class='cardCon']")

    # We iterate through the containers to get the info
    for container in containers:
        try:
            link = container.find_element(by="xpath",value='./span/div/a').get_attribute("href")
        except:
            link = ""
            #print(container.find_element(by="xpath",value='./span/div').page_source)
        lat_long = container.find_element(by="xpath",value='./span/div').get_attribute("data-value")#data_value
        image = container.find_element(by="xpath",value='./span/div/a/div/img').get_attribute("src")
        price = container.find_element(by="xpath",value='./span/div/a/div/div/div').text
        address = container.find_element(by="xpath",value='./span/div/a/div/div/div[3]').text
        try:
            bedrooms = container.find_element(by="xpath",value='./span/div/a/div/div/div[4]/div/div/div').text
        except:
            bedrooms = 0
        listed_since = container.find_element(by="xpath",value='./span/div/div[2]/div[2]').text
        try :#In case we don't have a bathroom
            bathrooms = container.find_element(by="xpath",value='./span/div/a/div/div/div[4]/div[2]/div/div').text
        except:
            bathrooms = 0

        # string processing
        id,lat,long = lat_long.split('_')
        try:
            bedrooms,smaller_rooms = bedrooms.split(' + ')
        except:
            smaller_rooms = 0

        since,time_number,time_unit = listed_since.split(' ')
        price = float(price.replace('$','').replace(' ',''))
        #print(price)

        #create a new row
        new_row = pd.DataFrame({'id':[id],'link':[link],
                                        'image':[image],
                                        'time_number':[time_number],
                                        'time_unit':[time_unit],
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
    time.sleep(4)
    return df

len_df = df.shape[0]
for i in range(50):
    df = scrape_page(df)
    if len_df ==df.shape[0]:
        break
    else:
        len_df = df.shape[0]


df.drop_duplicates(subset=['address'],inplace=True)
df.to_csv(file_path,index=False)
driver.quit()
