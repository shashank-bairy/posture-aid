import threading
import cv2
import numpy as np
import simpleaudio as sa

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

pad = 20
correct_pos = (0, 0, 0, 0)

_FINISH = True

wave_obj = sa.WaveObject.from_wave_file('./data/audio/alarm_tone.wav')


def play_alarm():
    play_obj = None
    while True:
        if _FINISH:
            play_obj.stop()
            break
        if not play_obj or not play_obj.is_playing():
            play_obj = wave_obj.play()


def get_pos_from_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
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


def check_head_within_boundary(correct_pos, current_pos, pad):
    (x1, y1, w1, h1) = correct_pos
    (x2, y2, w2, h2) = current_pos

    return (x1-pad <= x2 <= x2+w2 <= x1+w1+pad) and (y1-pad <= y2 <= y2+h2 <= y1+h1+pad)


def run_posture_aid():
    video = cv2.VideoCapture(0)

    _, frame = video.read()
    correct_pos = get_pos_from_frame(frame)
    print('Correct position configured')

    global _FINISH

    while True:
        _, frame = video.read()
        current_pos = get_pos_from_frame(frame)
        (fx, fy, fw, fh) = correct_pos
        (x, y, w, h) = current_pos

        t = None
        if not check_head_within_boundary(correct_pos, current_pos, 30):
            if _FINISH:
                _FINISH = False
                print(_FINISH)
                t = threading.Thread(target=play_alarm)
                t.start()
        else:
            if not _FINISH:
                _FINISH = True
                if t:
                    t.join()

        frame = cv2.rectangle(
            frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        frame = cv2.rectangle(frame, (fx-pad, fy-pad),
                              (fx+fw+pad, fy+fh+pad), (255, 0, 0), 2)

        cv2.imshow('Face detector', frame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    run_posture_aid()
