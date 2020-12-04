# MIT License
# Copyright (c) 2019,2020 JetsonHacks
# See license in root folder
# CSI_Camera is a class which encapsulates an OpenCV VideoCapture element
# The VideoCapture element is initialized via a GStreamer pipeline
# The camera is read in a separate thread 
# The class also tracks how many frames are read from the camera;
# The calling application tracks the frames_displayed

# Let's use a repeating Timer for counting FPS
import cv2 as cv2
import threading

class RepeatTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class CSI_Camera:

    def __init__ (self) :
        # Initialize instance variables
        # OpenCV video capture element
        self.video_capture = None
        # The last captured image from the camera
        self.frame = None
        self.grabbed = False
        # The thread where the video capture runs
        self.read_thread = None
        self.read_lock = threading.Lock()
        self.running = False
        self.fps_timer=None
        self.frames_read=0
        self.frames_displayed=0
        self.last_frames_read=0
        self.last_frames_displayed=0


    def open(self, gstreamer_pipeline_string):
        try:
            self.video_capture = cv2.VideoCapture(
                gstreamer_pipeline_string, cv2.CAP_GSTREAMER
            )
            
        except RuntimeError:
            self.video_capture = None
            print("Unable to open camera")
            print("Pipeline: " + gstreamer_pipeline_string)
            return
        # Grab the first frame to start the video capturing
        self.grabbed, self.frame = self.video_capture.read()

    def start(self):
        if self.running:
            print('Video capturing is already running')
            return None
        # create a thread to read the camera image
        if self.video_capture != None:
            self.running=True
            self.read_thread = threading.Thread(target=self.updateCamera)
            self.read_thread.start()
        return self

    def stop(self):
        self.running=False
        self.read_thread.join()

    def updateCamera(self):
        # This is the thread to read images from the camera
        while self.running:
            try:
                grabbed, frame = self.video_capture.read()
                with self.read_lock:
                    self.grabbed=grabbed
                    self.frame=frame
                    self.frames_read += 1
            except RuntimeError:
                print("Could not read image from camera")
        # FIX ME - stop and cleanup thread
        # Something bad happened
        

    def read(self):
        with self.read_lock:
            frame = self.frame.copy()
            grabbed=self.grabbed
        return grabbed, frame

    def release(self):
        if self.video_capture != None:
            self.video_capture.release()
            self.video_capture = None
        # Kill the timer
        self.fps_timer.cancel()
        self.fps_timer.join()
        # Now kill the thread
        if self.read_thread != None:
            self.read_thread.join()

    def update_fps_stats(self):
        self.last_frames_read=self.frames_read
        self.last_frames_displayed=self.frames_displayed
        # Start the next measurement cycle
        self.frames_read=0
        self.frames_displayed=0

    def start_counting_fps(self):
        self.fps_timer=RepeatTimer(1.0,self.update_fps_stats)
        self.fps_timer.start()

    @property
    def gstreamer_pipeline(self):
        return self._gstreamer_pipeline

    # Currently there are setting frame rate on CSI Camera on Nano through gstreamer
    # Here we directly select sensor_mode 3 (1280x720, 59.9999 fps)
    def create_gstreamer_pipeline(
        self,
        sensor_id=0,
        sensor_mode=3,
        display_width=1280,
        display_height=720,
        framerate=60,
        flip_method=0,
    ):
        self._gstreamer_pipeline = (
            "nvarguscamerasrc sensor-id=%d sensor-mode=%d ! "
            "video/x-raw(memory:NVMM), "
            "format=(string)NV12, framerate=(fraction)%d/1 ! "
            "nvvidconv flip-method=%d ! "
            "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
            "videoconvert ! "
            "video/x-raw, format=(string)BGR ! appsink"
            % (
                sensor_id,
                sensor_mode,
                framerate,
                flip_method,
                display_width,
                display_height,
            )
        )

