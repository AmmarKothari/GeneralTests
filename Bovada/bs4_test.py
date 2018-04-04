import pdb
from bs4 import BeautifulSoup
import bs4
import urllib2


url = r"SPX Quote - S&P 500 Index - Bloomberg Markets.html"
page = open(url)
soup = BeautifulSoup(page.read(), 'html.parser')

# Take out the <div> of name and get its value
name_box = soup.find('h1', attrs={'class': 'name'})

name = name_box.text.strip() #strip is used to remove the starting and trailing blank spaces
print(name)
# links = soup.find_all('a')
# for l in links:
#     print(l.get_text())

price_box = soup.find('div', attrs={'class':'price'})
price = price_box.text
print price
