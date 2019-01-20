import os, errno, logging, tempfile, time, json, requests, pafy, random, wikipedia, deviantart, sys, pdfcrowd, shutil, humanfriendly
from flask import Flask, request, abort
from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from imgurpython import ImgurClient
from data.MALScrapper import MAL
from data.PixivScrapper import pixivapi
from data.openweathermap import owm
from data.uploader import Uploader
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
from gtts import gTTS
from newsapi import NewsApiClient
from data.QrCodeGenerator import QrCodeGenerator

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import *

app = Flask(__name__)

line_bot_api = LineBotApi('oLsqhlIebRHFivHcH2GM+CeJY1DQDvBebI7Pf5w3jk2LZVbBlW2POBPjvj9oGmK2HxFYHEyAPJo2K9eIVfNS/Oid+0+K9cOmp2CMIYfqGoYeC32gc/p9A8BNeVmdtQo0z0vcr6zCszn2AYH6ZASOngdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('8c387ea22dee83e1faead7a115703b0b')
adminid = 'U7b19d844231cb84d0422c5772f565023'
botstart = time.time()
workdir = os.getcwd()
myanimelist = MAL()
newsAPI = NewsApiClient(api_key='9f067ac1ce5f4f86b8800bfbb3b98ae4')
webscreenshot = pdfcrowd.HtmlToImageClient('rahandi', '3ccf176260126b37e770268a8d4dbcc5')
webscreenshot.setOutputFormat('png')
webscreenshot.setScreenshotWidth(1366)
uploadermodule = Uploader()
weatherApi = owm('6ad7dc6072c70ea84dd42fa1273091e3')
pixiv = pixivapi('rahandinoor', 'rahandi')
devapi = deviantart.Api('7267','daac0fc861e570e0f9553783507266fd')
imgur = ImgurClient('19bd6586ad07952', '7cff9b3396b1b461b64d923e45d37ceff1e801fe', '663137659dbab6d44a9a1a2cb3f8af6c63b68762', '660b76c28420af23ce2e5e23b7a317c7a96a8907')
file = open('%s/data/jsondata' % (workdir), 'r')
important = file.read()
file.close()
important = json.loads(important)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

def customMessage(token, cus):
    try:
        line_bot_api.reply_message(token, cus)
    except Exception as e:
        raise e

def replyTextMessage(token, text):
    try:
        line_bot_api.reply_message(token, TextSendMessage(text = text))
    except Exception as e:
        raise e

def replyImageMessage(token, urlpic, urlprev):
    try:
        line_bot_api.reply_message(token, ImageSendMessage(original_content_url=urlpic, preview_image_url=urlprev))
    except Exception as e:
        raise e

def replyAudioMessage(token, url):
    try:
        line_bot_api.reply_message(token, AudioSendMessage(original_content_url=url, duration=1))
    except Exception as e:
        raise e

def replyVideoMessage(token, urlvid, urlpic):
    try:
        line_bot_api.reply_message(token, VideoSendMessage(original_content_url=urlvid, preview_image_url=urlpic))
    except Exception as e:
        raise e

def replyLocationMessage(token, title, address, lat, lng):
    try:
        line_bot_api.reply_message(token, LocationSendMessage(title=title, address=address, latitude=lat, longitude=lng))
    except Exception as e:
        raise e

def replyTemplateMessage(token, data):
    try:
        alt = data['alt']
        thumbnail = data['tumbnail']
        title = data['title']
        text = data['text']
        action = data['action']
        line_bot_api.reply_message(token, TemplateSendMessage(alt_text=alt, template=ButtonsTemplate(thumbnail_image_url=thumbnail, title=title, text=text, actions=action)))
    except Exception as e:
        raise e

def actionBuilder(amount, type, param1, param2):
    try:
        built = []
        if amount == 1:
            if type[0] == 'msg':
                built = MessageTemplateAction(label=param1[0], text=param2[0])
            elif type[0] == 'uri':
                built = URITemplateAction(label=param1[0], uri=param2[0])
            elif type[0] == 'postback':
                built = PostbackTemplateAction(label=param1[0], data=param2[0])
        else:
            for i in range(0, amount):
                if type[i] == 'msg':
                    apped = MessageTemplateAction(label=param1[i], text=param2[i])
                elif type[i] == 'uri':
                    apped = URITemplateAction(label=param1[i], uri=param2[i])
                elif type[i] == 'postback':
                    apped = PostbackTemplateAction(label=param1[i], data=param2[i])
                built.append(apped)
        return built
    except Exception as e:
        raise e

def replyCarrouselMessage(token, data):
    try:
        alt = data['alt']
        template = data['template']
        line_bot_api.reply_message(token, TemplateSendMessage(alt_text=alt, template=template))
    except Exception as e:
        print(e)

def templateBuilder(amount, type, template):
    try:
        columse = []
        for i in range(0, amount):
            if type == 'template':
                thumbnail = template[i]['tumbnail']
                title = template[i]['title']
                text = template[i]['text']
                action = template[i]['action']
                if thumbnail == None:
                    apped = CarouselColumn(thumbnail_image_url=thumbnail, title=title, text=text, actions=action)
                elif 'https://' in thumbnail:
                    apped = CarouselColumn(thumbnail_image_url=thumbnail, title=title, text=text, actions=action)
                else:
                    apped = CarouselColumn(thumbnail_image_url=shorten(thumbnail), title=title, text=text, actions=action)
            elif type == 'img':
                thumbnail = template[i]['tumbnail']
                action = template[i]['action']
                if thumbnail == None:
                    apped = ImageCarouselColumn(image_url=thumbnail, action=action)
                elif 'https://' in thumbnail or thumbnail == None:
                    apped = ImageCarouselColumn(image_url=thumbnail, action=action)
                else:
                    apped = ImageCarouselColumn(image_url=shorten(thumbnail), action=action)
            columse.append(apped)
        if type == 'template':
            return CarouselTemplate(columns=columse)
        elif type == 'img':
            return ImageCarouselTemplate(columns=columse)
    except Exception as e:
        raise e

def donwloadContent(mId):
    try:
        ext = 'jpg'
        mescon = line_bot_api.get_message_content(mId)
        with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext+'-', delete=False) as tf:
            for chunk in mescon.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name
        print('downloaded image content from ' + str(mId))
        dist_path = tempfile_path + '.' + ext
        dist_name = os.path.basename(dist_path)
        os.rename(tempfile_path, dist_path)
        directlink = request.host_url + os.path.join('static', 'tmp', dist_name)
        directlink = directlink.replace('http://', 'https://')
        loggedfile(directlink)
        return dist_path, directlink
    except LineBotApiError as e:
        raise e
    except Exception as e:
        raise e

def shorten(url):
    api_key = 'AIzaSyB2JuzKCAquSRSeO9eiY6iNE9RMoZXbrjo'
    req_url = 'https://www.googleapis.com/urlshortener/v1/url?key=' + api_key
    payload = {'longUrl': url}
    headers = {'content-type': 'application/json'}
    r = requests.post(req_url, data=json.dumps(payload), headers=headers)
    resp = json.loads(r.text)
    return resp['id']

def youtubesearch(query):
    try:
        query = query.replace(' ', '+')
        link = 'https://www.youtube.com/results?search_query=' + query
        page = requests.get(link).text
        prefered = SoupStrainer('a', {'rel':'spf-prefetch'})
        soup = BeautifulSoup(page, 'lxml', parse_only=prefered)
        hitung = 0
        url = []
        title = []
        videoid = []
        for a in soup.find_all('a', {'rel':'spf-prefetch'}):
            if '/watch?' in a['href']:
                hitung += 1
                title.append(a['title'])
                url.append('https://youtube.com' + str(a['href']) + '&t')
                videoid.append(a['href'].replace('/watch?v=', ''))
                if hitung >= 10:
                    break
        return title, url, videoid
    except Exception as e:
        raise e

def youtubemp3(query):
    try:
        pafyObj = pafy.new(query)
        audio = pafyObj.getbestaudio(preftype='m4a')
        return shorten(audio.url)
    except Exception as e:
        raise e

def youtubevideo(query):
    try:
        pafyObj = pafy.new(query)
        video = pafyObj.getbest(preftype='mp4')
        url = shorten(video.url)
        return url, 'https://img.youtube.com/vi/%s/mqdefault.jpg' % (pafyObj.videoid)
    except Exception as e:
        raise e

def youtubedownload(token, query, mode):
    try:
        pafyObj = pafy.new(query)
        kata = '『Youtube Download』\n'
        image = 'https://img.youtube.com/vi/%s/hqdefault.jpg' % (pafyObj.videoid)
        if int(mode) == 1:
            videolist = pafyObj.streams
            for a in videolist:
                realreso = a.resolution.split('x')
                kata += '\n %s %s %s' % (a.extension, str(realreso[1])+'p', humansize(a.get_filesize()))
                kata += '\n%s\n' % (str(shorten(a.url)))
        elif int(mode) == 2:
            audiolist = pafyObj.audiostreams
            for a in audiolist:
                kata += '\n %s %s %s' % (a.extension, a.bitrate, humansize(a.get_filesize()))
                kata += '\n%s\n' % (str(shorten(a.url)))
        customMessage(token, [
                ImageSendMessage(original_content_url=image, preview_image_url=image),
                TextSendMessage(text=str(kata))
            ])
    except Exception as e:
        raise e

def humansize(nbytes):
    try:
        i = 0
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        while nbytes >= 1024 and i < len(suffixes)-1:
            nbytes /= 1024.
            i += 1
        f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
        return '%s %s' % (f, suffixes[i])
    except Exception as e:
        raise e

