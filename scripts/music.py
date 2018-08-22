import sys
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import os
import click

@click.command(name='visualize', help=__doc__)
@click.option('--genre', 'genre', required=True, help="One of the genres from thesession.org in Tunes (except 'slip jigs', didn't do those)")
@click.option('--linkcheck', 'linkcheck',
              default=0,
              show_default=True, required=True, help="Whether to gather links for melodies or not. '0' - is to gather, anything else will skip that part")
@click.option('--startindex', 'startindex',
              default=0, show_default=True, help="If a process falls down for some reason (There is not much exception-work done here, along with network falling down), you can pick the line number from '%genre%links.txt' file that has been created before, to start downloading from a certain step" 
              )
@click.option('--path_to_driver', 'path_to_driver',
              default="../chromedriver.exe", show_default=True, help="The script uses selenium with chrome, so you need a chromedriver. There's one in the project, but they update, so you would want to download a new one at some point and put here the path to it." 
              )
@click.option('--download_path', 'download_path',
              default="F:/music", show_default=True, help="Prefix path to where you want to store your melodies (they will be a stored in a %genre% folder)" 
              )			  

def download(genre, linkcheck, startindex, path_to_driver, download_path):
	link = 'https://thesession.org/tunes/popular/%s?page=1' % genre
	orig_link = 'https://thesession.org'
	full_links = []
	path = '%s\%s' % (download_path, genre)
	if not os.path.isdir(path):
		os.mkdir(path)
	response = requests.get(link)
	soup = BeautifulSoup(response.content, 'html.parser')
	pages_quant = int(soup.find(class_='pagination') \
					  .get_text() \
					  .split(' ')[-1] \
					  .split('\n')[0])
	if linkcheck == 0:
		for i in range(pages_quant):
			print(link)
			resp = requests.get(link)
			soup = BeautifulSoup(resp.content, 'html.parser')
			links = soup.find_all('span', class_='manifest-item-title')
			links = [orig_link + link.find('a').get('href') for link in links]
			link = link.replace('page=%d' % (i + 1), 'page=%d' % (i + 2))
			full_links.extend(links)
		with open('../SessionLinks/%slinks.txt' % genre, 'w', encoding='utf8') as file:
			for item in full_links:
				file.write('%s\n' % item)
	else:
		with open('../SessionLinks/%slinks.txt' % genre) as f:
			full_links = f.read().splitlines()
	options = webdriver.ChromeOptions()
	prefs = {
		'profile.default_content_settings.popups': 0,
		'download.default_directory': r'%s\%s\\' % (download_path, genre),
		'directory_upgrade': True}
	options.add_experimental_option('prefs', prefs)
	browser = webdriver.Chrome(path_to_driver, chrome_options=options)
	for i, link in enumerate(full_links[int(startindex):]):
		print(link, i)
		browser.get(link)
		elements = browser.find_elements_by_css_selector('.reveals')
		for element in elements:
			element.find_element_by_css_selector('.button.reveal.action.download').click()
			browser.execute_script('arguments[0].scrollIntoView();',
								   element.find_element_by_css_selector(
									   '.button.reveal.action.download'
								   ))
			time.sleep(1)
			element.find_element_by_css_selector('.discrete.action.listen').click()
	browser.quit()

if __name__ == '__main__':
    download()