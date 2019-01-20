from pixivpy3 import *

class pixivapi:
	def __init__(self, username, password):
		self.api = PixivAPI()
		self.api.login(username, password)

	def search(self, query):
		data = self.api.search_works(query=query, page=1, per_page=10, mode='tag')
		image = []
		for a in data.response:
			image.append(a.image_urls.px_480mw)
		return image

	def ranking(self):
		data = self.api.ranking(page=1, per_page=10)
		image = []
		for a in data.response[0].works:
			image.append(a.work.image_urls.px_480mw.replace('http://', 'https://'))
		return image