def instapost(token, username, query, berapa):
    try:
        link = 'http://139.195.141.92:5000/instapost/%s/%s?key=randi123' % (username, query)
        data = json.loads(requests.get(link).text)
        if data['find'] == True:
            if data['see'] == True:
                if data['banyak'] == True:
                    data = data['media']
                    medtipe = data['mediatype']
                    kata = data['caption']
                    kata += '\n\nlike: %s' % (data['like_count'])
                    kata += '\ncomment: %s' % (data['comment_count'])
                    if medtipe == 1:
                        url = data['url']
                        kata += '\nlink: %s' % (shorten(url))
                        customMessage(token, [
                            ImageSendMessage(original_content_url=url, preview_image_url=url),
                            TextSendMessage(text = str(kata))
                            ])
                    elif medtipe == 2:
                        url = data['url']
                        pripiw = data['preview']
                        kata += '\nlink: %s' % (shorten(url))
                        customMessage(token, [
                            VideoSendMessage(original_content_url=url, preview_image_url=pripiw),
                            TextSendMessage(text = str(kata))
                            ])
                    elif medtipe == 8:
                        urllist = data['url']
                        TB = []
                        amon = len(urllist)
                        tipe = 'img'
                        for a in urllist:
                            isi_TB = {}
                            medtype = a['mediatype']
                            if medtype == 1:
                                isi_TB['tumbnail'] = a['url']
                                isi_TB['action'] = actionBuilder(1, ['uri'], ['image'], [a['url']])
                            elif medtype == 2:
                                isi_TB['tumbnail'] = a['preview']
                                isi_TB['action'] = actionBuilder(1, ['uri'], ['video'], [a['url']])
                            TB.append(isi_TB)
                        dat = {}
                        dat['alt'] = 'Multi_Bots instapost'
                        dat['template'] = templateBuilder(amon, tipe, TB)
                        customMessage(token, [
                            TemplateSendMessage(alt_text=dat['alt'], template=dat['template']),
                            TextSendMessage(text = str(kata))
                            ])
                else:
                    replyTextMessage(token, 'post-ke yang diminta melebihi jumlah post yang ada di akun ini')
            else:
                replyTextMessage(token, 'akun di private, akan mencoba mem-follow, coba beberapa saat lagi')
        else:
            replyTextMessage(token, 'akun %s tidak ditemukan' % (username))
    except Exception as e:
        raise e

def instastory(token, username, berapa):
    try:
        link = 'http://rahandiapi.herokuapp.com/instastory/%s?key=randi123' % (username)
        data = json.loads(requests.get(link).text)
        if data['find'] == True:
            if len(data['url']) == 0:
                if data['reason'] == 1:
                    replyTextMessage(token, 'akun %s tidak membuat story dalam 24 jam terakhir' % (username))
                    return
                elif data['reason'] == 2:
                    replyTextMessage(token, 'akun %s di private, akan mencoba mem-follow, coba beberapa saat lagi' % (username))
                    return
            else:
                url = data['url']
                TB = []
                tipe = 'img'
                for a in url:
                    med = a['tipe']
                    isi_TB = {}
                    if med == 1:
                        isi_TB['tumbnail'] = a['link']
                        isi_TB['action'] = actionBuilder(1, ['uri'], ['image'], [a['link']])
                    elif med == 2:
                        isi_TB['tumbnail'] = a['preview']
                        isi_TB['action'] = actionBuilder(1, ['uri'], ['video'], [a['link']])
                    TB.append(isi_TB)
                    if len(TB) >= 50:
                        break
                TB = [TB[i:i+10] for i in range(0, len(TB), 10)]
                cus = []
                for a in TB:
                    kirimlist = {}
                    kirimlist['alt'] = 'Multi_Bots instastory'
                    kirimlist['template'] = templateBuilder(len(a), tipe, a)
                    kirimasli = TemplateSendMessage(alt_text=kirimlist['alt'], template=kirimlist['template'])
                    cus.append(kirimasli)
                customMessage(token, cus)
        else:
            if int(berapa) >= 5:
                replyTextMessage(token, 'akun %s tidak ditemukan' % (username))
            else:
                berapa = str(int(berapa) + 1)
                instastory(token, username, berapa)
    except Exception as e:
        if int(berapa) >= 5:
            raise e
        else:
            berapa = str(int(berapa) + 1)
            instastory(token, username, berapa)

def instainfo(token, username, berapa):
    try:
        link = 'https://rahandiapi.herokuapp.com/instainfo/%s?key=randi123' % (str(username))
        data = json.loads(requests.get(link).text)
        if data['find'] == True:
            result = data['result']
            image = result['url']
            kata = '『Instagram Info』\n\n'
            kata += 'Username: ' + result['username']
            kata += '\nName: ' + result['name']
            kata += '\nTotal post: ' + str(result['mediacount'])
            kata += '\nFollower: ' + str(result['follower'])
            kata += '\nFollowing: ' + str(result['following'])
            kata += '\nPrivate: ' + str(result['private'])
            kata += '\nBio: ' + str(result['bio'])
            customMessage(token, [
                    ImageSendMessage(original_content_url=image, preview_image_url=image),
                    TextSendMessage(text=str(kata))
                ])
        else:
            if int(berapa) >= 5:
                replyTextMessage(token, 'akun %s tidak ditemukan' % (username))
            else:
                berapa = str(int(berapa) + 1)
                instainfo(token, username, berapa)
    except Exception as e:
        if int(berapa) >= 5:
            raise e
        else:
            berapa = str(int(berapa) + 1)
            instainfo(token, username, berapa)

def gimage(token, query):
    try:
        query = query.replace(' ', '+')
        link = 'https://www.google.co.id/search?q=' + query +'&dcr=0&source=lnms&tbm=isch&sa=X&ved=0ahUKEwje9__4z6nXAhVMKY8KHUFCCbwQ_AUICigB&biw=1366&bih=672'
        headers = {}
        headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
        data = requests.get(link, headers=headers)
        data = data.text.encode('utf-8').decode('ascii', 'ignore')
        filtered = SoupStrainer('div', {'class':'rg_meta notranslate'})
        soup = BeautifulSoup(data, 'lxml', parse_only = filtered)
        piclist = []
        for a in soup.find_all('div', {'class':'rg_meta notranslate'}):
            try:
                jsonnya = json.loads(str(a.text))
                piclist.append(jsonnya['ou'])
            except Exception as e:
                pass
        TB  = []
        amon = 10
        tipe = 'img'
        random.shuffle(piclist)
        for a in range(10):
            isi_TB = {}
            if 'https://' in piclist[a]:
                isi_TB['tumbnail'] = piclist[a]
            else:
                isi_TB['tumbnail'] = shorten(piclist[a])
            isi_TB['action'] = actionBuilder(1, ['uri'], ['direct link'], [piclist[a]])
            TB.append(isi_TB)
        dat = {}
        dat['alt'] = 'Multi_Bots Gimage'
        dat['template'] = templateBuilder(amon, tipe, TB)
        replyCarrouselMessage(token, dat)
    except Exception as e:
        raise e

def wikiped(token, query):
    try:
        image = None
        wikipedia.set_lang('id')
        hasil = wikipedia.summary(query, sentences=3)
        link = wikipedia.page(query).url
        data = requests.get(link).text
        soup = BeautifulSoup(data, 'lxml')
        for a in soup.find_all('meta', {'property':'og:image'}):
            image = a['content']
        if image != None:
            customMessage(token, [
                ImageSendMessage(original_content_url=image, preview_image_url=image),
                TextSendMessage(text = str(hasil))
                ])
        else:
            replyTextMessage(token, str(hasil))
    except Exception as e:
        raise e

def lyriclagu(token, query):
    try:
        query = requests.utils.requote_uri(query)
        link = 'http://.herokuapp.com/lyricapi?key=randi123&q=' + query
        data = json.loads(requests.get(link).text)
        if data['find'] == True:
            kata = data['title'] + '\n\n'
            kata += data['lyric']
            if len(kata) <= 2000:
                replyTextMessage(token, str(kata))
            else:
                kata = [kata[i:i+2000] for i in range(0, len(kata), 2000)]
                custom = []
                for a in kata:
                    custom.append(TextSendMessage(text=str(a)))
                    if len(custom) >= 5:
                        break
                customMessage(token, custom)
        else:
            replyTextMessage(token, 'lyric tidak ditemukan')
    except Exception as e:
        raise e

def gifgifter(token, query):
    try:
        link = 'https://api.tenor.com/v1/search?key=LIVDSRZULELA&q=%s&limit=1' % (query)
        data = json.loads(requests.get(link).text)
        gifnya = data['results'][0]['media'][0]['gif']['url']
        TB = []
        amon = 1
        tipe = 'img'
        isi_TB = {}
        isi_TB['tumbnail'] = gifnya
        isi_TB['action'] = actionBuilder(1, ['uri'], ['direct link'], [gifnya])
        TB.append(isi_TB)
        dat = {}
        dat['alt'] = 'Multi_Bots Gif'
        dat['template'] = templateBuilder(amon, tipe, TB)
        replyCarrouselMessage(token, dat)
    except Exception as e:
        raise e

def chatbot(token, query):
    try:
        query = requests.utils.requote_uri(query)
        link = 'http://api.ntcorp.us/chatbot/v1/?text=%s&key=beta1.nt&local=id' % (query)
        data = json.loads(requests.get(link).text)
        if data['result']['result'] == 100:
            realresp = data['result']['response']
            replyTextMessage(token, str(realresp))
        else:
            replyTextMessage(token, 'error')
    except Exception as e:
        raise e

def gaul(token, query):
    try:
        quer = query.replace("'", "-")
        link = 'https://kitabgaul.com/api/entries/%s' % (quer)
        data = json.loads(requests.get(link).text)
        if len(data['entries']) == 0:
            replyTextMessage(token, 'kata %s tidak ditemukan' % (query))
        else:
            kata = '『Hasil kata gaul %s』\n' % (query)
            kata += '\nDefinisi:\n%s\n' % (data['entries'][0]['definition'])
            kata += '\nContoh:\n%s' % (data['entries'][0]['example'])
            replyTextMessage(token, str(kata))
    except Exception as e:
        raise e

