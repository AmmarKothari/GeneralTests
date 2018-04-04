

import pdb
from bs4 import BeautifulSoup
import bs4
import urllib2


def get_divs(soup):
	all_divs = soup.find_all("div")
	pdb.set_trace()
	for div in all_divs:
		print div.get('href')
	return all_divs

def get_links(soup):
	all_links = soup.find_all("a")
	for link in all_links:
		print link.get('href')
	return all_links


def get_tables(soup):
	all_tables=soup.find_all('table')
	for table in all_tables:
		i = 1
	return all_tables

def get_element_id(soup, tag_id):
	item = soup.find(id=tag_id)
	return item

def get_element_class(soup, tag_id):
	item = soup.findAll("div", {"class": tag_id})
	return item

def get_articles(soup):
	items = soup.findAll('article')
	for item in items:
		print(item)
	return items

def recursive_divs(div_list):
	for d in div_list:
		if type(d) == bs4.element.Tag:
			recursive_divs(d)
		else:
			try:
				print(d.getText())
			except:
				pass

def get_score_box(soup):
	# retrieve all of the paragraph tags
	# items = soup.find('article').find("div", {'class': 'gameline-layout row ng-scope period-layout'})
	# soup.find_all('ul', {'class':"gameline-layout row ng-scope period-layout"})
	lis = soup.find_all('li')
	for l in lis:
		c = l.findChild()
		if c is not None:
			print(c.getText())
			if 'Warriors' in c.getText():
				pdb.set_trace()

	pdb.set_trace()


# URL = "https://sports.bovada.lv/basketball/nba/san-antonio-spurs-golden-state-warriors-201802102030"
# page = urllib2.urlopen(URL)
URL = "Phoenix Suns @ Golden State Warriors _ Bovada.html"
page = open(URL)
soup = BeautifulSoup(page, 'html.parser')

# time_box_all = soup.find_all('h2', attrs={'class', 'ng-binding'})
# for time_box in time_box_all:
# 	time = time_box.text
# 	print(time)

# time_box_all = soup.find_all('time', attrs={'class', 'ng-binding'})
# for time_box in time_box_all:
# 	time = time_box.text
# 	if 'Q' in time:
# 		print(time)

# team_box_all = soup.find_all('h3', attrs={'class', 'ng-binding'})
# for team_box in team_box_all:
# 	team = team_box.text
# 	print(team)

# score_box_all = soup.find_all('li', attrs={'class', 'ng-scope'})
# for score_box in score_box_all:
# 	score = score_box.text
# 	print(score)



game_box = soup.find_all('article', attrs={'class', 'gameline-layout'})
# pdb.set_trace()
# game = game_box[0] # looks at only the game lines
i  = 0
for game in game_box:
	print(i)
	i += 1
	# game.find_next('article')
	# which quarter?
	try:
		Q = game.find('h2', attrs={'class', 'marketline-period'}).getText()
		print(Q)
	except:
		print('could not find Quarter')

	# bet for the half
	GameTime = game.find('time', attrs={'class', 'ng-binding'}).getText()
	print(GameTime)
	# check for vertical line?
	# TODO: SAVE ADDITIONAL WEBPAGE EXAMPLES!

	# pdb.set_trace()
	# if 'period-layout' not in game.find_next('article').attrs['class']:
	# 	print('Main Game')

game_box[1].find_next('article')

pdb.set_trace()

for game in game_box:
	game_info = game.find_all('header', attrs={'class', 'gameline-even'})
	pdb.set_trace()
for game in game_box:
	g = game.text
	print(g)
