import requests
from bs4 import BeautifulSoup
from threading import Thread
import os
from multiprocessing.dummy import Pool as ThreadPool

#remove special characters from episode's title
def clean_name(value):
	deletechars = '\/:*?"<>|'
	for c in deletechars:
		value = value.replace(c,'')
	return value;

#get episode's page
def get_page(url, name):
	episode = requests.get(url)
	page = episode.content
	soup_page = BeautifulSoup(page, "lxml")

	divs = soup_page.findAll('div')
	for div in divs:
		#find mp3 url
		if div.get('data-bt-audio-url'):
			mp3_url = div.get('data-bt-audio-url')
			get_MP3(url, name)
			

#download mp3 file
def get_MP3(mp3_url, name):
	mp3_name = '{}.mp3'.format(name)
	file_path = os.path.join('MP3', mp3_name)

	#check if the file doesn't exist already
	if not os.path.exists(file_path):
		print('downloading {}...'.format(name))
		data = requests.get(mp3_url).content
		with open(file_path, 'wb') as file:
			file.write(data)
	else:
		print('already exists {}'.format(name))

#multithread execution
def parallel_execution(links, names, threads=2):
	pool = ThreadPool(threads)
	results = pool.map(get_page_wrapper, zip(links, names))
	pool.close()
	pool.join()

#wrapper - map only supports functions with a single argument
def get_page_wrapper(args):
	return get_page(*args)



if __name__ == "__main__": 

	url = 'https://talkpython.fm/episodes/all'
	response = requests.get(url)
	content = response.content
	soup = BeautifulSoup(content, "lxml")

	if not os.path.exists('MP3'):
		os.mkdir('MP3')

	link_list = []
	name_list = []

	for tr in soup.table.findAll('tr'):
		temp = ""
		for td in tr.findAll('td'):
			temp = '{} - {}'.format(temp, td.text)
			if td.a:
				href = (td.a.get('href'))
				link = '{}{}'.format('https://talkpython.fm', href)
				link_list.append(link)
				numb_id = temp.find('#')
				name_list.append(clean_name(temp[numb_id:]))

	parallel_execution(link_list, name_list, 4)