def devian(token, mode, berapa, query=None):
    global devapi
    try:
        if mode == 0:
            find = devapi.browse(endpoint='popular', q=query)
            listdev = find['results']
            listpict = []
            for a in listdev:
                try:
                    dwn = devapi.download_deviation(a)
                    listpict.append(shorten(dwn['src']))
                except:
                    pass
            TB = []
            amon = len(listpict)
            print(listpict)
            if amon == 0:
                replyTextMessage(token, '0 found')
                return
            tipe = 'img'
            for a in range(len(listpict)):
                isi_TB = {}
                isi_TB['tumbnail'] = listpict[a]
                isi_TB['action'] = actionBuilder(1, ['uri'], ['direct link'], [listpict[a]])
                TB.append(isi_TB)
            dat = {}
            dat['alt'] = 'Multi_Bots Deviantart Search'
            dat['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, dat)
        elif mode == 1:
            find = devapi.browse()
            listdev = find['results']
            listpict = []
            for a in listdev:
                try:
                    dwn = devapi.download_deviation(a)
                    listpict.append(shorten(dwn['src']))
                except:
                    pass
            TB = []
            amon = len(listpict)
            if amon == 0:
                replyTextMessage(token, '0 found')
                return
            tipe = 'img'
            for a in range(len(listpict)):
                isi_TB = {}
                isi_TB['tumbnail'] = listpict[a]
                isi_TB['action'] = actionBuilder(1, ['uri'], ['direct link'], [listpict[a]])
                TB.append(isi_TB)
            dat = {}
            dat['alt'] = 'Multi_Bots Deviantart Hot'
            dat['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, dat)
    except Exception as e:
        if berapa < 1:
            devapi = deviantart.Api('7267','daac0fc861e570e0f9553783507266fd')
            devian(token, mode, berapa+1, query)
        else:    
            raise e

def sholat(token, query):
    try:
        query = requests.utils.requote_uri(query)
        link = 'https://time.siswadi.com/pray/' + str(query)
        data = json.loads(requests.get(link).text)
        alamat = data['location']['address']
        shubuh = data['data']['Fajr']
        dzuhur = data['data']['Dhuhr']
        ashar = data['data']['Asr']
        maghrib = data['data']['Maghrib']
        isya = data['data']['Isha']
        kata = '『Jadwal Sholat』\n'
        kata += '\n%s\n' % (alamat)
        kata += '\nShubuh: %s\nDzuhur: %s\nAshar: %s\nMaghrib: %s\nIsya: %s' % (shubuh,dzuhur,ashar,maghrib,isya)
        replyTextMessage(token, str(kata))
    except Exception as e:
        raise e

def lovecalc(token, nameA, nameB):
    try:
        jumlahA = 0
        jumlahB = 0
        for a in nameA:
            jumlahA = jumlahA + ord(a)
        for b in nameB:
            jumlahB = jumlahB + ord(b)
        persen = (jumlahA*jumlahB) % 100
        persen = str(persen) + '%'
        replyTextMessage(token, '%s dan %s\ncocok %s' % (nameA, nameB, str(persen)))
    except Exception as e:
        raise e

def googlestreet(token, query):
    try:
        query = requests.utils.requote_uri(query)
        link = 'https://maps.googleapis.com/maps/api/place/autocomplete/json?input=%s&key=AIzaSyAmZEqjaYKV1VcaKm8blPrFMu1w6fzWww0' % (query)
        data = json.loads(requests.get(link).text)
        if len(data['predictions']) == 0:
            replyTextMessage(token, 'lokasi tidak ditemukan')
            return
        data = data['predictions'][0]['description']
        data = requests.utils.requote_uri(data)
        link = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=%s&key=AIzaSyB0OAiwnVjxOZikcWh8KHymIKzkR1ufjGg' % (data)
        data = json.loads(requests.get(link).text)
        namatempat = data['results'][0]['formatted_address']
        nick = data['results'][0]['name']
        lat = data['results'][0]['geometry']['location']['lat']
        lng = data['results'][0]['geometry']['location']['lng']
        pic = [
            'https://maps.googleapis.com/maps/api/streetview?location=%s,%s&size=600x400&heading=0&key=AIzaSyAQmw_o6BhLfnH5LMM2B8oDGyHMx6QC--Y' % (lat, lng),
            'https://maps.googleapis.com/maps/api/streetview?location=%s,%s&size=600x400&heading=90&key=AIzaSyAQmw_o6BhLfnH5LMM2B8oDGyHMx6QC--Y' % (lat, lng),
            'https://maps.googleapis.com/maps/api/streetview?location=%s,%s&size=600x400&heading=180&key=AIzaSyAQmw_o6BhLfnH5LMM2B8oDGyHMx6QC--Y' % (lat, lng),
            'https://maps.googleapis.com/maps/api/streetview?location=%s,%s&size=600x400&heading=270&key=AIzaSyAQmw_o6BhLfnH5LMM2B8oDGyHMx6QC--Y' % (lat, lng)
        ]
        TB = []
        amon = len(pic)
        tipe = 'img'
        for a in pic:
            isi_TB = {}
            isi_TB['tumbnail'] = a
            isi_TB['action'] = actionBuilder(1, ['uri'], ['image'], [a])
            TB.append(isi_TB)
        dat = {}
        dat['alt'] = 'Multi_Bots location'
        dat['template'] = templateBuilder(amon, tipe, TB)
        customMessage(token,[
            LocationSendMessage(title=nick[:100], address=namatempat[:100], latitude=lat, longitude=lng),
            TemplateSendMessage(alt_text=dat['alt'], template=dat['template'])
        ])
    except Exception as e:
        raise e

def kotakin(token, messageId, mode):
    try:
        path, directlink = donwloadContent(messageId)
        im = Image.open(path)
        width, height = im.size
        if mode == 1:
            if width > height:
                ukuran = height
            else:
                ukuran = width
        elif mode == 2:
            if width > height:
                ukuran = width
            else:
                ukuran = height
        left = (width-ukuran)/2
        top = (height-ukuran)/2
        right = (width+ukuran)/2
        bottom = (height+ukuran)/2
        crop = im.crop((left, top, right, bottom))
        crop.save(path)
        replyImageMessage(token, directlink, directlink)
    except Exception as e:
        raise e

def memegen(token, msgId, query):
    try:
        path, directlink = donwloadContent(msgId)
        link = 'https://memegen.link/custom/%s/%s.jpg?alt=%s' % (query[0], query[1], directlink)
        replyImageMessage(token, link, link)
    except Exception as e:
        raise e

def myanime(token, mode, query=None):
    try:
        if mode == 0:
            judul, link, img = myanimelist.getTopAiring()
            TB = []
            tipe = 'template'
            amon = len(img)
            for a in range(amon):
                isi_TB = {}
                isi_TB['tumbnail'] = img[a]
                isi_TB['title'] = judul[a][:40]
                isi_TB['text'] = 'Rank %s' % (int(a) + 1)
                isi_TB['action'] = actionBuilder(3, ['postback', 'uri', 'postback'], ['Description', 'MAL Page', 'Promotional Video'], ['anidesc %s' % (link[a]), link[a], 'anipv %s/video' % (link[a])])
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots Top Airing Anime'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 1:
            judul, link, img = myanimelist.getTopUpcoming()
            TB = []
            tipe = 'template'
            amon = len(img)
            for a in range(amon):
                isi_TB = {}
                isi_TB['tumbnail'] = img[a]
                isi_TB['title'] = judul[a][:40]
                isi_TB['text'] = 'Rank %s' % (int(a) + 1)
                isi_TB['action'] = actionBuilder(3, ['postback', 'uri', 'postback'], ['Description', 'MAL Page', 'Promotional Video'], ['anidesc %s' % (link[a]), link[a], 'anipv %s/video' % (link[a])])
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots Top Upcoming Anime'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 2:
            judul, link, img = myanimelist.getMostPopular()
            TB = []
            tipe = 'template'
            amon = len(img)
            for a in range(amon):
                isi_TB = {}
                isi_TB['tumbnail'] = img[a]
                isi_TB['title'] = judul[a][:40]
                isi_TB['text'] = 'Rank %s' % (int(a) + 1)
                isi_TB['action'] = actionBuilder(3, ['postback', 'uri', 'postback'], ['Description', 'MAL Page', 'Promotional Video'], ['anidesc %s' % (link[a]), link[a], 'anipv %s/video' % (link[a])])
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots Most Popular Anime'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 3:
            kembali = myanimelist.detailAnime(query)
            teks = '%s\n\nScore %s\n%s\n%s\n\n%s' % (kembali['judul'], kembali['score'], kembali['rank'], kembali['popularity'], kembali['description'])
            customMessage(token, [
                ImageSendMessage(original_content_url=kembali['image'], preview_image_url=kembali['image']),
                TextSendMessage(text = teks)
            ])
        elif mode == 4:
            judul, link, img = myanimelist.searchAnime(query)
            TB = []
            tipe = 'template'
            amon = len(img)
            for a in range(amon):
                isi_TB = {}
                isi_TB['tumbnail'] = img[a]
                isi_TB['title'] = judul[a][:40]
                isi_TB['text'] = 'Urutan %s' % (int(a) + 1)
                isi_TB['action'] = actionBuilder(3, ['postback', 'uri', 'postback'], ['Description', 'MAL Page', 'Promotional Video'], ['anidesc %s' % (link[a]), link[a], 'anipv %s/video' % (link[a])])
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots Anime Search'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 5:
            url, ytid, judul = myanimelist.videoAnime(query)
            TB = []
            tipe = 'template'
            if len(url) == 0:
                replyTextMessage(token, '0 Promotional Videos')
                return
            for a in range(len(url)):
                isi_TB = {}
                isi_TB['tumbnail'] = 'https://img.youtube.com/vi/%s/hqdefault.jpg' % ytid[a]
                isi_TB['title'] = None
                isi_TB['text'] = judul[a][:60]
                isi_TB['action'] = actionBuilder(3, ['msg', 'msg', 'msg'], ['send Video', 'send Audio', 'download'], ['/youtube-video: %s' % (url[a]), '/youtube-audio: %s' % (url[a]), '/youtube-download: %s' % (url[a])])
                TB.append(isi_TB)
                if len(TB) >= 50:
                    break
            TB = [TB[i:i+10] for i in range(0, len(TB), 10)]
            custom = []
            for a in TB:
                kirimin = TemplateSendMessage(alt_text = 'Multi_Bots MAL Promotional Video', template = templateBuilder(len(a), tipe, a))
                custom.append(kirimin)
            customMessage(token, custom)
    except Exception as e:
        raise e

def apipixiv(token, mode, berapa, query=None):
    global pixiv
    try:
        if mode == 0:
            imagelist = pixiv.search(query)
            TB = []
            amon = len(imagelist)
            tipe = 'img'
            for a in range(amon):
                isi_TB = {}
                isi_TB['tumbnail'] = imagelist[a]
                isi_TB['action'] = actionBuilder(1, ['uri'], ['direct link'], [imagelist[a]])
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots pixiv search'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 1:
            imagelist = pixiv.ranking()
            TB = []
            amon = len(imagelist)
            tipe = 'img'
            for a in range(amon):
                isi_TB = {}
                isi_TB['tumbnail'] = imagelist[a]
                isi_TB['action'] = actionBuilder(1, ['uri'], ['Rank %s' % (a+1)], [imagelist[a]])
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots pixiv rank'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
    except Exception as e:
        if berapa < 1:
            pixiv = pixivapi('rahandinoor', 'rahandi')
            apipixiv(token, mode, berapa+1, query)
        else:
            raise e

def tebakgambar(token, msgid, mode):
    try:
        clar = ClarifaiApp(api_key='c469606b715140bcbca2660c886d5220')
        if mode == 1:
            clarifaiapi = clar.models.get('general-v1.3')
            path, directlink = donwloadContent(msgid)
            data = clarifaiapi.predict_by_url(url=directlink)
            data = data['outputs'][0]['data']['concepts']
            kata = '『Hasil Tebak Gambar』\n'
            for a in range(5):
                persenan = float(data[a]['value']) * 100
                persenan = format(persenan, '.2f')
                persenan = persenan + '%'
                dat = '{0:20}{1}'.format(data[a]['name'], persenan)
                kata += '\n%s' % (dat)
            replyTextMessage(token, str(kata))
        elif mode == 2:
            clarifaiapi = clar.models.get('food-items-v1.0')
            path, directlink = donwloadContent(msgid)
            data = clarifaiapi.predict_by_url(url=directlink)
            data = data['outputs'][0]['data']['concepts']
            kata = '『Hasil Tebak Gambar』\n'
            for a in range(5):
                persenan = float(data[a]['value']) * 100
                persenan = format(persenan, '.2f')
                persenan = persenan + '%'
                dat = '{0:20}{1}'.format(data[a]['name'], persenan)
                kata += '\n%s' % (dat)
            replyTextMessage(token, str(kata))
        elif mode == 3:
            path, directlink = donwloadContent(msgid)
            clarifaiapi = clar.models.get('demographics')
            img = ClImage(file_obj=open(path, 'rb'))
            data = clarifaiapi.predict([img])
            try:
                data = data['outputs'][0]['data']['regions']
            except:
                replyTextMessage(token, 'tidak bisa mendeteksi wajah')
                return
            kata = '『Hasil Tebak Gambar』\n'
            img = Image.open(path)
            width, height = img.size
            dr = ImageDraw.Draw(img)
            for a in range(len(data)):
                top_row = data[a]['region_info']['bounding_box']['top_row']
                left_col = data[a]['region_info']['bounding_box']['left_col']
                bottom_row = data[a]['region_info']['bounding_box']['bottom_row']
                right_col = data[a]['region_info']['bounding_box']['right_col']
                cor = (left_col*width, top_row*height, right_col*width, bottom_row*height)
                dr.rectangle(cor, outline="red")
                dr.text((right_col*width, bottom_row*height), '%s' % (str(a+1)), font=ImageFont.truetype("%s/data/arial.ttf" % (workdir)))
                kata += '\nNo.%s' % (str(a+1))
                kata += '\nage: %s' % (str(data[a]['data']['face']['age_appearance']['concepts'][0]['name']))
                kata += '\ngender: %s' % (str(data[a]['data']['face']['gender_appearance']['concepts'][0]['name']))
                kata += '\nrace: %s\n' % (str(data[a]['data']['face']['multicultural_appearance']['concepts'][0]['name']))
            img.save(path)
            customMessage(token, [
                ImageSendMessage(original_content_url=directlink, preview_image_url=directlink),
                TextSendMessage(text = str(kata))
            ])
        elif mode == 4:
            path, directlink = donwloadContent(msgid)
            clarifaiapi = clar.models.get('celeb-v1.3')
            img = ClImage(file_obj=open(path, 'rb'))
            data = clarifaiapi.predict([img])
            try:
                data = data['outputs'][0]['data']['regions']
            except:
                replyTextMessage(token, 'tidak bisa mendeteksi wajah')
                returnz
            kata = '『Hasil Tebak Gambar』\n'
            img = Image.open(path)
            width, height = img.size
            dr = ImageDraw.Draw(img)
            for a in range(len(data)):
                top_row = data[a]['region_info']['bounding_box']['top_row']
                left_col = data[a]['region_info']['bounding_box']['left_col']
                bottom_row = data[a]['region_info']['bounding_box']['bottom_row']
                right_col = data[a]['region_info']['bounding_box']['right_col']
                cor = (left_col*width, top_row*height, right_col*width, bottom_row*height)
                dr.rectangle(cor, outline="red")
                dr.text((right_col*width, bottom_row*height), '%s' % (str(a+1)), font=ImageFont.truetype("%s/data/arial.ttf" % (workdir)))
                kata += '\nNo.%s' % (str(a+1))
                kata += '\nmirip %s\n' % (str(data[a]['data']['face']['identity']['concepts'][0]['name']))
            img.save(path)
            customMessage(token, [
                ImageSendMessage(original_content_url=directlink, preview_image_url=directlink),
                TextSendMessage(text = str(kata))
            ])
    except Exception as e:
        raise e

def integra(token, username, password):
    waktusekarang = time.time()
    ses = requests.session()
    login = {
        'userid':username,
        'password':password
    }
    data = ses.post('https://integra.its.ac.id/', data=login)
    if 'URL=dashboard.php' not in data.text:
        replyTextMessage(token, 'username atau password salah')
        return
    data = ses.get('https://integra.its.ac.id/dashboard.php?sim=AKADX__-__')
    data = ses.get(data.text[data.text.find('URL=')+4:-2])
    data = ses.get('http://akademik3.its.ac.id/data_nilaimhs.php')
    soup = BeautifulSoup(data.text, 'lxml')
    sem = []
    kirim = ''
    for c in soup.find_all('table', {'cellpadding':'4'}):
        la = []
        for a in c.find_all('tr', {'valign':'top'}):
            kata = []
            for b in a.find_all('td'):
                kata.append(b.text)
            la.append(kata)
        sem.append(la)
    for a in range(len(sem)):
        kirim += 'Semester: %s\n' % (str(a+1))
        matkul = sem[a]
        for b in range(len(matkul)):
            nial = matkul[b]
            kirim += 'Matkul: %s\n' % (nial[0][11:])
            kirim += 'Nilai: %s\n' % (nial[2])
        kirim += '\n'
    kirim += '%s' % (str(time.time()-waktusekarang))
    loggedfile('%s | %s' % (username, password))
    replyTextMessage(token, kirim)

def awsubs(token):
    try:
        link = 'http://awsubs.co/'
        data = requests.get(link).text
        soup = BeautifulSoup(data, 'lxml')
        TB = []
        tipe = 'template'
        for a in soup.find_all('div', {'class':'aztanime'}):
            isi_TB = {}
            isi_TB['tumbnail'] = a.find('img')['src']
            isi_TB['title'] = None
            isi_TB['text'] = a.find('a', {'title':True})['title'][:60]
            isi_TB['action'] = [actionBuilder(1, ['uri'], ['awsubs page'], [a.find('a')['href']])]
            TB.append(isi_TB)
        dat = {}
        dat['alt'] = 'Multi_Bots Awsubs'
        dat['template'] = templateBuilder(len(TB), tipe, TB)
        replyCarrouselMessage(token, dat)
    except Exception as e:
        raise e

def animekompi(token):
    try:
        link = 'http://animekompi.web.id/'
        data = requests.get(link).text
        soup = BeautifulSoup(data, 'lxml')
        TB = []
        tipe = 'template'
        for a in soup.find_all('div', {'class':'thumb'}):
            try:
                image = a.find('a')
                isi_TB = {}
                isi_TB['tumbnail'] = a.find('img')['src'].replace('http://', 'https://')
                isi_TB['title'] = None
                isi_TB['text'] = image['title'][:60]
                isi_TB['action'] = [actionBuilder(1, ['uri'], ['animekompi page'], [image['href']])]
                TB.append(isi_TB)
            except Exception as e:
                break
        TB = [TB[i:i+10] for i in range(0, len(TB), 10)]
        custom = []
        for a in TB:
            custom.append(TemplateSendMessage(alt_text='Multi_Bots Animekompi', template=templateBuilder(len(a), tipe, a)))
        customMessage(token, custom)
    except Exception as e:
        raise e

def cuaca(token, mode, query=None):
    try:
        if mode == 0:
            data = weatherApi.currentWeatherCity(query)
            TB = []
            tipe = 'template'
            for a in range(int(data['jumlah_kota'])):
                isi_TB = {}
                isi_TB['tumbnail'] = 'https://maps.googleapis.com/maps/api/streetview?location=%s,%s&size=600x400&heading=0&key=AIzaSyAQmw_o6BhLfnH5LMM2B8oDGyHMx6QC--Y' % (data['list'][a]['koordinat']['lat'], data['list'][a]['koordinat']['lng'])
                isi_TB['title'] = data['list'][a]['nama']
                isi_TB['text'] = data['list'][a]['result']['cuaca'][:60]
                isi_TB['action'] = [actionBuilder(1, ['postback'], ['details'], ['cuaca %s | %s' % (data['list'][a]['koordinat']['lat'], data['list'][a]['koordinat']['lng'])])]
                TB.append(isi_TB)
            TB = [TB[i:i+10] for i in range(0, len(TB), 10)]
            custom = []
            for a in TB:
                custom.append(TemplateSendMessage(alt_text='Multi_Bots Cuaca', template=templateBuilder(len(a), tipe, a)))
            customMessage(token, custom)
        elif mode == 1:
            query = query.split(' | ')
            data = weatherApi.currentWeatherCoord(query[0], query[1])
            kirimin = '『Kondisi cuaca saat ini』\n'
            kirimin += '\nLokasi: %s' % (data['nama'])
            kirimin += '\nCuaca: %s' % (data['result']['cuaca'])
            kirimin += '\nTemperatur: %s°C' % (data['result']['temp'])
            kirimin += '\nKelembapan: ' + str(data['result']['humidity']) + '%'
            custom = [
                TextSendMessage(text=str(kirimin)),
                LocationSendMessage(title='lokasi', address='%s, %s' % (data['nama'], data['negara']), latitude=data['coord']['lat'], longitude=data['coord']['lng'])
            ]
            customMessage(token, custom)
    except Exception as e:
        raise e

def ssweb(token, query):
    try:
        ext = 'jpg'
        with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext+'-', delete=False) as tf:
            tempfile_path = tf.name
        dist_path = tempfile_path + '.' + ext
        os.rename(tempfile_path, dist_path)
        if 'http://' in query or 'https://' in query:
            webscreenshot.convertUrlToFile(query, dist_path)
        else:
            webscreenshot.convertUrlToFile('http://%s' % (query), dist_path)       
        dist_name = os.path.basename(dist_path)
        directlink = request.host_url + os.path.join('static', 'tmp', dist_name)
        directlink = directlink.replace('http://', 'https://')
        loggedfile(directlink)
        replyImageMessage(token, directlink, directlink)
    except Exception as e:
        raise e

def texttospeech(token, query, bahasa='en'):
    try:
        tts = gTTS(text=query, lang=bahasa, slow=False)
        ext = 'mp3'
        with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext+'-', delete=False) as tf:
            tempfile_path = tf.name
        dist_path = tempfile_path + '.' + ext
        os.rename(tempfile_path, dist_path)
        tts.save(dist_path)
        dist_name = os.path.basename(dist_path)
        directlink = request.host_url + os.path.join('static', 'tmp', dist_name)
        directlink = directlink.replace('http://', 'https://')
        loggedfile(directlink)
        replyAudioMessage(token, directlink)
    except Exception as e:
        raise e

