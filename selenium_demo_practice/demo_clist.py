import os
import time
import datetime
from collections import namedtuple # Organize records into a more organized format
###
# This is what we will usually use when it comes to selenium automation
import selenium.webdriver as webdriver
from selenium.webdriver import Chrome, Firefox, Edge, safari
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementNotInteractableException
###
from bs4 import BeautifulSoup
import pandas as pd

class ButtonDisabledException(Exception):
    """Custom exception for when the next button is disabled."""
    pass


# We want to grab the User-Agent from Headers in the Network tab under minneapolis.craigslist.org
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'

options = Options()
options.add_experimental_option("detach", True)
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

# service = Service(executable_path=driver_path)
service = Service(ChromeDriverManager().install())

browser = Chrome(service=service, options=options) # Driver 

browser.implicitly_wait(7) # The amount you want to wait till a webpage loads

url = 'https://minneapolis.craigslist.org/'
browser.get(url)

# We want to get the XPath
for_sale_element = browser.find_element(By.XPATH, "//a[@data-alltitle='all for sale']") # Single method
# print(for_sale_element.text)
# print(for_sale_element.location)
# print(for_sale_element.is_enabled()) # Check if elements are disabled

# Click on the element
for_sale_element.click()

# Select from dropdown (We want to select hennepin co)
dropdown_region = browser.find_element(By.XPATH, "//div[@class='cl-breadcrumb subarea-selector bd-combo-box static bd-vStat-valid']") 

# Getting the dropdown by xpath
click_region = dropdown_region.click()
select_region = browser.find_element(By.XPATH, "//button[@class='bd-button hnp']") # Look into getting the region dynamically
select_region.click()

# Picking a category for whats on sale
dropdown_category = browser.find_element(By.XPATH, "//div[@class='cl-breadcrumb category-selector bd-combo-box static bd-vStat-valid']")
dropdown_category.click()
select_category = browser.find_element(By.XPATH, "//button[@class='bd-button cba']")
select_category.click()

# Search Query (enter on input)
search_query = 'card'
search_field = browser.find_element(By.CSS_SELECTOR, "input[placeholder='search collectibles'][enterkeyhint='search']") # CSS METHOD 
search_field.clear() # Clears the field
search_field.send_keys(search_query) # Sends the search_query and types it out in the search bar
search_field.send_keys(Keys.ENTER) # This enters in the data
time.sleep(1) # Delay the execution to not get ip blocked

# Store listing into CSV and Excel File
posts_html = []
to_stop = False

while not to_stop:
    search_results = browser.find_element(By.ID, 'search-results-page-1')
    soup = BeautifulSoup(search_results.get_attribute('innerHTML'), 'html.parser')
    # Getting data into the posts_html list
    posts_html.extend(soup.find_all('li', {'class':'cl-search-result cl-search-view-mode-gallery'}))

    # Pagination
    try:
        browser.execute_script('window.scrollTo(0, 0)')
        next_button = browser.find_element(By.CLASS_NAME, "cl-next-page")

        if "bd-disabled" in next_button.get_attribute("class"):
            raise ButtonDisabledException("Next button is disabled. Stopping pagination.")
        
        time.sleep(1)
        next_button.click()
        time.sleep(1)
    except ButtonDisabledException:
        to_stop = True

print('Collected {0} listing'.format(len(posts_html)))


# Clean up and organize records
CraigslistPosts = namedtuple('CraigslistPost', ['title', 'price', 'post_timestamp', 'location', 'post_url', 'image_url']) # , 'location', 'post_url', 'image_url'
craigslist_posts = []

for post_html in posts_html:
    title = post_html.find('span', 'label').text
    price = post_html.find('span', 'priceinfo').text if post_html.find('span', 'priceinfo') else None
    # meta has multiple pieces of data in it that needs to be split between timestamp and location
    meta = post_html.find('div', 'meta')
    post_timestamp = meta.contents[0].strip()
    location = meta.contents[-1].strip()
    post_url = post_html.find('a', 'main').get('href')
    image_url = post_html.find('img').get('src') if post_html.find('img') else None
    craigslist_posts.append(CraigslistPosts(title, price, post_timestamp, location, post_url, image_url))

# print(craigslist_posts[0])

df = pd.DataFrame(craigslist_posts)
df.to_csv(f'{search_query} ({datetime.datetime.now().strftime("%Y_%m_%d %H_%M_%S")}).csv', index=False)

df['link'] = df.apply(lambda row: f'=HYPERLINK("{row["post_url"]}", "Link")', axis=1) # Hyper link to click to webpage
df.to_excel(f'{search_query} ({datetime.datetime.now().strftime("%Y_%m_%d %H_%M_%S")}).xlsx', index=False) # Export to excel

browser.quit()