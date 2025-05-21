import time
import tkinter
from tkinter import ttk
import threading
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_

from g1_header import *
from g1_subscribe import LowStateSubscriber
from g1_publish import LowCmdPublisher

#
##
class Controller:

    #
    ##
    def __init__(self,
                 domain,
                 netface,
                 control_range = 1000.0,
                 monitor_dt = 0.1,
                 control_dt = 0.01):
        #
        ##
        ChannelFactoryInitialize(domain, netface)
        #
        self.control_range = control_range
        self.monitor_dt = monitor_dt
        self.control_dt = control_dt
        #
        self.low_state_sub = LowStateSubscriber()
        self.low_cmd_pub = LowCmdPublisher()
        self.low_cmd = unitree_hg_msg_dds__LowCmd_()
        #
        self.motor_list = [motor_id for (motor_id, _) in G1Joint.__dict__.items() if motor_id[0] != "_"]
        self.motor_state_initial = self.low_state_sub.low_state.motor_state
        #
        ##
        self.motor_scale = {}
        self.motor_state_q = {}
        #
        ##
        self.controller = tkinter.Tk(className = " G1 Controller ")
        self.frame = ttk.Frame(self.controller, padding = 20)
        self.frame.grid()
        #
        ttk.Label(self.frame, text = "Control", font = ("", 18)).grid(column = 7, row = 0, pady = 5)
        ttk.Label(self.frame, text = "Monitor", font = ("", 18)).grid(column = 7, row = 10, pady = 5)
        #
        ##
        for var_i, motor_id in enumerate(self.motor_list):
            #
            if var_i < 6: column_i, row_i = 0, 0
            elif var_i < 12: column_i, row_i = 3, 6
            elif var_i < 15: column_i, row_i = 6, 12
            elif var_i < 22: column_i, row_i = 9, 15
            elif var_i < 29: column_i, row_i = 12, 22
            else: break
            #
            ##
            ttk.Label(self.frame, text = motor_id, font = ("", 12)).grid(column = column_i, row = var_i - row_i + 1)
            #
            self.motor_scale[motor_id] = tkinter.Scale(self.frame, orient = tkinter.HORIZONTAL, 
                                                       from_ = -control_range, to_ = control_range, 
                                                       length = 200, showvalue = True)
            #
            self.motor_scale[motor_id].grid(column = column_i + 1, row = var_i - row_i + 1)
            #
            ttk.Label(self.frame, text = "    ").grid(column = column_i + 2, row = var_i - row_i + 1)

            self.motor_state_q[motor_id] = tkinter.StringVar()
            self.motor_state_q[motor_id].set(f"{self.motor_state_initial[var_i].q:.6f}")
            #
            ##
            ttk.Label(self.frame, text = motor_id, font = ("", 12)).grid(column = column_i, row = var_i - row_i + 11 + 1, pady = 5)

            ttk.Label(self.frame, textvariable = self.motor_state_q[motor_id], font = ("", 12)).grid(column = column_i + 1, 
                                                                                                     row = var_i - row_i + 11 + 1)
            
        #
        self.thread_monitor = threading.Thread(target = self.monitor_thread)
        self.thread_control = threading.Thread(target = self.control_thread)

    #
    ##
    def monitor_thread(self):
        #
        ##
        while True:
            #
            ##
            motor_state = self.low_state_sub.low_state.motor_state
            #
            for var_i, motor_id in enumerate(self.motor_list):
                #
                if var_i > 28: break
                #
                self.motor_state_q[motor_id].set(f"{motor_state[var_i].q:.6f}")
            #
            time.sleep(self.monitor_dt)
    
    #
    ##
    def control_thread(self):
        #
        ##
        while True:
            #
            ##
            motor_state = self.low_state.low_state.motor_state
            #
            for var_i, motor_id in enumerate(self.motor_list):
                #
                if var_i > 28: break
                    #
                low_cmd_q = self.motor_state_initial[var_i].q  +  self.motor_scale[motor_id].get() / self.control_range * ConstPi
               
                if low_cmd_q > ConstPi: low_cmd_q = ConstPi
                if low_cmd_q < -ConstPi: low_cmd_q = -ConstPi
                    
                self.low_cmd.mode_pr = 0
                self.low_cmd.motor_cmd[var_i].dq = 0
                self.low_cmd.motor_cmd[var_i].kp = 60
                self.low_cmd.motor_cmd[var_i].kd = 1.5
                self.low_cmd.motor_cmd[var_i].q = low_cmd_q
                self.low_cmd.motor_cmd[var_i].tau = 0

                # if self.motor_scale[motor_id].get() / self.control_range * ConstPi != 0:
                #     print("hhh")
                # print(self.motor_scale[28].get() / self.control_range)
            #
            self.low_cmd_pub.publish(self.low_cmd)
                
            #
            time.sleep(self.control_dt)
            
    #
    ##
    def start(self):
        #
        ##
        self.thread_monitor.start()
        self.thread_control.start()
        self.controller.mainloop()


if __name__ == "__main__":
    #
    ##
    controller = Controller(2, "lo")
    controller.start()