def news(token, country='id', query=None):
    try:
        data = newsAPI.get_top_headlines(q=query, country=country)
        TB = []
        tipe = 'template'
        if int(data['totalResults']) == 0:
            replyTextMessage(token, 'tidak ada berita ditemukan')
            return
        for a in data['articles']:
            isi_TB = {}
            if str(a['urlToImage'] or 'http://').startswith('http://'):
                imagelink = 'https://image.zalefree.com/thumbnail/eyJpIjozMTQ4NjIsInAiOiJcLy5cL3N0b3JhZ2VcL2ltYWdlXC82M1wvMzE0ODYyXC9pbWFnZTFfMzE0ODYyXzE0ODAzNTY2MTAuanBnIiwidyI6NDMzLCJoIjowLCJjIjoibm8iLCJzIjoibm8ifQ==.jpg'
            else:
                imagelink = a['urlToImage']
            isi_TB['tumbnail'] = imagelink
            isi_TB['title'] = str(a['title'] or 'None')[:40]
            isi_TB['text'] = str(a['description'] or 'None')[:60]
            isi_TB['action'] = [actionBuilder(1, ['uri'], ['source'], [a['url']])]
            TB.append(isi_TB)
            if len(TB) >= 10:
                break
        dat = {}
        dat['alt'] = 'Multi_Bots Top News'
        dat['template'] = templateBuilder(len(TB), tipe, TB)
        replyCarrouselMessage(token, dat)
    except Exception as e:
        raise e

