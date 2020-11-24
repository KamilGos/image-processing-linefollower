# Project: Jetson Nano based LineFollower with image processing
# Author: Kamil Goś
# Version: 1.0
# https://github.com/KamilGos/JetsonLinefollower

from camera import LineFollowerCamera
from PID import PID
from pwm_driver import Motors, Tilt
import cv2 as cv2
import time


if __name__=="__main__":
    try:
        cam = LineFollowerCamera(show_fps=True,
                                    crop_left = 0,
                                    crop_right = 640,
                                    crop_top = 200,
                                    crop_bottom = 340)
        cam.initialize_camera()
        # Motors  = Motors()
        Tilt = Tilt()
        PID = PID(cam.return_middle_point())


        cam.open_new_window("ORYGINAL")
        cv2.moveWindow("ORYGINAL", 100,100)
        cam.create_trackbar("ORYGINAL", "SHOW", 0,2)
        # cam.create_trackbar("ORYGINAL", "THRESH", 1, 255)
        cam.create_trackbar("ORYGINAL", "KP", 0, 10)
        cam.create_trackbar("ORYGINAL", "KI", 0, 100)
        cam.create_trackbar("ORYGINAL", "KD", 0, 10)
        cam.open_new_window("LINE EXTRACTION")
        cv2.moveWindow("LINE EXTRACTION", 1000, 100)
        print("\n\nALL MODLUES READY\n\n")
        time.sleep(1)


        while True:
            try:
                frame = cam.read_frame()
                TB_SHOW = cv2.getTrackbarPos('SHOW', 'ORYGINAL')
                # TB_THRESH = cv2.getTrackbarPos('THRESH', 'ORYGINAL')
                
                binary, oryginal, possition = cam.extract_line(frame, None, TB_SHOW)
                
                if TB_SHOW == 0:
                    cam.show_image("LINE EXTRACTION",binary)
                cam.show_image("ORYGINAL",oryginal)

                TB_KP = cv2.getTrackbarPos('KP', 'ORYGINAL')/10
                TB_KI = cv2.getTrackbarPos('KI', 'ORYGINAL')/100
                TB_KD = cv2.getTrackbarPos('KD', 'ORYGINAL')

                PID.update_factors(KP=TB_KP, KI=TB_KI, KD=TB_KD)
                PID.print_factors()
                PID.calcualte_PID(possition)
                print("CONTROL: ", PID.return_control())
                Tilt.setTilt(PID.return_control())

                keyCode = cv2.waitKey(5) & 0xFF
                # Stop the program on the ESC key
                if keyCode == 27:
                    break
            except Exception as ex:
                print("STH WRONG: ", ex)
                break
    except Exception as ex:
                print("STH WRONG: ", ex)
    cam.close_camera()
    exit()



    