# Author: Kamil Goś

class LineFollowerCamera():
    def __init__(self, show_fps, crop_left, crop_right, crop_top, crop_bottom):
        self.show_fps = show_fps
        self.crop_left = crop_left
        self.crop_right = crop_right
        self.crop_top = crop_top
        self.crop_bottom = crop_bottom
        self.middle_point = int((crop_right-crop_left)/2)
        self.DISPLAY_WIDTH=640
        self.DISPLAY_HEIGHT=360
        self.SENSOR_MODE_720=3
        self.my_camera = None
        self.windows = []
        self.counting_fps = False
        self.font_face = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.5
        self.font_color = (255,255,255)
        self.ready = True

    # Initialize camera
    def initialize_camera(self):
        self.my_camera = CSI_Camera()
        self.my_camera.create_gstreamer_pipeline(
            sensor_id=0,
            sensor_mode=self.SENSOR_MODE_720,
            framerate=30,
            flip_method=2,
            display_height=self.DISPLAY_HEIGHT,
            display_width=self.DISPLAY_WIDTH,)   
        self.my_camera.open(self.my_camera.gstreamer_pipeline)
        self.my_camera.start()
        self.my_camera.start_counting_fps()
        self.counting_fps = True

        if (not self.my_camera.video_capture.isOpened()):
        # Cameras did not open, or no camera attached
            print("Unable to open any cameras")
            SystemExit(0)
        else:
            self.ready = True
            print("Camera ready...")

    def return_state(self):
        return self.ready

    def return_middle_point(self):
        return self.middle_point

    def plot_fps(self, img):
        if self.counting_fps is True:
            cv2.putText(
                img=img,
                text="Frames Displayed (PS): "+str(int(self.my_camera.last_frames_displayed/len(self.windows))),
                org=(10,20),
                fontFace=self.font_face,
                fontScale=self.font_scale,
                color=self.font_color,
                thickness=1,
                lineType=cv2.LINE_AA)
            cv2.putText(
                img=img,
                text="Frames Read (PS): "+str(self.my_camera.last_frames_read),
                org=(10,40),
                fontFace=self.font_face,
                fontScale=self.font_scale,
                color=self.font_color,
                thickness=1,
                lineType=cv2.LINE_AA)
        else:
            print("Unable to print fps. Counting FPS is: ", self.counting_fps)

    # opens new window to show frame as picture
    def open_new_window(self, win_name):
        self.windows.append(win_name)
        cv2.namedWindow(win_name, cv2.WINDOW_AUTOSIZE)
        if cv2.getWindowProperty(win_name, 0) >= 0:
            print("Window: ", win_name, " ready...")
        else:
            print("Unable to open window: ", win_name)



    def create_trackbar(self, win_name, tb_name, low, high):
        cv2.createTrackbar(tb_name, win_name, low, high, nothing)

    def get_trackbar_pos(self, tb_name, win_name):
        return cv2.getTrackbarPos(tb_name, win_name)

    def close_camera(self):
        self.my_camera.stop()
        self.my_camera.release()
        cv2.destroyAllWindows()
        print("Camera closed...")

    def show_image(self, win_name, img):
        if win_name in self.windows:
            if cv2.getWindowProperty(win_name, 0) >= 0 :
                cv2.imshow(win_name, img)
                self.my_camera.frames_displayed += 1
            else:
                print("Problem with window: ", win_name)
        else:
            print("Window: ", win_name, " is NOT opend. Available windows: ", self.windows)

    # Read a frame from the camera, and draw the FPS on the image if desired
    # Return an image
    def read_frame(self):
        _ , frame=self.my_camera.read()
        if self.show_fps:
            self.plot_fps(frame)
        return frame

    def extract_line(self, img, TB_SHOW, TB_T_L, TB_T_U):
        oryginal = img.copy()
        cv2.line(oryginal, (self.crop_left, self.crop_top), (self.crop_right, self.crop_top), (0, 0, 255), 1)
        cv2.line(oryginal, (self.crop_left, self.crop_bottom), (self.crop_right, self.crop_bottom), (0, 0, 255), 1)
        cv2.line(oryginal, (self.middle_point, self.crop_top), (self.middle_point, self.crop_bottom), (0, 255, 0), 2)
        

        img = img[self.crop_top:self.crop_bottom, self.crop_left:self.crop_right]
        frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame, (11,11), 0)
        # _, frame = cv2.threshold(frame, TB_THRESH, 255, cv2.THRESH_BINARY_INV)
        frame = cv2.inRange(frame, TB_T_L, TB_T_U)
        frame = cv2.erode(frame, None, iterations=3)
        frame = cv2.dilate(frame, None, iterations=3)
        frame = cv2.bitwise_not(frame)
        contours, hierarchy = cv2.findContours(frame, 1, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            try:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])+self.crop_top
                error = cx-self.middle_point
            except:
                cx = None
                print("Centroid error")
            
            if cx != None:
                if TB_SHOW == 0:
                    cv2.drawContours(img, contours, -1, (0, 255, 0), 1)
                    cv2.line(oryginal, (cx, self.crop_top), (cx, self.crop_bottom), (255, 0, 0), 1)
                    cv2.line(oryginal, (self.crop_left, cy), (self.crop_right, cy), (255, 0, 0), 1)
            
                cv2.circle(oryginal, (cx, cy), 5, (0,255,0), 3)
                cv2.line(oryginal, (cx,cy), (self.middle_point, cy), (0, 0, 255), 2)
                cv2.putText(img=oryginal,
                    text=str(error),
                    org=(int((cx+self.middle_point)/2),cy-10),
                    fontFace=self.font_face,
                    fontScale=1,
                    color=(0,0,255),
                    thickness=1,
                    lineType=cv2.LINE_AA)
        else:
            cx = None
        return frame, img, oryginal, cx