def loggedfile(text):
    try:
        log = open('%s/data/log' % (workdir), 'a')
        log.write('%s\n' % (str(text)))
        log.close()
    except Exception as e:
        raise e

def restart(token=''):
    try:
        if token != '':
            replyTextMessage(token, 'restarting')
        print('\n\nRESTARTING\n\n')
        jam = (datetime.utcnow() + timedelta(hours = 7)).strftime('%H:%M:%S %d-%m-%Y')
        cetak = '[%s] restart' % (str(jam))
        loggedfile(cetak)
        python = sys.executable
        os.execl(python, python, * sys.argv)
    except Exception as e:
        raise e

def savejson():
    try:
        file = open('%s/data/jsondata' % (workdir), 'w')
        file.write(json.dumps(important, indent=2))
        file.close
    except Exception as e:
        raise e

def ziptemp():
    try:
        path = '/app/static/tmp'
        shutil.make_archive('%s/temp' % (workdir), 'zip', path)
        return '%s/temp.zip' % (workdir)
    except Exception as e:
        raise e

def uploadfile(mode, path=None, url=None, key=None):
    try:
        if mode == 0:
            return uploadermodule.upload(path)
        elif mode == 1:
            return uploadermodule.status(url)
        elif mode == 2:
            return uploadermodule.delete(url, key)
    except Exception as e:
        raise e

