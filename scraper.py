from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.firefox.options import Options

from bs4 import BeautifulSoup

from datetime import datetime
import csv

import os

def accept_cookies(driver):
	"""Accept cookies on the Etsy homepage"""
	wait = WebDriverWait(driver, 100)
	try:
		cookie_popup = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".wt-overlay__modal.wt-mb-xs-6.wt-overlay--animation-done")))
		button_cookie_popop = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".wt-btn.wt-btn--filled.wt-mb-xs-0")))
		button_cookie_popop.click()
	except:
		print("No Cookie Pop-up")

def search(driver, query):
	"""Search for a query on Etsy"""
	# Find the search box and enter a search query
	search_box = driver.find_element(By.ID, 'global-enhancements-search-query')
	search_box.send_keys(query)

	# Find the search button and click it
	search_button = driver.find_element(By.CSS_SELECTOR, '.wt-input-btn-group__btn.global-enhancements-search-input-btn-group__btn')
	wait = WebDriverWait(driver, 10)
	actions = ActionChains(driver)
	actions.move_to_element(search_button)
	actions.click(search_button)
	actions.perform()

	# Wait for the search results to load
	wait = WebDriverWait(driver, 100)
	wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".v2-listing-card")))

def sort_by_top_reviews(driver):
	"""Sort search results by top customer reviews"""
	# Click on the "Sort by" dropdown button
	wait = WebDriverWait(driver, 10)
	sort_button = wait.until(EC.visibility_of_element_located((By.XPATH, '//span[contains(text(), "Sort by:")]')))
	
	# Scroll down to sort button.
	driver.execute_script("arguments[0].scrollIntoView();", sort_button)
	
    # Move cursor to button
	actions = ActionChains(driver)
	actions.move_to_element(sort_button)
	actions.click(sort_button)
	actions.perform()
	wait = WebDriverWait(driver, 10)
	# Wait for the "Top customer reviews" option to appear and click on it
	top_reviews_option = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a.wt-menu__item:nth-child(5)')))
	top_reviews_option.click()


# Set run Headless for Docker Container
options = Options()
options.headless = True
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Create a webdriver instance
driver = webdriver.Firefox(options=options)
# Navigate to the website
driver.get('https://www.etsy.com/')

# Define input parameters
search_input = "sketchbook"
max_pages = 10

# Run Accept Cookies, Search and Sort
accept_cookies(driver)

search(driver, search_input)

sort_by_top_reviews(driver)

# Create output file path
today = datetime.today().strftime('%Y-%m-%d')
file_path = f'./output/{search_input.replace(" ", "_")}_{today}.csv'

# Create output folder if not exists
if not os.path.exists('./output'):
   os.makedirs('./output')

# Open a CSV file for writing
with open(file_path, 'w', newline='') as csvfile:
	# Create a CSV writer
	writer = csv.writer(csvfile)
	# Write the header row
	writer.writerow(['listing_id','title', 'price', 'url', 'shop_id'])

	page_nr = 0
	while True:
		try:
			# Get the HTML content of the current page
			html = driver.page_source
			# Create a BeautifulSoup object
			soup = BeautifulSoup(html, 'html.parser')
			# Find all the product elements on the page
			product_elements = soup.select('.v2-listing-card')

			for product_element in product_elements:
				title = product_element.select('h3.wt-text-caption.v2-listing-card__title.wt-text-truncate')[0].get_text(strip=True)
				price = product_element.select('span.currency-value')[0].get_text(strip=True)
				url = product_element.select('a')[0]['href']
				shop_id = product_element.get_attribute_list('data-shop-id')[0]
				listing_id = product_element.get_attribute_list('data-listing-id')[0]

				# Write the product data to the CSV file
				writer.writerow([listing_id,title, price, url, shop_id])

			# Find the parent element that contains the next button
			parent_element = driver.find_elements(By.CSS_SELECTOR, 'ul.wt-action-group.wt-list-inline.search-pagination')[-1]

			# Find all the list items within the parent element
			list_items = parent_element.find_elements(By.TAG_NAME, "li")
			
			
			# Get the last list item, which should be the next button
			next_button = list_items[-1]
			# Scroll to Next Button
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			wait = WebDriverWait(driver, 100)

			# Check if the "next" button is disabled
			if 'disabled' in next_button.get_attribute('class'):
				break
			
			next_button.click()
			wait = WebDriverWait(driver, 100)
			page_nr +=1
			if page_nr > max_pages:
				break
			print("Page : ", page_nr)

		except NoSuchElementException as e:
			print(e)
			break
			
driver.close()
print('Done')