import cv2
from pypiqe import piqe

def measure_quality(filename):
    img = cv2.imread(filename, 0)
    score, activityMask, noticeableArtifactMask, noiseMask = piqe(img)
    return score

def main():
    filename = 'images/test1.png'
    
    score = measure_quality(filename)
    
    print(f"The quality score of the image '{filename}' is: {score}")

if __name__ == "__main__":
    main()