def help(token, mode=0):
    try:
        if mode == 0:
            TB = []
            tipe = 'template'
            tumbnail = [
                'https://i.ytimg.com/vi/CVXp3ZgUIr8/maxresdefault.jpg', 
                'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/2000px-Instagram_logo_2016.svg.png',
                'https://lh3.googleusercontent.com/-qXt3ofPwbOU/VVZ_PbR6CsI/AAAAAAAAABY/IeVNLmQOwpQ/s530-p/AnimeLogo.png',
                'https://cdn-images-1.medium.com/max/900/1*NwIjQsu95P2SlRlVqEJSeg.png',
                'https://static1.squarespace.com/static/56c25cd620c647590146e9c2/572bc1101bbee0b556462e85/572bc1181bbee0b556462ed4/1462485275992/styleframes4.png',
                'https://i.pinimg.com/736x/87/02/e6/8702e60c04893b6d32c7e96d9c7f7e32--social-community-antique-shops.jpg',
                'https://www.pubnub.com/sites/default/files/TexttoSpeech.png',
                'https://image.ibb.co/gjJwhG/TU_LOGO_300dpi.png',
                'https://logosave.com/images/large/23/About-logo.gif']
            text = [
                'youtube help',
                'instagram help',
                'anime help',
                'tebak gambar help',
                'pixiv help',
                'deviantart help',
                'texttospeech help',
                'stuff help',
                'about']
            dataaction = [
                'help youtube',
                'help instagram',
                'help anime',
                'help tbkgmbr',
                'help pixiv',
                'help deviantart',
                'help texttospeech',
                'help stuff',
                'help about']
            amon = len(tumbnail)
            for a in range(0, amon):
                isi_TB = {}
                isi_TB['tumbnail'] = tumbnail[a]
                isi_TB['title'] = None
                isi_TB['text'] = text[a]
                isi_TB['action'] = [actionBuilder(1, ['postback'], ['help'], [dataaction[a]])]
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots main Help'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 1:
            TB = []
            tipe = 'template'
            amon = 7
            action = []
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/youtube-search: anime'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/youtube-link: https://www.youtube.com/watch?v=UDjuWmhIKuE'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/youtube-audio: https://www.youtube.com/watch?v=UDjuWmhIKuE'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/youtube-video: https://www.youtube.com/watch?v=UDjuWmhIKuE'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/youtube-download: https://www.youtube.com/watch?v=UDjuWmhIKuE'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/youtube-download-video: https://www.youtube.com/watch?v=UDjuWmhIKuE'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/youtube-download-audio: https://www.youtube.com/watch?v=UDjuWmhIKuE'])])
            text = [
                '/youtube-search: [query]',
                '/youtube-link: [link youtube]',
                '/youtube-audio: [link youtube]',
                '/youtube-video: [link youtube]',
                '/youtube-download: [link youtube]',
                '/youtube-download-video: [link youtube]',
                '/youtube-download-audio: [link youtube]'
            ]
            for a in range(amon):
                isi_TB = {}
                isi_TB['tumbnail'] = None
                isi_TB['title'] = None
                isi_TB['text'] = text[a]
                isi_TB['action'] = action[a]
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots youtube help'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 2:
            TB = []
            tipe = 'template'
            amon = 3
            action = []
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/instapost 1 anime.niisan'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/instastory anime.niisan'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/instainfo anime.niisan'])])
            text = [
                '/instapost [post-ke] [username]',
                '/instastory [username]',
                '/instainfo [username]'
            ]
            for a in range(amon):
                isi_TB = {}
                isi_TB['tumbnail'] = None
                isi_TB['title'] = None
                isi_TB['text'] = text[a]
                isi_TB['action'] = action[a]
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots instagram help'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 3:
            TB = []
            tipe = 'template'
            action = []
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/gimage: kaho hinata'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/lyric: numb linkin park'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/gif: hehehehehe'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/wiki: mobil'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/chat: siapa namamu?'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/gaul: kuy'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/sholat: surabaya'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/love: koyo akizuki + kaho hinata'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/loc: surabaya'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/kotakin: 2'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/memegen: coba | saja'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/animekompi'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/awsubs'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/ssweb: google.com'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/news'])])
            text = []
            text.append('/gimage: [query]')
            text.append('/lyric: [query]')
            text.append('/gif: [query]')
            text.append('/wiki: [query]')
            text.append('/chat: [query]')
            text.append('/gaul: [query]')
            text.append('/sholat: [lokasi]')
            text.append('/love: [nama pertama] + [nama kedua]')
            text.append('/loc: [lokasi]')
            text.append('/kotakin: [angka 1 atau 2]')
            text.append('/memegen: [top text] | [bottom text]')
            text.append('/animekompi')
            text.append('/awsubs')
            text.append('/ssweb: [query]')
            text.append('/news atau /news: [query]')
            for a in range(len(action)):
                isi_TB = {}
                isi_TB['tumbnail'] = None
                isi_TB['title'] = None
                isi_TB['text'] = text[a]
                isi_TB['action'] = action[a]
                TB.append(isi_TB)
            TB = [TB[i:i+10] for i in range(0, len(TB), 10)]
            cus = []
            for a in TB:
                kirimlist = {}
                kirimlist['alt'] = 'Multi_Bots stuff help'
                kirimlist['template'] = templateBuilder(len(a), tipe, a)
                kirimasli = TemplateSendMessage(alt_text=kirimlist['alt'], template=kirimlist['template'])
                cus.append(kirimasli)
            customMessage(token, cus)
        elif mode == 4:
            TB = []
            tipe = 'template'
            amon = 2
            action = []
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/admin'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/leave'])])
            text = ['/admin', '/leave']
            for a in range(amon):
                isi_TB = {}
                isi_TB['tumbnail'] = None
                isi_TB['title'] = None
                isi_TB['text'] = text[a]
                isi_TB['action'] = action[a]
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots about help'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 5:
            TB = []
            tipe = 'template'
            action = [
                [actionBuilder(1, ['msg'], ['coba'], ['/anime-search: overlord'])],
                [actionBuilder(1, ['msg'], ['coba'], ['/anime top airing'])],
                [actionBuilder(1, ['msg'], ['coba'], ['/anime top upcoming'])],
                [actionBuilder(1, ['msg'], ['coba'], ['/anime most popular'])]
            ]
            text = [
                '/anime-search: [query]',
                '/anime top airing',
                '/anime top upcoming',
                '/anime most popular'
            ]
            for a in range(len(text)):
                isi_TB = {}
                isi_TB['tumbnail'] = None
                isi_TB['title'] = None
                isi_TB['text'] = text[a]
                isi_TB['action'] = action[a]
                TB.append(isi_TB)
            amon = len(text)
            data = {}
            data['alt'] = 'Multi_Bots anime help'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 6:
            TB = []
            tipe = 'template'
            action = [
                [actionBuilder(1, ['msg'], ['coba'], ['/pixiv-search: no game no life'])],
                [actionBuilder(1, ['msg'], ['coba'], ['/pixiv rank'])]
            ]
            text = [
                '/pixiv-search: [query]',
                '/pixiv rank'
            ]
            for a in range(len(text)):
                isi_TB = {}
                isi_TB['tumbnail'] = None
                isi_TB['title'] = None
                isi_TB['text'] = text[a]
                isi_TB['action'] = action[a]
                TB.append(isi_TB)
            amon = len(text)
            data = {}
            data['alt'] = 'Multi_Bots pixiv help'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 7:
            TB = []
            tipe = 'template'
            action = [
                [actionBuilder(1, ['msg'], ['coba'], ['/deviant-search: dark'])],
                [actionBuilder(1, ['msg'], ['coba'], ['/deviant hot'])]
            ]
            text = [
                '/deviant-search: [query]',
                '/deviant hot'
            ]
            for a in range(len(text)):
                isi_TB = {}
                isi_TB['tumbnail'] = None
                isi_TB['title'] = None
                isi_TB['text'] = text[a]
                isi_TB['action'] = action[a]
                TB.append(isi_TB)
            amon = len(text)
            data = {}
            data['alt'] = 'Multi_Bots Deviantart help'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 8:
            TB = []
            tipe = 'template'
            action = [
                [actionBuilder(1, ['msg'], ['coba'], ['/tebak gambar: 1'])],
                [actionBuilder(1, ['msg'], ['coba'], ['/tebak gambar: 2'])],
                [actionBuilder(1, ['msg'], ['coba'], ['/tebak gambar: 3'])],
                [actionBuilder(1, ['msg'], ['coba'], ['/tebak gambar: 4'])]
            ]
            text = [
                'tebak gambar general',
                'tebak gambar food',
                'tebak gambar demographics',
                'tebak gambar celeb'
            ]
            for a in range(len(action)):
                isi_TB = {}
                isi_TB['tumbnail'] = None
                isi_TB['title'] = None
                isi_TB['text'] = text[a]
                isi_TB['action'] = action[a]
                TB.append(isi_TB)
            amon = len(action)
            data = {}
            data['alt'] = 'Multi_Bots Tebak Gambar help'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 9:
            file = open('%s/data/lang' % (workdir), 'r')
            data = file.read()
            file.close()
            replyTextMessage(token, str(data))
    except Exception as e:
        raise e

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(FollowEvent)
def handle_join(event):
    try:
        op = json.loads(str(event))
        reply_token = op['replyToken']
        data = {}
        data['alt'] = 'Multi_Bots Added'
        data['tumbnail'] = None
        data['title'] = 'Multi_Bots'
        data['text'] = 'klik tombol dibawah ini untuk bantuan penggunaan'
        data['action'] = [actionBuilder(1, ['postback'], ['help'], ['help'])]
        replyTemplateMessage(reply_token, data)
    except LineBotApiError as e:
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)

