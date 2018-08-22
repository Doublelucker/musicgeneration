import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import sys
import os
import re
import click

@click.command(name='visualize', help=__doc__)
@click.option('--startindex', 'startindex',
              default=0, show_default=True, help="If a process falls down for some reason (There is not much exception-work done here, along with network falling down), you can pick the line number from '%genre%links.txt' file that has been created before, to start downloading from a certain step" 
              )
@click.option('--download_path', 'download_path',
              default="F:/music", show_default=True, help="Prefix path to where you want to store your melodies (they will be a stored in a %genre% folder)" 
              )
def rename(startindex, download_path):
	folders = ['barndances', 'hornpipes', 'jigs', 'mazurkas', 'polkas', 'reels', 'slides', 'strathpeys', 'three-twos',
			   'waltz']
	bad_links = []
	for folder in folders:
		path = os.path.join(download_path, folder)
		if os.path.exists(path):
			if all(os.path.isdir(os.path.join(path, x)) for x in os.listdir(path)):
				print("There are no more files left in the directory of {0} genre".format(folder))
				continue
			with open('../SessionLinks/%slinks.txt' % folder) as f:
				full_links = f.read().splitlines()
			path = os.path.join(download_path, folder)
			for link in full_links[startindex:]:
				print(link)
				response = requests.get(link)
				soup = BeautifulSoup(response.content, 'html.parser')
				name = soup.find('h1')
				bad_elem = name.find('a')
				try:
					bad_elem.decompose()
				except:
					bad_links.append(link)
					continue
				print(name.get_text())
				tune_number = ''.join(link.split('/')[-2:]).replace('s', '')
				print(tune_number)
				folder2 = re.sub(r'[/\&~?*|<>";:+]', '', name.get_text().strip()).strip()
				try:
					files = [x for x in os.listdir(os.path.join(path)) if re.match(tune_number + 'setting', x)]
				except FileNotFoundError:
					continue
				files.sort(key=lambda x: int(x.split('setting')[1].split('.')[0]))
				different_tunes = soup.find(id='settings').find_all(class_='setting')
				settings = [s.get('id') + '1' for s in different_tunes]

				for tune, file, setting in zip(different_tunes, files, settings):
					# print(setting, file)
					attrs = [t.split(': ')[1].replace('/', '-') for t in
							 tune.find(class_='notes').get_text().strip().split('\n')[:7] if t != '']
					attrs[2] = attrs[2].upper()[0]
					attrs[1] = re.sub(r'[/\&~?*|<>";:+]', '', attrs[1].strip()).strip()
					attrs[0], attrs[1] = attrs[1], attrs[0]
					name = '_'.join([link.split('/')[-1]] + attrs) + '.mid'
					if not os.path.exists(os.path.join(path, folder2)):
						os.mkdir(os.path.join(path, folder2))
					if setting == re.search('(setting[0-9]{1,10})', file).group(0):
						os.rename(os.path.join(path, file), os.path.join(path, folder2, name))
		else:
			print("You've given the wrong path or there is no music downloaded for {0}".format(folder))


if __name__ == '__main__':
	rename()
