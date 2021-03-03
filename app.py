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
        self.running = False
        self.pad_x = 30
        self.pad_y = 30
        self.correct_pos = (0, 0, 0, 0)
        self.wave_obj = sa.WaveObject.from_wave_file(
            './data/audio/alarm_tone.wav')

        self.root = tk.Tk()
        self.root.title("Posture Aid")  # set window title
        # self.destructor function gets fired when the window is closed
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)

        self.panel = tk.Label(self.root)  # initialize image panel
        self.panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.startBtn = tk.Button(
            self.root, text="Start", command=self.start_running)
        self.startBtn.pack(fill=tk.X, side=tk.LEFT,
                           expand=True, padx=10, pady=10)

        self.stopBtn = tk.Button(
            self.root, text="Stop", command=self.stop_running)
        self.stopBtn.pack(fill=tk.X, side=tk.LEFT,
                          expand=True, padx=10, pady=10)

        self.settingsBtn = tk.Button(
            self.root, text="Settings", command=self.show_settings)
        self.settingsBtn.pack(fill=tk.X, side=tk.LEFT,
                              expand=True, padx=10, pady=10)

        self.video_loop()

    def exit_settings(self, win, pad_x, pad_y):
        self.pad_x = pad_x
        self.pad_y = pad_y
        win.destroy()

    def show_settings(self):
        win = tk.Toplevel()
        win.wm_title("Settings")
        win.geometry("300x120")
        win.resizable(0, 0)

        frame_x = tk.Frame(win)

        label_x = tk.Label(frame_x, text="Boundary width")
        label_x.pack(fill="both", expand=True, side=tk.LEFT)

        pad_x = tk.Spinbox(frame_x, from_=30, to=50)
        pad_x.pack(fill="both", expand=True, side=tk.LEFT)

        frame_x.pack(fill="both", padx=10, pady=10)

        frame_y = tk.Frame(win)

        label_y = tk.Label(frame_y, text="Boundary height")
        label_y.pack(fill="both", expand=True, side=tk.LEFT)

        pad_y = tk.Spinbox(frame_y, from_=30, to=50)
        pad_y.pack(fill="both", expand=True, side=tk.LEFT)

        frame_y.pack(fill="both", padx=10, pady=10)

        btn = tk.Button(win, text="Okay", command=lambda: self.exit_settings(
            win, pad_x.get(), pad_y.get()))
        btn.pack(fill=tk.X, expand=True, padx=10, pady=10)

        win.mainloop()

    def start_running(self):
        self.running = True

    def stop_running(self):
        self.running = False
        self.finish = True

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

            pad_x = int(self.pad_x)
            pad_y = int(self.pad_y)

            if self.running:
                t = None
                if not check_head_within_boundary(self.correct_pos, current_pos, pad_x, pad_y):
                    if self.finish:
                        self.finish = False
                        t = threading.Thread(target=self.play_alarm)
                        t.start()
                else:
                    if not self.finish:
                        self.finish = True
                        if t:
                            t.join()
            else:
                self.correct_pos = current_pos

            (fx, fy, fw, fh) = self.correct_pos
            (x, y, w, h) = current_pos
            frame = cv2.rectangle(
                frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            frame = cv2.rectangle(frame, (fx-pad_x, fy-pad_y),
                                  (fx+fw+pad_x, fy+fh+pad_y), (0, 0, 255), 2)

            # convert colors from BGR to RGBA
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_image = Image.fromarray(cv2image)
            # # convert image for tkinter
            imgtk = ImageTk.PhotoImage(image=self.current_image)
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk)  # show the image

        # call the same function after 30 milliseconds
        self.root.after(30, self.video_loop)

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