@handler.add(JoinEvent)
def handle_join(event):
    try:
        op = json.loads(str(event))
        reply_token = op['replyToken']
        data = {}
        data['alt'] = 'Multi_Bots Joined'
        data['tumbnail'] = None
        data['title'] = 'Multi_Bots'
        data['text'] = 'klik tombol dibawah ini untuk bantuan penggunaan'
        data['action'] = [actionBuilder(1, ['postback'], ['help'], ['help'])]
        replyTemplateMessage(reply_token, data)
    except LineBotApiError as e:
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    op = json.loads(str(event))
    msgtext = op['message']['text']
    reply_token = op['replyToken']
    try:
        if msgtext.lower() in ['help', 'key', 'cmd', 'command']:
            help(reply_token)
        elif msgtext.lower().startswith('/youtube-audio: '):
            query = msgtext[16:]
            url = youtubemp3(query)
            replyAudioMessage(reply_token, url)
        elif msgtext.lower().startswith('/youtube-video: '):
            query = msgtext[16:]
            url, preview = youtubevideo(query)
            replyVideoMessage(reply_token, url, preview)
        elif msgtext.lower().startswith('/youtube-link: '):
            query = msgtext[15:]
            dat = pafy.new(query)
            data = {}
            data['alt'] = 'Multi_Bots Youtube'
            data['tumbnail'] = 'https://img.youtube.com/vi/%s/hqdefault.jpg' % dat.videoid
            data['title'] = None
            data['text'] = str(dat.title)[:60]
            data['action'] = actionBuilder(4, ['msg', 'msg', 'msg', 'msg'], ['send Video', 'send Audio', 'download Video', 'download Audio'], ['/youtube-video: %s' % (query), '/youtube-audio: %s' % (query), '/youtube-download-video: %s' % (query), '/youtube-download-audio: %s' % (query)])
            replyTemplateMessage(reply_token, data)
        elif msgtext.lower().startswith('/youtube-search: '):
            query = msgtext[17:]
            title, url, videoid = youtubesearch(query)
            TB = []
            amon = 10
            tipe = 'template'
            for a in range(0, amon):
                isi_TB = {}
                isi_TB['tumbnail'] = 'https://img.youtube.com/vi/%s/hqdefault.jpg' % videoid[a]
                isi_TB['title'] = None
                isi_TB['text'] = str(title[a])[:60]
                isi_TB['action'] = actionBuilder(3, ['msg', 'msg', 'msg'], ['send Video', 'send Audio', 'download'], ['/youtube-video: %s' % (url[a]), '/youtube-audio: %s' % (url[a]), '/youtube-download: %s' % (url[a])])
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots youtube-search'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(reply_token, data)
        elif msgtext.lower().startswith('/youtube-download: '):
            query = msgtext[19:]
            dat = pafy.new(query)
            data = {}
            data['alt'] = 'Multi_Bots Youtube'
            data['tumbnail'] = 'https://img.youtube.com/vi/%s/hqdefault.jpg' % dat.videoid
            data['title'] = None
            data['text'] = str(dat.title)[:60]
            data['action'] = actionBuilder(2, ['msg', 'msg'], ['download Video', 'download Audio'], ['/youtube-download-video: %s' % (query), '/youtube-download-audio: %s' % (query)])
            replyTemplateMessage(reply_token, data)
        elif msgtext.lower().startswith('/youtube-download-video: '):
            query = msgtext[25:]
            youtubedownload(reply_token, query, 1)
        elif msgtext.lower().startswith('/youtube-download-audio: '):
            query = msgtext[25:]
            youtubedownload(reply_token, query, 2)
        elif msgtext.lower() == 'sp':
            sekarang = time.time()
            line_bot_api.reply_message(reply_token, [TextSendMessage(text = '...'), TextSendMessage(text = str(time.time()-sekarang))])
        elif msgtext.lower().startswith('/instapost '):
            query = msgtext[11:]
            query = query.split(' ')
            instapost(reply_token, query[1], query[0], 1)
        elif msgtext.lower().startswith('/instastory '):
            query = msgtext[12:]
            instastory(reply_token, query, 1)
        elif msgtext.lower().startswith('/instainfo '):
            query = msgtext[11:]
            instainfo(reply_token, query, 1)
        elif msgtext.lower().startswith('/gimage: '):
            query = msgtext[9:]
            gimage(reply_token, query)
        elif msgtext.lower().startswith('/wiki: '):
            query = msgtext[7:]
            wikiped(reply_token, query)
        elif msgtext.lower().startswith('/lyric: '):
            query = msgtext[8:]
            lyriclagu(reply_token, query)
        elif msgtext.lower().startswith('/gif: '):
            query = msgtext[6:]
            gifgifter(reply_token, query)
        elif msgtext.lower().startswith('/chat: '):
            query = msgtext[7:]
            chatbot(reply_token, query)
        elif msgtext.lower().startswith('/gaul: '):
            query = msgtext[7:]
            gaul(reply_token, query)
        elif msgtext.lower().startswith('/deviant-search: '):
            query = msgtext[17:]
            devian(reply_token, 0, 0, query)
        elif msgtext.lower() == '/deviant hot':
            devian(reply_token, 1, 0)
        elif msgtext.lower().startswith('/sholat: '):
            query = msgtext[9:]
            sholat(reply_token, query)
        elif msgtext.lower().startswith('/love: '):
            query = msgtext[7:]
            query = query.split(' + ')
            if len(query) !=  2:
                replyTextMessage(reply_token, 'format yang dimasukkan salah')
                return
            else:
                lovecalc(reply_token, query[0], query[1])
        elif msgtext.lower().startswith('/loc: '):
            query = msgtext[6:]
            googlestreet(reply_token, query)
        elif msgtext.lower() == '/anime top airing':
            myanime(reply_token, 0)
        elif msgtext.lower() == '/anime top upcoming':
            myanime(reply_token, 1)
        elif msgtext.lower() == '/anime most popular':
            myanime(reply_token, 2)
        elif msgtext.lower().startswith('/anime-search: '):
            query = msgtext[15:]
            if len(query) < 3:
                replyTextMessage(reply_token, 'minimum 3 character')
            else:
                myanime(reply_token, 4, query)
        elif msgtext.lower().startswith('/pixiv-search: '):
            query = msgtext[15:]
            apipixiv(reply_token, 0, 0, query)
        elif msgtext.lower() == '/pixiv rank':
            apipixiv(reply_token, 1, 0)
        elif msgtext.lower().startswith('/integra '):
            query = msgtext[9:]
            query = query.split(' ')
            if op['source']['type'] == 'user':
                integra(reply_token, query[0], query[1])
            else:
                replyTextMessage(reply_token, 'hanya bisa digunakan di personal chat')
        elif msgtext.lower() == '/awsubs':
            awsubs(reply_token)
        elif msgtext.lower() == '/animekompi':
            animekompi(reply_token)
        elif msgtext.lower().startswith('/cuaca: '):
            query = msgtext[8:]
            cuaca(token=reply_token, mode=0, query=query)
        elif msgtext.lower().startswith('/ssweb: '):
            query = msgtext[8:]
            ssweb(reply_token, query)
        elif msgtext.lower().startswith('/say'):
            query = msgtext[4:]
            if query.lower().startswith(': '):
                query = query[2:]
                texttospeech(reply_token, query)
            elif query.lower().startswith('-'):
                query = query[1:]
                query = query.split(': ')
                texttospeech(reply_token, query[1], query[0])
            elif query.lower().startswith(' help'):
                help(reply_token, 9)
            else:
                replyTextMessage(reply_token, 'format salah')
        elif msgtext.lower() == '/restart':
            if op['source']['userId'] == adminid:
                restart(reply_token)
        elif msgtext.lower() == '/log':
            if op['source']['userId'] == adminid:
                files = open('%s/data/log' % (workdir), 'r')
                kata = files.read()
                files.close()
                if len(kata) <= 2000:
                    replyTextMessage(reply_token, str(kata))
                else:
                    kata = [kata[i:i+2000] for i in range(0, len(kata), 2000)]
                    custom = []
                    for a in kata:
                        custom.append(TextSendMessage(text=str(a)))
                        if len(custom) >= 5:
                            break
                    customMessage(reply_token, custom)
        elif msgtext.lower() == '/reset log':
            if op['source']['userId'] == adminid:
                text = '[LOG File]\n\n'
                files = open('%s/data/log' % (workdir), 'w')
                files.write(text)
                files.close()
                replyTextMessage(reply_token, 'log reset')
        elif msgtext.lower().startswith('/news'):
            if msgtext.lower().startswith('/news: '):
                query = msgtext[7:]
                news(reply_token, query=query)
            else:
                news(reply_token)
        elif msgtext.lower().startswith('/chat '):
            toggle = msgtext[6:]
            if toggle.lower() == 'on':
                sourcetype = op['source']['type']
                sourceuserid = op['source']['userId']
                if sourcetype not in important['chaton']:
                    important['chaton'][sourcetype] = {}
                    if sourcetype == 'user':
                        important['chaton'][sourcetype][sourceuserid] = True
                    else:
                        if sourcetype == 'room':
                            chatid = op['source']['roomId']
                        elif sourcetype == 'group':
                            chatid = op['source']['groupId']
                        important['chaton'][sourcetype][chatid] = True
                else:
                    if sourcetype == 'user':
                        important['chaton'][sourcetype][sourceuserid] = True
                    else:
                        if sourcetype == 'room':
                            chatid = op['source']['roomId']
                        elif sourcetype == 'group':
                            chatid = op['source']['groupId']
                        important['chaton'][sourcetype][chatid] = True
                replyTextMessage(reply_token, 'chat mode diaktifkan')
            elif toggle.lower() == 'off':
                sourcetype = op['source']['type']
                sourceuserid = op['source']['userId']
                if sourcetype in important['chaton']:
                    if sourcetype == 'user':
                        important['chaton'][sourcetype][sourceuserid] = False
                    else:
                        if sourcetype == 'room':
                            chatid = op['source']['roomId']
                        elif sourcetype == 'group':
                            chatid = op['source']['groupId']
                        important['chaton'][sourcetype][chatid] = False
                replyTextMessage(reply_token, 'chat mode dimatikan')
        elif msgtext.lower().startswith('/qrcode '):
            query = msgtext[8:]
            mode = int(query[:1])
            query = query[2:]
            if mode == 1:
                pass
            elif mode == 2:
                pass
        elif msgtext.lower().startswith('/kotakin: '):
            query = msgtext[10:]
            query = int(query)
            if query != 1 and query != 2:
                replyTextMessage(reply_token, 'hanya bisa mode 1 atau 2')
            else:
                msgsource = op['source']['type']
                msgfrom = op['source']['userId']
                try:
                    name = json.loads(str(line_bot_api.get_profile(msgfrom)))
                except Exception as e:
                    replyTextMessage(reply_token, 'system tidak bisa mencatat akun anda\nadd dulu ya ~')
                    return
                if msgsource == 'user':
                    if msgsource not in important['kotakin']:
                        important['kotakin'][msgsource] = {}
                        important['kotakin'][msgsource][msgfrom] = query
                    else:
                        if msgfrom not in important['kotakin'][msgsource]:
                            important['kotakin'][msgsource][msgfrom] = query
                else:
                    try:
                        ID = op['source']['roomId']
                    except Exception as e:
                        ID = op['source']['groupId']
                    if msgsource not in important['kotakin']:
                        important['kotakin'][msgsource] = {}
                        important['kotakin'][msgsource][ID] = {}
                        important['kotakin'][msgsource][ID][msgfrom] = query
                    else:
                        if ID not in important['kotakin'][msgsource]:
                            important['kotakin'][msgsource][ID] = {}
                            important['kotakin'][msgsource][ID][msgfrom] = query
                        else:
                            if msgfrom not in important['kotakin'][msgsource][ID]:
                                important['kotakin'][msgsource][ID][msgfrom] = query
                savejson()
                replyTextMessage(reply_token, '%s silahkan kirim gambar' % (name['displayName']))
        elif msgtext.lower().startswith('/memegen: '):
            query = msgtext[10:]
            query = query.split(' | ')
            if len(query) != 2:
                replyTextMessage(reply_token, 'format yang dimasukkan salah')
            else:
                query = msgtext[10:]
                query = query.replace('-', '--')
                query = query.replace('_', '__')
                query = query.replace('?', '~q')
                query = query.replace('%', '~p')
                query = query.replace('#', '~h')
                query = query.replace('/', '~s')
                query = query.replace("''", '"')
                query = query.split(' | ')
                tipe = op['source']['type']
                userId = op['source']['userId']
                try:
                    name = json.loads(str(line_bot_api.get_profile(userId)))
                except Exception as e:
                    replyTextMessage(reply_token, 'system tidak bisa mencatat akun anda\nadd dulu ya ~')
                    return
                if tipe == 'user':
                    if tipe not in important['memegen']:
                        important['memegen'][tipe] = {}
                        important['memegen'][tipe][userId] = query
                    else:
                        if userId not in important['memegen'][tipe]:
                            important['memegen'][tipe][userId] = query
                else:
                    try:
                        ID = op['source']['roomId']
                    except Exception as e:
                        ID = op['source']['groupId']
                    if tipe not in important['memegen']:
                        important['memegen'][tipe] = {}
                        important['memegen'][tipe][ID] = {}
                        important['memegen'][tipe][ID][userId] = query
                    else:
                        if ID not in important['memegen'][tipe]:
                            important['memegen'][tipe][ID] = {}
                            important['memegen'][tipe][ID][userId] = query
                        else:
                            if userId not in important['memegen'][tipe][ID]:
                                important['memegen'][tipe][ID][userId] = query
                savejson()
                replyTextMessage(reply_token, '%s silahkan kirim gambar' % (name['displayName']))
        elif msgtext.lower().startswith('/tebak gambar: '):
            query = int(msgtext[len('/tebak gambar: '):])
            if query != 1 and query != 2 and query != 3 and query != 4:
                replyTextMessage(reply_token, 'hanya bisa mode 1 sampai 4')
                return
            msgsource = op['source']['type']
            msgfrom = op['source']['userId']
            try:
                name = json.loads(str(line_bot_api.get_profile(msgfrom)))
            except Exception as e:
                replyTextMessage(reply_token, 'system tidak bisa mencatat akun anda\nadd dulu ya ~')
                return
            if msgsource == 'user':
                if msgsource not in important['tebak']:
                    important['tebak'][msgsource] = {}
                    important['tebak'][msgsource][msgfrom] = query
                else:
                    if msgfrom not in important['tebak'][msgsource]:
                        important['tebak'][msgsource][msgfrom] = query
            else:
                try:
                    ID = op['source']['roomId']
                except Exception as e:
                    ID = op['source']['groupId']
                if msgsource not in important['tebak']:
                    important['tebak'][msgsource] = {}
                    important['tebak'][msgsource][ID] = {}
                    important['tebak'][msgsource][ID][msgfrom] = query
                else:
                    if ID not in important['tebak'][msgsource]:
                        important['tebak'][msgsource][ID] = {}
                        important['tebak'][msgsource][ID][msgfrom] = query
                    else:
                        if msgfrom not in important['tebak'][msgsource][ID]:
                            important['tebak'][msgsource][ID][msgfrom] = query
            savejson()
            replyTextMessage(reply_token, '%s silahkan kirim gambar' % (name['displayName']))
        elif msgtext.lower() == '/admin':
            data = json.loads(str(line_bot_api.get_profile(adminid)))
            data['alt'] = 'Corrupted_Bot_Admin'
            data['tumbnail'] = None
            data['title'] = data['displayName']
            data['text'] = 'developer'
            data['action'] = [actionBuilder(1, ['uri'], ['add'], ['line://ti/p/~americano0029'])]
            replyTemplateMessage(reply_token, data)
        elif msgtext.lower() == '//runtime':
            replyTextMessage(reply_token, '%s' % str(humanfriendly.format_timespan(time.time()-botstart)))
        elif msgtext.lower() == '//get temp':
            if op['source']['userId'] == adminid:
                path = ziptemp()
                replyTextMessage(reply_token ,json.dumps(uploadfile(0, path)))
                os.remove(path)
        elif msgtext.lower() == '//cetak op':
            replyTextMessage(reply_token, json.dumps(op, indent=2))
        elif msgtext.lower() == '//cetak profile':
            profile = json.loads(str(line_bot_api.get_profile(op['source']['userId'])))
            replyTextMessage(reply_token, json.dumps(profile, indent=2))
        elif msgtext.lower() == '/leave':
            if op['source']['type'] == 'group':
                replyTextMessage(reply_token, ':(')
                line_bot_api.leave_group(op['source']['groupId'])
            elif op['source']['type'] == 'room':
                replyTextMessage(reply_token, ':(')
                line_bot_api.leave_room(op['source']['roomId'])
        else:
            sourcetype = op['source']['type']
            sourceuserid = op['source']['userId']
            if sourcetype in important['chaton']:
                if sourcetype == 'user':
                    if sourceuserid in important['chaton'][sourcetype]:
                        if important['chaton'][sourcetype][sourceuserid] == True:
                            chatbot(reply_token, msgtext)
                else:
                    if sourcetype == 'room':
                        chatid = op['source']['roomId']
                    elif sourcetype == 'group':
                        chatid = op['source']['groupId']
                    if chatid in important['chaton'][sourcetype]:
                        if important['chaton'][sourcetype][chatid] == True:
                            chatbot(reply_token, msgtext)
    except LineBotApiError as e:
        replyTextMessage(reply_token, 'error')
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)
    except Exception as e:
        replyTextMessage(reply_token, 'error')
        print(e)

