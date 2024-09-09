import serial
import adafruit_fingerprint
import os
import cv2
import json
import requests
import numpy as np
from generate.enhance import enhance
from generate.extract import extract
from generate.match.match import match_sets
from generate.match.describe import MinutiaeConverter
from PIL import Image

url = 'http://127.0.0.1:8000/register/api/'
username = ''


def __normalise(img: np.ndarray) -> np.ndarray:
        """Normalize the image.

        Args:
            img (np.ndarray): input image.

        Raises:
            ValueError: raises an exception if image is faulty.

        Returns:
            np.ndarray: normalized image
        """
        if np.std(img) == 0:
            raise ValueError("Image standard deviation is 0. Please review image again")
        normed = (img - np.mean(img)) / (np.std(img))
        print(img)
        print(255 *normed)
        return normed

def test_normalise(filename):
    img1 = cv2.imread(filename, 0)
    if len(img1.shape) > 2:  # convert image into gray if necessary
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img1 = __normalise(img1)
    cv2.imwrite('normalise.png', (255 * img1))

def test_enhance(filename):
    img1 = cv2.imread(filename, 0)
    if len(img1.shape) > 2:  # convert image into gray if necessary
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    image_enhancer = enhance.FingerprintImageEnhancer()
    img1 = image_enhancer.enhance(img1)
    cv2.imwrite('segment.png', (255 * image_enhancer._normim))
    cv2.imwrite('orient.png', (255 * image_enhancer._orientim))
    cv2.imwrite('result.png', (255 * image_enhancer._binim))

def test_extract(filename1):
    img1 = cv2.imread(filename1, 0)
    FeaturesTerminations, FeaturesBifurcations = extract.extract_minutiae_features(img1, spuriousMinutiaeThresh=10, saveResult=True)

def main():
    while True:
        print("----------------")
        print("1) test normalise")
        print("2) test enhance")
        print("3) test extract")
        print("q) quit")
        print("----------------")

        c = input("> ")

        if c == "1":
            test_normalise(f"./images/test1.png")
        elif c == "2":
            test_enhance(f"./images/test1.png")
        elif c == "3":
            test_extract(f"result.png")
        elif c == "q":
            quit()
        else:
            print("invalid option")


if __name__ == "__main__":
    try:
        main()
    except:
        raise
    