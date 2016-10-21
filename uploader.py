import time
import os
from instagram import InstagramSession

USERNAME = "cycamatic"
PASSWORD = "<password>"

PHOTO_DIR = "/opt/photos/"
PROCESSED_DIR = "/opt/photos-processed/"


def upload_photo(filepath):
    print "Converting {}".format(filepath)
    status = os.system(
        "convert -sample 1280x1280^ -gravity Center "
        "-extent 1280x1280 {} /tmp/small.jpg".format(filepath)
    )
    if status & 0xff00:
        raise ValueError("Failed to convert")

    print "Uploading {}".format(filepath)
    insta = InstagramSession()
    if insta.login(USERNAME, PASSWORD):
        media_id = insta.upload_photo("/tmp/small.jpg")
        print media_id
        if media_id is not None:
            insta.configure_photo(media_id, "")
            #try:
            #    insta.permalink(media_id)
            #except:
            #    pass
            return True

    return False


def main():
    if not os.access(PHOTO_DIR, os.R_OK | os.W_OK | os.X_OK):
        raise ValueError("Need permission to {}".format(PHOTO_DIR))

    while True:
        time.sleep(1)
        for fn in os.listdir(PHOTO_DIR):
            path = os.path.join(PHOTO_DIR, fn)
            if upload_photo(path):
                print "Moving {}".format(path)
                os.rename(path, os.path.join(PROCESSED_DIR, fn))
            else:
                print "Failed"


if __name__ == "__main__":
    main()
