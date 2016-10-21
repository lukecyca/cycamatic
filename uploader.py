import time
import os
import os.path
import configparser
import pynstagram


def upload_photo(filepath, c):
    print "Converting {}".format(filepath)
    status = os.system(
        "convert -auto-orient -sample 1280x1280^ -gravity Center "
        "-extent 1280x1280 {} /tmp/small.jpg".format(filepath)
    )
    if status & 0xff00:
        raise ValueError("Failed to convert")

    print "Uploading {}".format(filepath)
    with pynstagram.client(c['username'], c['password']) as client:
        client.upload("/tmp/small.jpg", c['caption'])


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    c = config['instagram']

    source_dir = os.path.abspath(c['source_dir'])
    dest_dir = os.path.abspath(c['dest_dir'])
    throttle = int(c['throttle'])

    if not os.access(source_dir, os.R_OK | os.W_OK | os.X_OK):
        raise ValueError("Need permission to {}".format(source_dir))

    while True:
        time.sleep(1)
        for fn in os.listdir(source_dir):
            path = os.path.join(source_dir, fn)
            upload_photo(path, c)
            print "Moving {}".format(path)
            os.rename(path, os.path.join(dest_dir, fn))
            time.sleep(throttle)


if __name__ == "__main__":
    main()
