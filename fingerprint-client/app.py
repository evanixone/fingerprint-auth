import serial
import adafruit_fingerprint
import os
import cv2
from time import sleep
from generate.enhance import enhance
from generate.extract import extract
from generate.match.match import match_sets
from generate.match.describe import MinutiaeConverter
from generate.hide_data import hide_data
from PIL import Image

def measure_quality(filename):
    from pypiqe import piqe
    img1 = cv2.imread(filename, 0)
    score, activityMask, noticeableArtifactMask, noiseMask = piqe(img1)
    return score

def enhance_image(filename):
    img1 = cv2.imread(filename, 0)  # Read image in grayscale
    if len(img1.shape) > 2:  # convert image into gray if necessary
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    image_enhancer = enhance.FingerprintImageEnhancer()
    img1 = image_enhancer.enhance(img1)
    return 255 * img1

def get_minutiae_descriptors(image):
    FeaturesTerminations, FeaturesBifurcations = extract.extract_minutiae_features(image, spuriousMinutiaeThresh=10, saveResult=False)
    minutiae_list = FeaturesTerminations + FeaturesBifurcations
    return MinutiaeConverter().convert_minutiae_to_descriptors(minutiae_list)


def match_test(filename1, filename2):
    img1 = enhance_image(filename1)
    img2 = enhance_image(filename2)

    source_minutiae = get_minutiae_descriptors(img1)
    target_minutiae = get_minutiae_descriptors(img2)

    source_minutiae = hide_data.hide_data(source_minutiae, "iwan")
    target_minutiae = hide_data.hide_data(target_minutiae, "iwan")

    hidden_message = hide_data.extract_message(source_minutiae)
    print(hidden_message)
    
    return match_sets(source_minutiae, target_minutiae)
    

def save_fingerprint_image(filename):
    uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
    finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

    while finger.get_image():
        # sleep(1)
        pass
    print("got it")
    from PIL import Image

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

    if not img.save(filename):
        return filename  # Return the filename if saved successfully
    return None

def input_fingerprint(target_filename):
    if os.path.exists(target_filename):
        os.remove(target_filename)
    print("Put your fingerprint on the sensor")
    if save_fingerprint_image(target_filename):
        print(f"Fingerprint image saved")
    else:
        print(f"Failed to save fingerprint image")

def generate_result(directory):
    average_quality = 0
    first_quality = None
    last_quality = None
    match_results = []
    match_scores = []
    failed_attempts = 0
    false_matches = 0
    false_non_matches = 0
    total_quality_samples = 0

    for i in range(10):
        quality = measure_quality(f"./{directory}/{i}.png")
        
        if quality is None:
            failed_attempts += 1
            continue
        
        if total_quality_samples == 0:
            first_quality = quality
        average_quality += quality
        last_quality = quality
        total_quality_samples += 1

        # Match with 0.png
        match_0, score_0 = match_test(f"./{directory}/0.png", f"./{directory}/{i}.png")
        # Match with 5.png
        match_5, score_5 = match_test(f"./{directory}/5.png", f"./{directory}/{i}.png")
        
        if i < 5:
            # Genuine attempt: should match with 0.png
            if not match_0:
                false_non_matches += 1
            # Impostor attempt: should not match with 5.png
            if match_5:
                false_matches += 1
        else:
            # Genuine attempt: should match with 5.png
            if not match_5:
                false_non_matches += 1
            # Impostor attempt: should not match with 0.png
            if match_0:
                false_matches += 1
        
        # Record the better score and match result
        if score_0 > score_5:
            match_results.append("Good" if match_0 else "Bad")
            match_scores.append(score_0)
        else:
            match_results.append("Good" if match_5 else "Bad")
            match_scores.append(score_5)
    
    total_attempts = 10 - failed_attempts
    average_quality /= total_attempts
    consistency = (1 - abs((first_quality - last_quality) / first_quality)) * 100

    FTA = failed_attempts / 10
    FMR = false_matches / 5  # False matches over 5 impostor attempts
    FNMR = false_non_matches / 5  # False non-matches over 5 genuine attempts
    FRR = FTA + FNMR * (1 - FTA)
    FAR = FMR * (1 - FTA)

    # Calculate average score excluding 0.png and 5.png
    average_score = sum(match_scores[1:5] + match_scores[6:10]) / 8

    print("Average Quality:", average_quality)
    print("Usable Range:", 100)
    print("Consistency:", consistency)
    print("Match result:", match_results)
    print("Match scores:", match_scores)
    print("FTA:", FTA)
    print("FMR:", FMR)
    print("FNMR:", FNMR)
    print("FRR:", FRR)
    print("FAR:", FAR)
    print("Average Score:", average_score)


def main():
    while True:
        print("----------------")
        print("t) test match")
        print("tr) test match raspberrypi")
        print("s) save fingerprint images")
        print("r) generate result")
        print("q) quit")
        print("----------------")

        c = input("> ")

        if c == "t":
            fingerprint1 = input("Enter fingerprint 1: ")
            fingerprint2 = input("Enter fingerprint 2: ")
            match_test(f"./images/{fingerprint1}.png", f"./images/{fingerprint2}.png")
        elif c == "tr":
            filename1 = "./images/fingerprint0.png"
            filename2 = "./images/fingerprint1.png"
            input_fingerprint(filename1)
            input_fingerprint(filename2)
            match_test(filename1, filename2)
        elif c == "s":
            directory = input("Enter Directory Name: ")
            os.makedirs(directory)
            for i in range(10):
                input_fingerprint(f"./{directory}/{i}.png")
        elif c == "r":
            directory = input("Generating Result For: ")
            generate_result(directory)
        elif c == "q":
            quit()
        else:
            print("invalid option")


if __name__ == "__main__":
    try:
        main()
    except:
        raise
    