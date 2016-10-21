import RPi.GPIO as GPIO
import time
import datetime
import gphoto2 as gp
from gphoto2.backend import lib as gplib
import logging
import signal
import sys
import thread


# Pins
BUTTON = 27
READY_LED = 18
POSE_LED = 22
WAIT_LED = 17


def flash(pin, delay, count):
    for _ in range(count):
        GPIO.output(pin, True)
        time.sleep(delay)
        GPIO.output(pin, False)
        time.sleep(delay)


def main():
    logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    GPIO.setwarnings(False)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON, GPIO.IN)
    GPIO.setup(READY_LED, GPIO.OUT)
    GPIO.setup(POSE_LED, GPIO.OUT)
    GPIO.setup(WAIT_LED, GPIO.OUT)

    # Fancy startup sequence
    for _ in range(3):
        GPIO.output(READY_LED, True)
        time.sleep(0.05)
        GPIO.output(POSE_LED, True)
        time.sleep(0.05)
        GPIO.output(WAIT_LED, True)
        time.sleep(0.2)
        GPIO.output(READY_LED, False)
        time.sleep(0.05)
        GPIO.output(POSE_LED, False)
        time.sleep(0.05)
        GPIO.output(WAIT_LED, False)
        time.sleep(0.1)

    # Catch signals and turn off LEDs upon exit
    def signal_handler(signal, frame):
        GPIO.output(READY_LED, False)
        GPIO.output(POSE_LED, False)
        GPIO.output(WAIT_LED, False)
        sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    # Connect to camera
    cam = gp.Camera()
    GPIO.output(READY_LED, True)
    GPIO.output(POSE_LED, False)
    GPIO.output(WAIT_LED, False)

    lock = thread.allocate_lock()

    while True:
        if not GPIO.input(BUTTON):
            continue

        GPIO.output(READY_LED, False)

        # Trigger capture
        def trig():
            try:
                err = gplib.gp_camera_trigger_capture(cam._cam, cam._ctx)
                if err != 0:
                    raise ValueError("gp_camera_trigger_capture returned {}".format(err))
            except:
                thread.interrupt_main()
            lock.release()

        lock.acquire()
        thread.start_new_thread(trig, ())
        flash(POSE_LED, 0.5, 2)
        while lock.locked():
            flash(POSE_LED, 0.125, 1)
        GPIO.output(WAIT_LED, True)

        # Wait for camera to process the photo
        fobj = cam._wait_for_event(event_type=gplib.GP_EVENT_FILE_ADDED)
        data = fobj.get_data()
        try:
            fobj.remove()
        except gp.errors.CameraIOError:
            pass

        filename = datetime.datetime.now().strftime('/opt/photos/%Y-%m-%d-%H-%M-%S.%f.jpg')
        print("Saving " + filename)
        with open(filename, "wb") as fh:
            fh.write(data)

        flash(WAIT_LED, 0.5, 10)

        GPIO.output(WAIT_LED, False)
        GPIO.output(READY_LED, True)

        time.sleep(0.01)

if __name__ == "__main__":
    main()
