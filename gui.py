from PIL import Image, ImageTk
import tkinter as tk
import argparse
import datetime
import numpy as np
import simpleaudio as sa
import threading
import cv2
import os
from utils import *


class PostureAidApplication:
    def __init__(self, output_path="./"):
        """ Initialize application which uses OpenCV + Tkinter. It displays
            a video stream in a Tkinter window and stores current snapshot on disk """
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        self.vs = cv2.VideoCapture(0)
        self.output_path = output_path  # store output path
        self.current_image = None  # current image from the camera
        self.finish = False
        self.wave_obj = sa.WaveObject.from_wave_file(
            './data/audio/alarm_tone.wav')
        self.pad = 20
        _, frame = self.vs.read()
        frame = cv2.flip(frame, 1)
        self.correct_pos = self.get_pos_from_frame(frame)

        self.root = tk.Tk()
        self.root.title("Posture Aid")  # set window title
        # self.destructor function gets fired when the window is closed
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)

        self.panel = tk.Label(self.root)  # initialize image panel
        self.panel.pack(padx=10, pady=10)

        # create a button, that when pressed, will take the current frame and save it to file
        btn = tk.Button(self.root, text="Snapshot!",
                        command=self.take_snapshot)
        btn.pack(fill="both", expand=True, padx=10, pady=10)

        self.label = tk.Label(self.root, text="Padding")
        self.label.pack(side=tk.LEFT)

        self.pad_input = tk.Spinbox(self.root, from_=30, to=50)
        self.pad_input.pack(side=tk.LEFT)

        # start a self.video_loop that constantly pools the video sensor
        # for the most recently read frame
        self.video_loop()

    def reset_head_pos(self):
        pass

    def play_alarm(self):
        play_obj = None
        while True:
            if self.finish:
                play_obj.stop()
                break
            if not play_obj or not play_obj.is_playing():
                play_obj = self.wave_obj.play()

    def get_pos_from_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5)

        max_area = 0
        area = 0
        pos = (0, 0, 0, 0)
        for (x, y, w, h) in faces:
            area = h*w
            if area > max_area:
                max_area = area
                pos = (x, y, w, h)
        return pos

    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.vs.read()  # read frame from video stream
        frame = cv2.flip(frame, 1)
        if ok:  # frame captured without any errors
            current_pos = self.get_pos_from_frame(frame)
            (fx, fy, fw, fh) = self.correct_pos
            (x, y, w, h) = current_pos

            t = None
            pad = int(self.pad_input.get())
            if not check_head_within_boundary(self.correct_pos, current_pos, pad):
                if self.finish:
                    self.finish = False
                    t = threading.Thread(target=self.play_alarm)
                    t.start()
            else:
                if not self.finish:
                    self.finish = True
                    if t:
                        t.join()

            frame = cv2.rectangle(
                frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            frame = cv2.rectangle(frame, (fx-pad, fy-pad),
                                  (fx+fw+pad, fy+fh+pad), (255, 0, 0), 2)

            # convert colors from BGR to RGBA
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_image = Image.fromarray(cv2image)
            # # convert image for tkinter
            imgtk = ImageTk.PhotoImage(image=self.current_image)
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk)  # show the image
        # call the same function after 30 milliseconds
        self.root.after(30, self.video_loop)

    def take_snapshot(self):
        """ Take snapshot and save it to the file """
        ts = datetime.datetime.now()  # grab the current timestamp
        filename = "{}.jpg".format(ts.strftime(
            "%Y-%m-%d_%H-%M-%S"))  # construct filename
        p = os.path.join(self.output_path, filename)  # construct output path
        self.current_image.save(p, "JPEG")  # save image as jpeg file
        print("[INFO] saved {}".format(filename))

    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        self.root.destroy()
        self.finish = True
        self.vs.release()  # release web camera
        cv2.destroyAllWindows()  # it is not mandatory in this application


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", default="./",
                help="path to output directory to store snapshots (default: current folder")
args = vars(ap.parse_args())

# start the app
print("[INFO] starting...")
pba = PostureAidApplication(args["output"])
pba.root.mainloop()
