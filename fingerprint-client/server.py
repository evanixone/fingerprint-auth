import http.server
import socketserver
from http import HTTPStatus
import json
from PIL import Image
import serial
import adafruit_fingerprint
import cv2
import numpy as np

def input_fingerprint():
    from time import sleep

    uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
    finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

    while finger.get_image():
        pass

    print("fingerprint collected")

    img = Image.new("L", (256, 288), "white")
    pixeldata = img.load()
    mask = 0b00001111
    result = finger.get_fpdata(sensorbuffer="image")

    x = 0
    y = 0

    for i in range(len(result)):
        pixeldata[x, y] = (int(result[i]) >> 4) * 17
        x += 1
        pixeldata[x, y] = (int(result[i]) & mask) * 17
        if x == 255:
            x = 0
            y += 1
        else:
            x += 1

    if not img.save(f"fingerprint.png"):
        return f"fingerprint.png"
    return None

def enhance_image(img1):
    from generate.enhance import enhance

    if len(img1.shape) > 2:
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    image_enhancer = enhance.FingerprintImageEnhancer()
    img1 = image_enhancer.enhance(img1)
    return 255 * img1

def extract_image(image):
    from generate.extract import extract
    from generate.match.describe import MinutiaeConverter

    FeaturesTerminations, FeaturesBifurcations = extract.extract_minutiae_features(image, spuriousMinutiaeThresh=10, saveResult=False)
    minutiae_list = FeaturesTerminations + FeaturesBifurcations
    return MinutiaeConverter().convert_minutiae_to_descriptors(minutiae_list)

def hide_data(descriptors, username):
    from generate.hide_data import hide_data
    return hide_data.hide_data(descriptors, username)

class FingerprintHandler(http.server.SimpleHTTPRequestHandler):
    def _set_headers(self):
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self._set_headers()
        self.end_headers()

    def do_POST(self):
        if self.path in ['/enroll', '/enrolltest']:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            username = data.get('username')
            if not username:
                self.send_response(HTTPStatus.BAD_REQUEST)
                self._set_headers()
                self.end_headers()
                self.wfile.write(b'Username is missing')
                return
            
            img1 = None
            if self.path == '/enroll':
                img1 = input_fingerprint()
                filename = f"fingerprint.png"
                img1 = cv2.imread(filename)
            elif self.path == '/enrolltest':
                fingerprint = "fingerprint0"
                filename = f"./images/{fingerprint}.png"
                img1 = cv2.imread(filename)

            img1 = enhance_image(img1)
            descriptors = extract_image(img1)
            descriptors = hide_data(descriptors, username)

            response = {
                'descriptors': descriptors
            }

            for key, value in response.items():
                if isinstance(value, np.ndarray):
                    response[key] = value.tolist()

            self.send_response(HTTPStatus.OK)
            self._set_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self._set_headers()
            self.end_headers()

PORT = 8080
Handler = FingerprintHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
