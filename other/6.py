import requests
from bs4 import BeautifulSoup
import re

def get_link(url):

    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    link=[]
    for tb in soup.find_all('a', class_='content',href = re.compile('articles')):
            #
            #
            # print(tb)
            # print(tb['href'])
            link.append(tb['href'])
    return link

a=get_link('https://wallstreetcn.com/news/global')

for j,i in enumerate(a):
    print(j)
    page = requests.get('https://wallstreetcn.com{}'.format(i))
    soup = BeautifulSoup(page.content, 'html.parser')


    tb = soup.find('article', class_='article')

    print(tb.get_text())

