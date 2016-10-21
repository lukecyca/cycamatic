import time
import os


# -resize is best
# -scale
# -sample is fastest


INPUT_DIR = "/opt/photos/"
OUTPUT_DIR = "/root/slideshow/"
PROCESSED_DIR = "/opt/photos-processed/"

def move_photo(filepath):
    print "Converting {}".format(filepath)
    status = os.system(
        "convert -resize '2000x2000>' {} {}cycamatic-{}.jpg".format(filepath, OUTPUT_DIR, int(time.time()))
        #"convert -sample '2000x2000>' {} {}cycamatic-{}.jpg".format(filepath, OUTPUT_DIR, int(time.time()))
    )
    if status & 0xff00:
        print("Failed to convert")
        return False

    return True


def main():
    if not os.access(OUTPUT_DIR, os.R_OK | os.W_OK | os.X_OK):
        raise ValueError("Need permission to {}".format(INPUT_DIR))

    while True:
        time.sleep(1)
        for fn in os.listdir(INPUT_DIR):
            path = os.path.join(INPUT_DIR, fn)
            if move_photo(path):
                print "Moving {}".format(path)
                os.rename(path, os.path.join(PROCESSED_DIR, fn))
            else:
                print "Failed"


if __name__ == "__main__":
    main()
