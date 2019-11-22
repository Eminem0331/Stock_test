import requests
from bs4 import BeautifulSoup

# if __name__ == 'main':
    # re_obj = requests.get('https://movie.douban.com/subject/26580232/')
    # bs_obj = BeautifulSoup(re_obj.text.encode('utf8'),'html.parser')
    #
    # element = bs_obj.find('div',{})

page = requests.get('https://wallstreetcn.com/articles/3518645')


# print(page.content)
soup = BeautifulSoup(page.content, 'html.parser')

# print(soup.prettify())

tb = soup.find('article', class_='article')

# print(tb)

print(tb.get_text())
# for link in tb.find_all('p'):
#
#     print(link)