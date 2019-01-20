import requests
from bs4 import BeautifulSoup

class MAL:
    def getTopAiring(self):
        try:
            link = 'https://myanimelist.net/'
            data = requests.get(link).text
            soup = BeautifulSoup(data, 'lxml')
            img = []
            judul = []
            link = []
            for a in soup.find_all('div', {'class':'ranking-digest'}):
                for b in a.find_all('h2', {'class':'ranking-header'}):
                    if b.text[4:] == 'Top Airing Anime':
                        for c in a.find_all('img'):
                            img.append(c['data-src'].replace('/r/50x70', ''))
                        for c in a.find_all('a', {'class':'title'}):
                            judul.append(c.text)
                            link.append(c['href'])
            return judul, link, img
        except Exception as e:
            raise e

    def getTopUpcoming(self):
        try:
            link = 'https://myanimelist.net/'
            data = requests.get(link).text
            soup = BeautifulSoup(data, 'lxml')
            img = []
            judul = []
            link = []
            for a in soup.find_all('div', {'class':'ranking-digest'}):
                for b in a.find_all('h2', {'class':'ranking-header'}):
                    if b.text[4:] == 'Top Upcoming Anime':
                        for c in a.find_all('img'):
                            img.append(c['data-src'].replace('/r/50x70', ''))
                        for c in a.find_all('a', {'class':'title'}):
                            judul.append(c.text)
                            link.append(c['href'])
            return judul, link, img
        except Exception as e:
            raise e
        

    def getMostPopular(self):
        try:
            link = 'https://myanimelist.net/'
            data = requests.get(link).text
            soup = BeautifulSoup(data, 'lxml')
            img = []
            judul = []
            link = []
            for a in soup.find_all('div', {'class':'ranking-digest'}):
                for b in a.find_all('h2', {'class':'ranking-header'}):
                    if b.text[4:] == 'Most Popular Anime':
                        for c in a.find_all('img'):
                            img.append(c['data-src'].replace('/r/50x70', ''))
                        for c in a.find_all('a', {'class':'title'}):
                            judul.append(c.text)
                            link.append(c['href'])
            return judul, link, img
        except Exception as e:
            raise e
        

    def detailAnime(self, link):
        try:
            kembali = {}
            data = requests.get(link).text
            soup = BeautifulSoup(data, 'lxml')
            kembali['judul'] = soup.find('span', {'itemprop':'name'}).text
            kembali['image'] = soup.find('img', {'class':'ac'})['src']
            kembali['score'] = soup.find('div', {'data-title':'score'}).text[9:-7]
            kembali['rank'] = soup.find('span', {'class':'numbers ranked'}).text
            kembali['popularity'] = soup.find('span', {'class':'numbers popularity'}).text
            kembali['description'] = soup.find('span', {'itemprop':'description'}).text
            return kembali
        except Exception as e:
            raise e

    def videoAnime(self, link):
        try:
            kembali = []
            ytid = []
            judul = []
            data = requests.get(link).text
            soup = BeautifulSoup(data, 'lxml')
            for a in soup.find_all('div', {'class':'video-list-outer po-r pv'}):
                text = a.find('a')['href']
                text = text[:text.find('?enablejsapi')]
                text = text.replace('embed/', 'watch?v=')
                judul.append(a.find('span', {'class':'title'}).text)
                kembali.append(text)
                ytid.append(text[text.find('?v=')+3:])
            return kembali, ytid, judul
        except Exception as e:
            raise e

    def searchAnime(self, query):
        try:
            query = requests.utils.requote_uri(query)
            link =  'https://myanimelist.net/search/all?q=%s' % (query)
            data = requests.get(link).text
            soup = BeautifulSoup(data, 'lxml')
            image = []
            judul = []
            link = []
            for a in soup.find_all('div', {'class':'list di-t w100'}):
                img = a.find('img')
                if '/anime/' in img['src']:
                    image.append(img['src'].replace('/r/100x140', ''))
                    judul.append(img['alt'])
                    link.append(a.find('a')['href'])
            return judul, link, image
        except Exception as e:
            raise e