import requests
from bs4 import BeautifulSoup
import re


# if __name__ == 'main':
    # re_obj = requests.get('https://movie.douban.com/subject/26580232/')
    # bs_obj = BeautifulSoup(re_obj.text.encode('utf8'),'html.parser')
    #
    # element = bs_obj.find('div',{})

page = requests.get('https://wallstreetcn.com/news/global')


# print(page.content)
soup = BeautifulSoup(page.content, 'html.parser')

# print(soup.prettify())
for tb in soup.find_all('a', class_='content',href = re.compile('articles')):
# for tb in soup.find_all('a', href = re.compile('lacie')):
    try:
        print(type(tb))
        print(tb)
        print(tb['href'])
        print(type(tb['href']))
        pp=requests.get('https://wallstreetcn.com/{}'.format(tb['href']))
        soup = BeautifulSoup(page.content, 'html.parser')
        aaa = soup.find('article', class_='article')
        print(aaa.get_text())
    except:
        pass
