import requests, json

class owm():
	def __init__(self, appid):
		self.appid = appid

	def currentWeatherCity(self, query):
		link = 'http://api.openweathermap.org/data/2.5/find?q=%s&type=accurate&appid=%s&units=metric' % (query, self.appid)
		data = json.loads(requests.get(link).text)
		kembali = {}
		kembali['jumlah_kota'] = data['count']
		kembali['list'] = []
		for a in range(data['count']):
			isi = {}
			isi['nama'] = data['list'][a]['name']
			isi['koordinat'] = {}
			isi['koordinat']['lat'] = data['list'][a]['coord']['lat']
			isi['koordinat']['lng'] = data['list'][a]['coord']['lon']
			isi['result'] = {}
			isi['result']['cuaca'] = data['list'][a]['weather'][0]['description']
			isi['result']['temp'] = data['list'][a]['main']['temp']
			isi['result']['humidity'] = data['list'][a]['main']['humidity']
			kembali['list'].append(isi)
		return kembali

	def currentWeatherCoord(self, lat, lng):
		link = 'http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s&units=metric' % (lat, lng, self.appid)
		data = json.loads(requests.get(link).text)
		kembali = {}
		kembali['nama'] = data['name']
		kembali['negara'] = data['sys']['country']
		kembali['coord'] = {}
		kembali['coord']['lat'] = data['coord']['lat']
		kembali['coord']['lng'] = data['coord']['lon']
		kembali['result'] = {}
		kembali['result']['cuaca'] = data['weather'][0]['description']
		kembali['result']['temp'] = data['main']['temp']
		kembali['result']['humidity'] = data['main']['humidity']
		return kembali