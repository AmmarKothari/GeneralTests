from selenium import webdriver
from selenium.webdriver.support.ui import Select

import os
import pdb
import time
import re
import subprocess
import nmap
import sys

DRIVER_LOCATION = os.path.expanduser('~/Downloads/chromedriver')
CHROME_USER_PROFILE_LOCATION = os.path.expanduser("~/.config/google-chrome")
WI_FI_LABEL = "Wi-Fi IP"
INFORMATION_OF_INTEREST = ["Receiver Type", "Serial Number", WI_FI_LABEL, "Firmware Version", "RTK Version", "Hardware Version", "System Name"]
# should go to a built path
CONFIG_FILE_PATH = "/home/ammar/Downloads/3521_3rd_hq.cfg"


# TODO: Open window with user profile so that saved passwords can be used.
# TODO: print out values in an easy to copy paste format with regex
# TODO: detect if being run as sudo -- and warn that no mac address will be returned

class WebpageDriver(object):
	def __init__(self, ip):
		self.driver = self.init_driver()
		self.ip = ip

	def init_driver(self):
		options = webdriver.chrome.options.Options()
		options.add_argument('--no-sandbox')
		# options.add_argument("--user-data-dir={}".format(CHROME_USER_PROFILE_LOCATION)) #Path to your chrome profile

		driver = webdriver.Chrome(DRIVER_LOCATION, options=options)
		return driver

	def open_subpage(self, page_name):
		self.driver.get('http://{}/{}.html'.format(self.ip, page_name))
		time.sleep(0.5) # need this so the page can load

def do_nmap_scan(ip):
	nm = nmap.PortScanner()
	scan_info = nm.scan(ip, arguments = '-sP')
	try:
		print('MAC ADDRESS: {}'.format(scan_info['scan'][ip]['addresses']['mac']))
	except:
		print('Couldn\'t find mac address')



def get_identity_info(driver):
	driver.open_subpage('xml/identity')

	elements_with_info = []
	for ids in ["odd", "even"]:
		elements_with_info.extend(driver.find_elements_by_class_name(ids))

	# gets information from the interface
	copy_paste_vals = []
	for element in elements_with_info:
		for label in INFORMATION_OF_INTEREST:
			pattern = "^{}".format(label)
			match = re.match(pattern, element.text)
			if match:
				print element.text

				copy_paste_vals.append(element.text.split(':', 1))

def load_config_file(driver, config_file_path):
	try:
		driver.open_subpage('forms/appFile')
		pdb.set_trace()
		select_upload_file = Select(driver.driver.find_element_by_id('option'))
		select.select_by_visible_text('Upload File')

		file_to_upload = driver.driver.find_element_by_id('appUploadFile')
		file_to_upload.send_keys(CONFIG_FILE_PATH)

		ok_button = driver.driver.find_element_by_id('okButtonId')
		ok_button.click()

		print('Config file loaded')

	except:
		print('Config file failed to load')
		raise


def get_gps_data():

	if len(sys.argv) == 1:
		print('no ip address give')
		return
	wi_fi_addr = sys.argv[1] # assume this is given by the user

	driver = WebpageDriver(wi_fi_addr)

	# get_identity_info(driver)

	load_config_file(driver, CONFIG_FILE_PATH)

	# do_nmap_scan(wi_fi_addr)

get_gps_data()

