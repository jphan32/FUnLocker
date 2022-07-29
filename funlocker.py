#!/usr/bin/python3

import cv2
from PIL import Image as Img
from PIL import ImageTk
from cv2 import transform

from tkinter import *
import tkinter.font as tkFont

import tensorflow as tf
import tflite_runtime.interpreter as tflite

from inference import *

#### Defined PATH
MODEL_PATH_TPU = "Mobilefacenet/pretrained_model/edgetpu_v1/facedetection_320_240_edgetpu.tflite"
REC_MODEL_PATH_TPU = "Mobilefacenet/pretrained_model/edgetpu_v2/model_with_mask_clf_quant_edgetpu.tflite"
CAMERA_WIDTH, CAMERA_HEIGHT = 640, 480
WIDTH, HEIGHT = 320, 240
STATE_VIEW, STATE_DETECT_ONLY, STATE_CAPTURE, STATE_RECOGNITION = [i for i in range(4)]

#### Global variables
#mode_state = STATE_VIEW
mode_state = STATE_DETECT_ONLY
lock_state = True

# Recursive refresh by every (REFRESH_TIME_MS)ms
class MainWindow:
    REFRESH_TIME_MS = 3

    def __init__(self, form):
        # Load Model
        self.face_detector = FaceDetector(MODEL_PATH_TPU, tpu=True)
        self.face_recognizer = FaceRecognizer(REC_MODEL_PATH_TPU, tpu=True, mask=True)

        # Initialize Camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Design Resources for Window Form
        self.FONT1 = tkFont.Font(form, family = 'DejaVu Sans', size = 14, weight = 'bold')
        self.FONT2 = tkFont.Font(form, family = 'DejaVu Sans', size = 10, weight = 'bold')
        self.FONT3 = tkFont.Font(form, family = 'DejaVu Sans', size = 8)
        self.BUTTON_ON  = PhotoImage(file = "switch-on.png")
        self.BUTTON_OFF = PhotoImage(file = "switch-off.png")

        ### CameraView
        self.cam_view = Label(form, width=CAMERA_WIDTH, height=CAMERA_HEIGHT)
        self.cam_view.pack(side="left", fill=BOTH, expand=False)
        ### Right Panel
        self.r_panel = PanedWindow(form)
        self.r_panel.pack(side="left", fill=BOTH, expand=True)
        ###### Title
        lable_title = Label(self.r_panel, text="FUnLocker v1.0", anchor='center', font=self.FONT2)
        lable_title.pack(side="top", fill="x", expand=False)
        #r_panel.add(lable_title)

        ###### Button - Toggle Detection
        self.btn_detection = Button(self.r_panel, image = self.BUTTON_ON, bd = 0, command = self.toggle_detection)
        self.btn_detection.pack(side="top", fill="x", expand=False, pady = 20)

        ###### Lock State
        self.lable_lock_state = Label(self.r_panel, anchor='center', font=self.FONT1, pady=4)
        self.lable_lock_state.pack(side="bottom", fill="x", expand=False)
        #r_panel.add(self.lable_lock_state)
        
        # Redraw
        self.cam_view.after(self.REFRESH_TIME_MS, self.show_frames)


    def cvt_point(self, rect):
        x1, y1, x2, y2 = rect[0], rect[1], rect[2], rect[3]
        pt1 = (int(x1 * CAMERA_WIDTH / WIDTH), int(y1 * CAMERA_HEIGHT / HEIGHT))
        pt2 = (int(x2 * CAMERA_WIDTH / WIDTH), int(y2 * CAMERA_HEIGHT / HEIGHT))
        return pt1, pt2
    

    # Define switch function
    def toggle_detection(self):
        if mode_state == STATE_VIEW:
            mode_state = STATE_DETECT_ONLY
            self.btn_detection.config(image = self.BUTTON_ON)
        else:
            mode_state = STATE_VIEW
            self.btn_detection.config(image = self.BUTTON_OFF)


    def toggle_lockstatus(self):
        if lock_state:
            lock_state = False
        else:
            lock_state = True
    

    def reflect_status(self):
        if mode_state == STATE_VIEW:
            self.btn_detection.config(image = self.BUTTON_OFF)
        else:
            self.btn_detection.config(image = self.BUTTON_ON)

        if lock_state:
            self.lable_lock_state.config(text="Locked", bg='#FF0000')
        else:
            self.lable_lock_state.config(text="Unlocked", bg='#00FF00')


    def show_frames(self):
        self.reflect_status()

        # COMMON [mode_state : STATE_VIEW,...]
        src_image = cv2.flip(self.cap.read()[1], 1)  # flip the camera
        dst_image = cv2.cvtColor(src_image, cv2.COLOR_BGR2RGB)
        
        # COMMON [mode_state : STATE_DETECT_ONLY, STATE_CAPTURE, STATE_RECOGNITION]
        if mode_state:
            rgb_img = cv2.resize(src_image, (WIDTH, HEIGHT))  # resize the images
            rgb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2RGB).astype('float32')
            rgb_norm = (rgb_img / 255) - 0.5

            # detection [mode_state : STATE_DETECT_ONLY, STATE_CAPTURE, STATE_RECOGNITION]
            pred_bbox_pixel, pred_ldmk_pixel, pred_prob = self.face_detector.detect_face(rgb_norm)

            for bbox in pred_bbox_pixel:
                pt1, pt2 = self.cvt_point(bbox)
                cv2.rectangle(dst_image, pt1, pt2, (0, 0, 255), 2)

        # COMMON [mode_state : STATE_VIEW,...]
        # Drawing Cam Image
        imgtk = ImageTk.PhotoImage(image=Img.fromarray(dst_image))
        self.cam_view.imgtk = imgtk
        self.cam_view.configure(image=imgtk)
        self.cam_view.after(self.REFRESH_TIME_MS, self.show_frames)


def main():
    # Create an instance of TKinter Window or frame
    winform = Tk()

    # Set the size of the window
    winform.attributes('-fullscreen', True)
    winform.geometry("800x480")

    # Define an event to close the window
    def close_win(e):
        winform.destroy()

    # Bind the ESC key with the callback function
    winform.bind('<Escape>', lambda e: close_win(e))
    winform.bind('q', lambda e: close_win(e))

    # Start MainLoop
    mainWindow = MainWindow(winform)
    winform.mainloop()


if __name__ == "__main__":
    main()
