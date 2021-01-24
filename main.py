# Project: Jetson Nano based LineFollower with image processing
# Author: Kamil Goś
# Version: 1.0
# https://github.com/KamilGos/JetsonLinefollower

from camera import LineFollowerCamera
from PID import PID
from pwm_driver import Motors, Tilt
import cv2 as cv2
import time
import traceback

if __name__=="__main__":
    try:
        cam = LineFollowerCamera(show_fps=True,
                                    crop_left = 0,
                                    crop_right = 640,
                                    crop_top = 200,
                                    crop_bottom = 340)
        cam.initialize_camera()
        motors  = Motors()
        tilt = Tilt()
        pid = PID(cam.return_middle_point())

        cam.open_new_window("ORYGINAL")
        cv2.moveWindow("ORYGINAL", 100,100)
        print(cv2.getWindowImageRect("ORYGINAL"))
        cam.create_trackbar("ORYGINAL", "SHOW", 0,2)
        cam.create_trackbar("ORYGINAL", "LOWER", 1, 255)
        cam.create_trackbar("ORYGINAL", "UPPER", 1, 255)
        # cam.create_trackbar("ORYGINAL", "THRESH", 1, 255)
        cam.create_trackbar("ORYGINAL", "KP", 0, 1000)
        # cam.create_trackbar("ORYGINAL", "KI", 0, 100)
        cam.create_trackbar("ORYGINAL", "KD", 0, 1000)
        cam.create_trackbar("ORYGINAL", "MOTORS", 0, 30000)

        cam.open_new_window("LINE EXTRACTION")
        cv2.moveWindow("LINE EXTRACTION", 750, 100)
        cam.open_new_window("FEATURE EXTRACTION")  
        cv2.moveWindow("FEATURE EXTRACTION", 750, 300)

        print("*"*20)
        print("CAMERA: {} \n TILT: {} \n MOTORS: {} \n PID: {}".format(cam.return_state(), tilt.return_state(), motors.return_state(), True))
        print("*"*20)
        
        time.sleep(1)

        while True:
            try:
                frame = cam.read_frame()
                TB_SHOW = cv2.getTrackbarPos('SHOW', 'ORYGINAL')
                TB_T_L = cv2.getTrackbarPos('LOWER', 'ORYGINAL')
                TB_T_U = cv2.getTrackbarPos('UPPER', 'ORYGINAL')
                
                binary, features, oryginal, possition = cam.extract_line(frame, TB_SHOW, TB_T_L, TB_T_U)
                
                if TB_SHOW == 0:
                    cam.show_image("LINE EXTRACTION",binary)
                    cam.show_image("FEATURE EXTRACTION", features)
                cam.show_image("ORYGINAL",oryginal)


                TB_KP = cv2.getTrackbarPos('KP', 'ORYGINAL')/1000
                # TB_KI = cv2.getTrackbarPos('KI', 'ORYGINAL')/1000
                TB_KD = cv2.getTrackbarPos('KD', 'ORYGINAL')/100
                TB_MOTORS = cv2.getTrackbarPos("MOTORS", "ORYGINAL")

                pid.update_factors(KP=TB_KP, KI=0, KD=TB_KD)
                pid.print_factors()

                if possition != None:
                    pid.calcualte_PID(possition)
                    control = pid.return_control()
                    if TB_MOTORS > 0:
                        motors.bothForward(TB_MOTORS)
                    else:
                        motors.bothStop()
                    print("CONTROL: ", control)                    
                    print("TILT: ", tilt.setTilt(-control))
                else:
                    motors.bothStop()
                    print("STOP")

                keyCode = cv2.waitKey(5) & 0xFF
                # Stop the program on the ESC key
                if keyCode == 27:
                    break
            except Exception as err:
                print("STH WRONG: ", err)
                traceback.print_tb(err.__traceback__)
                break
    except Exception as err:
        print("STH WRONG 2: ", err)
        traceback.print_tb(err.__traceback__)
    
    # except Exception as ex:
    #             print("STH WRONG: ", ex)
    cam.close_camera()
    exit()


 