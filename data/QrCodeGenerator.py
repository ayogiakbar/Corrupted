from pyqrcode import QRCode
from PIL import Image
import time

class QrCodeGenerator:
    def generate(self, string, imagepath=None):
        qr = QRCode(string, error='H')
        path = time.time()*1000
        qr.png(path, scale=10)
        if(imagepath == None):
            return path
        else:
            self.addImage(path, imagepath)
            return path

    def addImage(self, qrpath, imagepath):
        image = Image.open(qrpath)
        image = image.convert('RGBA')
        logo = Image.open(imagepath)
        box = (135, 135, 235, 235)
        image.crop(box)
        region = logo
        region = region.resize((box[2] - box[0], box[3] - box[1]))
        image.paste(region, box)
        image.save(qrpath)