
'''

Slack - Automation Interview Tasks
Task 1

Srinivaas Sekaran
June 16, 2017

star_message.py

Automates functional test of sending a message, 
starring, and verification in Slack on Chrome.

Functional approach for extensibility and reusability


Passing on Chrome 58.0.3029.110 MacOS Sierra 10.12

'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Driver initialization 
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

# Configuration
with open('config.json') as config:
	user_config = json.load(config)
slack_team_name = user_config['TEAM_NAME']
slack_url_name = user_config['TEAM_URL']
slack_recepient_username = user_config['RECEPIENT']

my_message = 'Hello, world!'

def open_slackbot_conversation(team_url, recepient_username):
	driver.get('https://' + team_url + '.slack.com/messages/@' + slack_recepient_username)

def login(user, password):
	username_field = driver.find_element_by_id('email')
	password_field = driver.find_element_by_id('password')

	logger.info('Signing in as ' + user)

	username_field.send_keys(user)
	password_field.send_keys(password)
	driver.find_element_by_id('signin_btn').click()

def send_message(message):
	logger.info('Sending message to Slackbot ...')
	try:
		# Wait until slackbot page is loaded
		element = wait.until(EC.text_to_be_present_in_element((By.ID, 'channel_name'), slack_recepient_username))
	except:
		logging.exception('Cannot find element!')

	msg_box = driver.find_element_by_id('msg_input')
	actions = webdriver.ActionChains(driver)
	actions.move_to_element(msg_box)
	actions.click()
	
	actions.send_keys(message)
	actions.perform()
	msg_box.submit()
	logger.info('Message sent: ' + message)

def star_message():
	logger.info('Starring message ...')
	
	# Wait until Slackbot responds to prevent DOM changes altering XPath
	wait_for_slackbot_response = wait.until( lambda driver: driver.find_element_by_xpath(
		'//*[@id="msgs_div"]/div[1]/div[2]/ts-message[last()]').get_attribute('data-member-id') == 'USLACKBOT'
	)
	body_element = driver.find_element_by_xpath('//*[@id="msgs_div"]/div[1]/div[2]/ts-message[last()-1]')
	star = driver.find_element_by_xpath('//*[@id="msgs_div"]/div[1]/div[2]/ts-message[last()-1]/div[2]/div/div/span[2]/button')

	# Hover over message
	actions = webdriver.ActionChains(driver)
	actions.move_to_element(body_element).perform()

	star.click()
	logger.info('Message starred!')

def search_star(search_query):
	logger.info('Searching starred messages ...')
	search_field = driver.find_element_by_id('search_terms')
	search_field.send_keys(search_query)
	search_field.submit()

def verify_search(message):
	logger.info('Verifying message in search results ...')
	search_successful = wait.until(EC.text_to_be_present_in_element((By.ID, 'search_heading'), 'Search Results'))
	search_elements = driver.find_elements_by_css_selector('.search_message_result.null_transform')
	search_results = [result.text for result in search_elements]

	try: 
		for string in search_results:
			if string.find(message) != -1:
				logger.info('Verification successful: Message is in search results')
	except:
		logging.exception('Message is not in search results!')

def click_starred():
	logger.info('Toggling star icon ...')
	driver.find_element_by_id('stars_toggle').click()
	logger.info('Star icon clicked!')

def verify_starred(message):
	logger.info('Verifying message in starred list ...')

	# Wait until starred panel is toggled and active
	panel_successful = wait.until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="stars_tab"]/div[1]/div/h2'), 'Starred Items'))
	toggle_successful = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn_basic.close_flexpane')))
	wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'star_item')))

	starred_elements = driver.find_elements_by_class_name('star_item')
	starred_results = [result.text for result in starred_elements]
	try: 
		for string in starred_results:
			if string.find(message) != -1:
				logger.info('Verification successful: Message is in starred list')
	except:
		logging.exception('Message is not in starred list!')

def main():
	logger.info('Starting user workflow: Starring messages')

	open_slackbot_conversation(slack_url_name, slack_recepient_username)

	# Login if prompted
	if driver.find_element_by_id('signin_header'):
		login(user_config['USERNAME'], user_config['PASSWORD'])

	# Ensure page loaded and send message to Slackbot
	assert slack_team_name in driver.title
	send_message(my_message)

	# Star message
	star_message()

	# Search for starred messages and verify in results
	search_star('has:star')
	verify_search(my_message)

	# Click on star icon and verify in results
	click_starred()
	verify_starred(my_message)

	# End session
	logger.info('Finished user workflow sucessfully: Starring messages')
	driver.close()


if __name__ == '__main__':
	main()