def nothing(x):
    pass    


if __name__ == "__main__":
    camera = LineFollowerCamera(show_fps=True,
                                crop_left = 0,
                                crop_right = 640,
                                crop_top = 200,
                                crop_bottom = 340)
    camera.initialize_camera()
    print("STATE: ", camera.return_state())
    print("MIDDLE POINT: ", camera.return_middle_point())

    camera.open_new_window("ORYGINAL")
    cv2.moveWindow("ORYGINAL", 100,100)
    camera.create_trackbar("ORYGINAL", "SHOW", 0,2)
    camera.create_trackbar("ORYGINAL", "LOWER", 1, 255)
    camera.create_trackbar("ORYGINAL", "UPPER", 1, 255)
    
    camera.open_new_window("LINE EXTRACTION")
    cv2.moveWindow("LINE EXTRACTION", 750,100)

    camera.open_new_window("FEATURE EXTRACTION")
    cv2.moveWindow("FEATURE EXTRACTION", 750,300)

    while True:
        try:
            frame = camera.read_frame()
            TB_SHOW = cv2.getTrackbarPos('SHOW', 'ORYGINAL')
            TB_T_L = cv2.getTrackbarPos('LOWER', 'ORYGINAL')
            TB_T_U = cv2.getTrackbarPos('UPPER', 'ORYGINAL')
            binary, features, oryginal, cx  = camera.extract_line(frame, TB_SHOW, TB_T_L, TB_T_U)
            
            if TB_SHOW == 0:
                camera.show_image("LINE EXTRACTION",binary)
                camera.show_image("FEATURE EXTRACTION", features)

            camera.show_image("ORYGINAL",oryginal)

            keyCode = cv2.waitKey(5) & 0xFF
            # Stop the program on the ESC key
            if keyCode == 27:
                break
        except Exception as ex:
            print("STH WRONG: ", ex)
            break
    camera.close_camera()
    exit()

