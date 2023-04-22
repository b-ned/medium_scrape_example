# Step 1
# ========================================================
# Import Dependencies
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

from datetime import datetime
import csv


# Create a webdriver instance
driver = webdriver.Firefox()
# Navigate to the website
driver.get('https://www.etsy.com/')


# Step 2
# ========================================================
# Create waiting object that waits max. 5 seconds
wait = WebDriverWait(driver, 5)
try:
	# Wait until button appears. Locate button using XPath
	button_cookie_popop = wait.until(EC.visibility_of_element_located((By.XPATH, '//button[contains(text(), "Accept")]')))
	# Click button
	button_cookie_popop.click()
except TimeoutException:
	print('No Cookie Pop up')

# Step 3
# ========================================================
# Define input parameters
query = "sketchbook"

# Find the search box using unique id
search_box = driver.find_element(By.ID, 'global-enhancements-search-query')

# Send the query
search_box.send_keys(query)

# Find the search button and click it
search_button = driver.find_element(By.CSS_SELECTOR, '.wt-input-btn-group__btn.global-enhancements-search-input-btn-group__btn')
actions = ActionChains(driver)
actions.move_to_element(search_button)
actions.click(search_button)
actions.perform()

# Wait for the search results to load
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".v2-listing-card")))


# Step 4
# ========================================================
# Find the "Sort by" dropdown button
sort_button = wait.until(EC.visibility_of_element_located((By.XPATH, '//span[contains(text(), "Sort by:")]')))

# Scroll down to sort button.
driver.execute_script("arguments[0].scrollIntoView();", sort_button)
sort_button.click()

# Wait for the "Top customer reviews" option to appear and click on it
top_reviews_option = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a.wt-menu__item:nth-child(5)')))
top_reviews_option.click()


# Step 5
# ========================================================
# Create output file path
today = datetime.today().strftime('%Y-%m-%d')
file_path = f'./output/{query.replace(" ", "_")}_{today}.csv'

# Open a CSV file for writing
with open(file_path, 'w', newline='') as csvfile:
	# Create a CSV writer
	writer = csv.writer(csvfile)
	# Write the header row
	writer.writerow(['listing_id','title', 'price', 'url', 'shop_id'])


	# Step 6
	# ========================================================
	page_nr = 0
	while page_nr < 11:
		try:
			# Get the HTML content of the current page
			html = driver.page_source
			# Create a BeautifulSoup object
			soup = BeautifulSoup(html, 'html.parser')
			# Find all the product elements on the page
			product_elements = soup.select('.v2-listing-card')
			
			for product_element in product_elements:
				title = product_element.select('h3')[0].get_text(strip=True)
				price = product_element.select('span.currency-value')[0].get_text(strip=True)
				url = product_element.select('a')[0]['href']
				shop_id = product_element.get_attribute_list('data-shop-id')[0]
				listing_id = product_element.get_attribute_list('data-listing-id')[0]
				
				# Write the product data to the CSV file
				writer.writerow([listing_id,title, price, url, shop_id])

			# Find the pagination element that contains the next button
			parent_element = driver.find_elements(By.CSS_SELECTOR, 'ul.wt-action-group.wt-list-inline.search-pagination')[-1]

			# Find all the list items within the pagination element
			list_items = parent_element.find_elements(By.TAG_NAME, "li")

			# Get the last list item; the Next Button
			next_button = list_items[-1]

			# Scroll to Next Button; All the way down.
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

			# Check if the "next" button is disabled
			if 'disabled' in next_button.get_attribute('class'):
				break

			next_button.click()
			page_nr +=1
		
		except NoSuchElementException as e:
			print(e)
			break
			
driver.close()
print('Done')