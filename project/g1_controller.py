

# from tkinter import *
# from tkinter import ttk
# root = Tk()
# frm = ttk.Frame(root, padding=10)
# frm.grid()
# ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
# ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
# root.mainloop()
import time
import tkinter
from tkinter import ttk
import threading

#
##
class Controller:

    #
    ##
    def __init__(self,
                 motor_list = ["left_Arm", "right_arm", "left_shoulder", "right_shoulder"]):
        #
        ##
        self.motor_list = motor_list
        self.motor_scale = {}
        #
        ##
        self.controller = tkinter.Tk(className = " G1 Controller ")
        self.frame = ttk.Frame(self.controller, padding = 10)
        self.frame.grid()
        #
        ##
        for var_i, motor_id in enumerate(motor_list):
            #
            ##
            ttk.Label(self.frame, text = motor_id, justify = tkinter.LEFT).grid(column = 0, row = var_i)
            #
            self.motor_scale[motor_id] = tkinter.Scale(self.frame, orient = tkinter.HORIZONTAL, from_ = -100, to_ = 100, length = 1000)
            self.motor_scale[motor_id].grid(column = 1, row = var_i)
        #
        self.get_thread = threading.Thread(target = self.handler_scale)

    #
    ##
    def start(self):
        #
        ##
        self.get_thread.start()
        self.controller.mainloop()


    #
    ##
    def handler_scale(self):
        #
        ##
        while True:
            #
            if True:
                #
                try:
                    motor_values = {}
                    for motor_id in self.motor_list:
                        motor_values[motor_id] = self.motor_scale[motor_id].get()
                    print(motor_values)
                #
                except:
                    break

            time.sleep(0.1)

if __name__ == "__main__":
    #
    ##
    controller = Controller()
    controller.start()