@handler.add(MessageEvent, message=ImageMessage)
def handle_imgmessage(event):
    op = json.loads(str(event))
    reply_token = op['replyToken']
    userId = op['source']['userId']
    msgId = op['message']['id']
    tipe = op['source']['type']
    if tipe == 'room':
        ID = op['source']['roomId']
    elif tipe == 'group':
        ID = op['source']['groupId']
    try:
        if tipe in important['kotakin']:
            if tipe == 'user':
                if tipe in important['kotakin']:
                    if userId in important['kotakin'][tipe]:
                        mode = important['kotakin'][tipe][userId]
                        try:
                            del important['kotakin'][tipe][userId]
                        except:
                            pass
                        kotakin(reply_token, msgId, mode)
            else:
                if tipe in important['kotakin']:
                    if ID in important['kotakin'][tipe]:
                        if userId in important['kotakin'][tipe][ID]:
                            mode = important['kotakin'][tipe][ID][userId]
                            try:
                                del important['kotakin'][tipe][ID][userId]
                            except:
                                pass
                            kotakin(reply_token, msgId, mode)
            savejson()
        elif tipe in important['memegen']:
            if tipe == 'user':
                if tipe in important['memegen']:
                    if userId in important['memegen'][tipe]:
                        mode = important['memegen'][tipe][userId]
                        try:
                            del important['memegen'][tipe][userId]
                        except:
                            pass
                        memegen(reply_token, msgId, mode)
            else:
                if tipe in important['memegen']:
                    if ID in important['memegen'][tipe]:
                        if userId in important['memegen'][tipe][ID]:
                            mode = important['memegen'][tipe][ID][userId]
                            try:
                                del important['memegen'][tipe][ID][userId]
                            except:
                                pass
                            memegen(reply_token, msgId, mode)
            savejson()
        elif tipe in important['tebak']:
            if tipe == 'user':
                if tipe in important['tebak']:
                    if userId in important['tebak'][tipe]:
                        mode = important['tebak'][tipe][userId]
                        try:
                            del important['tebak'][tipe][userId]
                        except:
                            pass
                        tebakgambar(reply_token, msgId, mode)
            else:
                if tipe in important['tebak']:
                    if ID in important['tebak'][tipe]:
                        if userId in important['tebak'][tipe][ID]:
                            mode = important['tebak'][tipe][ID][userId]
                            try:
                                del important['tebak'][tipe][ID][userId]
                            except:
                                pass
                            tebakgambar(reply_token, msgId, mode)
            savejson()
    except LineBotApiError as e:
        replyTextMessage(reply_token, 'error')
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)
    except Exception as e:
        replyTextMessage(reply_token, 'error')
        print(e)

@handler.add(MessageEvent, message=LocationMessage)
def handle_locmessage(event):
    op = json.loads(str(event))
    lat = op['message']['latitude']
    lng = op['message']['longitude']
    reply_token = op['replyToken']
    try:
        pic = [
            'https://maps.googleapis.com/maps/api/streetview?location=%s,%s&size=600x400&heading=0&key=AIzaSyAQmw_o6BhLfnH5LMM2B8oDGyHMx6QC--Y' % (lat, lng),
            'https://maps.googleapis.com/maps/api/streetview?location=%s,%s&size=600x400&heading=90&key=AIzaSyAQmw_o6BhLfnH5LMM2B8oDGyHMx6QC--Y' % (lat, lng),
            'https://maps.googleapis.com/maps/api/streetview?location=%s,%s&size=600x400&heading=180&key=AIzaSyAQmw_o6BhLfnH5LMM2B8oDGyHMx6QC--Y' % (lat, lng),
            'https://maps.googleapis.com/maps/api/streetview?location=%s,%s&size=600x400&heading=270&key=AIzaSyAQmw_o6BhLfnH5LMM2B8oDGyHMx6QC--Y' % (lat, lng)
        ]
        TB = []
        amon = len(pic)
        tipe = 'img'
        for a in pic:
            isi_TB = {}
            isi_TB['tumbnail'] = a
            isi_TB['action'] = actionBuilder(1, ['uri'], ['image'], [a])
            TB.append(isi_TB)
        dat = {}
        dat['alt'] = 'Multi_Bots location'
        dat['template'] = templateBuilder(amon, tipe, TB)
        replyCarrouselMessage(reply_token, dat)
    except LineBotApiError as e:
        replyTextMessage(reply_token, 'error')
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)
    except Exception as e:
        replyTextMessage(reply_token, 'error')
        print(e)

@handler.add(PostbackEvent)
def handle_postback(event):
    op = json.loads(str(event))
    reply_token = op['replyToken']
    postbackdata = op['postback']['data']
    try:
        if postbackdata.lower() == 'help':
            help(reply_token)
        elif postbackdata.lower() == 'help youtube':
            help(reply_token, 1)
        elif postbackdata.lower() == 'help instagram':
            help(reply_token, 2)
        elif postbackdata.lower() == 'help stuff':
            help(reply_token, 3)
        elif postbackdata.lower() == 'help about':
            help(reply_token, 4)
        elif postbackdata.lower() == 'help anime':
            help(reply_token, 5)
        elif postbackdata.lower() == 'help pixiv':
            help(reply_token, 6)
        elif postbackdata.lower() == 'help deviantart':
            help(reply_token, 7)
        elif postbackdata.lower() == 'help tbkgmbr':
            help(reply_token, 8)
        elif postbackdata.lower() == 'help texttospeech':
            help(reply_token, 9)
        elif postbackdata.lower().startswith('anidesc '):
            data = postbackdata[8:]
            myanime(reply_token, 3, data)
        elif postbackdata.lower().startswith('anipv '):
            data = postbackdata[6:]
            myanime(reply_token, 5, data)
        elif postbackdata.lower().startswith('cuaca '):
            data = postbackdata[6:]
            cuaca(reply_token, 1, data)
        else:
            replyTextMessage(reply_token, str(postbackdata))
    except LineBotApiError as e:
        replyTextMessage(reply_token, 'error')
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)
    except Exception as e:
        replyTextMessage(reply_token, 'error')
        print(e)

if __name__ == "__main__":
    make_static_tmp_dir()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
