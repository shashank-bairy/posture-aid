import tkinter as tk
import cv2
import torch
import posenet

from config import PostureAidConfig
from alarm import Alarm
from utils import check_head_within_boundary, draw_boxes


class PostureAidApplication:
    def __init__(self):
        """ Initialize application which uses OpenCV + Tkinter. It displays
            a video stream in a Tkinter window and stores current snapshot on disk """

        self._running = False
        self._vs = cv2.VideoCapture(PostureAidConfig.config("CAM_ID"))
        self._pad_x = PostureAidConfig.config("PAD_X")
        self._pad_y = PostureAidConfig.config("PAD_Y")
        self._correct_pos = PostureAidConfig.config("CORRECT_POS")
        self._alarm = Alarm(PostureAidConfig.config("ALARM_FILE"))
        self._model = self._get_model()
        self._output_stride = self._model.output_stride

        self.root = tk.Tk()
        self.root.title("Posture Aid")

        self.root.protocol('WM_DELETE_WINDOW', self._destructor)

        self.panel = tk.Label(self.root)
        self.panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.startBtn = tk.Button(
            self.root, text="Start", command=self._start_running)
        self.startBtn.pack(fill=tk.X, side=tk.LEFT,
                           expand=True, padx=10, pady=10)

        self.stopBtn = tk.Button(
            self.root, text="Stop", command=self._stop_running)
        self.stopBtn.pack(fill=tk.X, side=tk.LEFT,
                          expand=True, padx=10, pady=10)

        self.settingsBtn = tk.Button(
            self.root, text="Settings", command=self._show_settings)
        self.settingsBtn.pack(fill=tk.X, side=tk.LEFT,
                              expand=True, padx=10, pady=10)

        self._video_loop()
    
    def _get_model(self):
        model = posenet.load_model(PostureAidConfig.config("MODEL"))
        if torch.cuda.is_available():
            model = model.cuda()
        return model

    def _show_settings(self):
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

        btn = tk.Button(win, text="Okay", command=lambda: self._exit_settings(
            win, pad_x.get(), pad_y.get()))
        btn.pack(fill=tk.X, expand=True, padx=10, pady=10)

        win.mainloop()
    
    def _exit_settings(self, win, pad_x, pad_y):
        self._pad_x = int(pad_x)
        self._pad_y = int(pad_y)
        win.destroy()

    def _start_running(self):
        self._running = True

    def _stop_running(self):
        self._running = False
        self._alarm.stop()

    def _video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """

        input_image, display_image, output_scale = posenet.read_cap(
            self._vs,
            scale_factor=PostureAidConfig.config("SCALE_FACTOR"),
            output_stride=self._output_stride
        )

        with torch.no_grad():
            if torch.cuda.is_available():
                input_image = torch.Tensor(input_image).cuda()
            else:
                input_image = torch.Tensor(input_image)

            heatmaps_result, offsets_result, displacement_fwd_result, displacement_bwd_result = self._model(input_image)

            pose_scores, keypoint_scores, keypoint_coords = posenet.decode_multiple_poses(
                heatmaps_result.squeeze(0),
                offsets_result.squeeze(0),
                displacement_fwd_result.squeeze(0),
                displacement_bwd_result.squeeze(0),
                output_stride=self._output_stride,
                max_pose_detections=10,
                min_pose_score=0.15
            )

        keypoint_coords *= output_scale        
        
        current_pos = posenet.get_pos_from_img(
            display_image, pose_scores, keypoint_scores, keypoint_coords,
            min_pose_score=0.15, min_part_score=0.1
        )

        if self._running:
            if not check_head_within_boundary(self._correct_pos, current_pos, self._pad_x, self._pad_y):
                if not self._alarm.is_playing():
                    self._alarm.play()
            else:
                if self._alarm.is_playing():
                    self._alarm.stop()
        else:
            self._correct_pos = current_pos

        imgtk = draw_boxes(display_image, self._correct_pos, current_pos, self._pad_x, self._pad_y)
        self.panel.imgtk = imgtk
        self.panel.config(image=imgtk)

        # call the same function after 30 milliseconds
        self.root.after(50, self._video_loop)

    def _destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        self.root.destroy()
        self._vs.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    app = PostureAidApplication()
    app.root.mainloop()