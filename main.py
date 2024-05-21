from selenium.webdriver import Chrome, Firefox, Edge, safari
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

url = 'https://finance.yahoo.com/'
# driver_path = 'chromedriver.exe'

# options = webdriver.ChromeOptions()
options = Options()
options.add_experimental_option("detach", True)
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

# service = Service(executable_path=driver_path)
service = Service(ChromeDriverManager().install())

browser = Chrome(service=service, options=options) # Driver 
browser.get(url)

search_field_id = 'ybar-sbq'

element_search_field = browser.find_element(By.ID, search_field_id)

element_search_field.clear() # Clears the search field
element_search_field.send_keys('TSLA') # Searching telsa
element_search_field.send_keys(Keys.ENTER)

# print(browser.page_source)

# This closes after operation completes
# browser.close() # Close current tab
# browser.quit() # will close the browser

