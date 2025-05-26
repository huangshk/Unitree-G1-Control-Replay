import os
import time
import json

import tkinter
from tkinter import ttk
import threading

from unitree_sdk2py.core.channel import ChannelFactoryInitialize

from g1_header import *
from g1_body import LowStateSubscriber, LowCmdPublisher, LowCmdInit
from g1_hand import HandStateSubscriber, HandCmdPublisher, HandCmdInit

class Replay:
    def __init__(self,
                 domain,
                 netface,
                 control_dt = 0.01,
                 num_target = 10,
                 path_snapshot = "snapshot",
                 path_default = "snapshot/default.json"):
        #
        ##
        self.control_dt = control_dt
        self.num_target = num_target
        self.path_snapshot = path_snapshot
        with open(path_default) as default_file:
            self.default_set = json.load(default_file)
        #
        ChannelFactoryInitialize(domain, netface)
        
        self.low_state_sub = LowStateSubscriber()
        time.sleep(0.1)
        self.low_state_init = self.low_state_sub.low_state


        self.body_motors = [motor_id for (motor_id, _) in G1Body.__dict__.items() if (motor_id[0] != "_" and motor_id != "kNotUsedJoint")]



        
        self.low_cmd_pub = LowCmdPublisher()
        self.low_cmd = LowCmdInit(self.low_state_init.mode_machine).low_cmd

        #
        self.init_panel()
        self.ready = False

        self.thread_control = threading.Thread(target = self.control_thread)


    #
    ##
    def init_panel(self):
        #
        ##
        self.panel = tkinter.Tk(className = " Imperial AESE G1 Replay ")
        #
        self.frame = ttk.Frame(self.panel, padding = 20)
        self.frame.grid()
        #
        font_title = ("Arial", 14, "bold")
        font_content = ("Arial", 12, "bold")
        self.panel.option_add('*TCombobox*Listbox.font', font_content)
        
        self.button_run = ttk.Button(self.frame, text = "Run", command = self.handler_run)
        self.button_run.grid(column = 1, row = self.num_target + 2)
        #
        self.button_reset = ttk.Button(self.frame, text = "Reset", command = self.handler_reset)
        self.button_reset.grid(column = 2, row = self.num_target + 2)
        
        ttk.Label(self.frame, text = "Target", font = font_title).grid(column = 1, row = 0, pady = 2)
        ttk.Label(self.frame, text = "Duration (s)", font = font_title).grid(column = 2, row = 0, pady = 2)
        ttk.Label(self.frame, text = "Repeat", font = font_title).grid(column = 3, row = 0, pady = 2)

        target_json_list = os.listdir(self.path_snapshot)
        target_json_list.sort()

        self.target_box_list = [ttk.Combobox(self.frame, width = 100, values = target_json_list, font = font_content) for _ in range(self.num_target)]

        self.duration_box_list = [ttk.Entry(self.frame, justify = tkinter.CENTER, font = font_content) for _ in range(self.num_target)]
        self.repeat_box_list = [ttk.Entry(self.frame, justify = tkinter.CENTER, font = font_content) for _ in range(self.num_target)]

        for var_i in range(self.num_target):
            
            ttk.Label(self.frame, text=var_i, font = font_content).grid(column = 0, row = var_i + 1, padx = 10)

            self.target_box_list[var_i].grid(column = 1, row = var_i + 1, pady = 10, padx = 10)

            self.duration_box_list[var_i].grid(column = 2, row = var_i + 1, pady = 10, padx = 10)
            self.repeat_box_list[var_i].grid(column = 3, row = var_i + 1, pady = 10, padx = 10)
            # duration_box_list[var_i].insert(0, "1.0")
            # print(duration_box_list[var_i].get())

    #
    ##
    def handler_run(self):
        #
        ##
        self.button_reset["state"] = tkinter.DISABLED
        #
        # target_dict_list = []
        # duration_list = []
        #
        # for var_i in range(self.num_target):

            # if self.target_box_list[var_i].get() != "":

                # with open(self.path_snapshot + "/" + self.target_box_list[var_i].get()) as file:

                    # targe_dict = json.load(file)

                    # target_dict_list.append(targe_dict)
                #
                # if self.duration_box_list[var_i].get() != "":
                    #
                    # duration_list.append(float(self.duration_box_list[var_i].get()))
                #
                # else:
                    # duration_list.append(1.0)

        # assert(len(target_dict_list) == len(duration_list))
        #
        # target_q_array = []
        #
        # for targe_dict, duration in zip(target_dict_list, duration_list):
            
            # target_q = [targe_dict["low_cmd"]["motor_cmd"][motor_i]["q"] for motor_i in range(len(self.body_motors))]

            # print(target_q, duration)
            # time.sleep(1)

            # self.forward(target_q, duration)

        var_i = 0
        while var_i < self.num_target:
            
            if self.target_box_list[var_i].get() != "":

                with open(self.path_snapshot + "/" + self.target_box_list[var_i].get()) as file:

                    targe_dict = json.load(file)

                    target_q = [targe_dict["low_cmd"]["motor_cmd"][motor_i]["q"] for motor_i in range(len(self.body_motors))]
                #
                if self.duration_box_list[var_i].get() != "":
                    #
                    duration = float(self.duration_box_list[var_i].get())
                #
                else:
                    duration = 1.0

                self.forward(target_q, duration)

            if self.repeat_box_list[var_i].get() != "" and int(self.repeat_box_list[var_i].get()) < self.num_target:
                var_i = int(self.repeat_box_list[var_i].get())
            else:
                var_i = var_i + 1

        # for target_i in range(len(target_dict_list)):
        #     targe_dict, duration = target_dict_list[target_i], duration_list[target_i]
        #     target_q = [targe_dict["low_cmd"]["motor_cmd"][motor_i]["q"] for motor_i in range(len(self.body_motors))]
        #     self.forward(target_q, duration)


        self.button_reset["state"] = tkinter.NORMAL

    #
    ##
    def handler_reset(self):
        #
        ##
        self.button_run["state"] = tkinter.DISABLED
        #
        target_q = [self.default_set["low_cmd"]["motor_cmd"][motor_i]["q"] for motor_i in range(len(self.body_motors))]
        #
        # print(len(target_q))
        #
        self.forward(target_q, 1)
        #
        self.button_run["state"] = tkinter.NORMAL

    #
    ##
    def forward(self,
                target_q: list,
                duration: float):
        
        if duration < 1.0: duration = 1.0

        num_step = int(duration / self.control_dt) 

        if self.ready:
            source_q = [self.low_cmd.motor_cmd[motor_i].q for motor_i in range(len(self.body_motors))]
        else:
            source_q = [self.low_state_sub.low_state.motor_state[motor_i].q for motor_i in range(len(self.body_motors))]
        # 
        #
        # for var_i, _ in enumerate(self.body_motors):
            #
            # source_q.append(self.low_state_sub.low_state.motor_state[var_i].q)

        for var_t in range(num_step):
            #
            for var_i, _ in enumerate(self.body_motors):

                self.low_cmd.motor_cmd[var_i].q = source_q[var_i] + (target_q[var_i] - source_q[var_i]) / num_step * (var_t + 1)

            self.ready = True
            time.sleep(self.control_dt)
        #
        for var_i, _ in enumerate(self.body_motors):

            self.low_cmd.motor_cmd[var_i].q = target_q[var_i]


    #
    ##
    def control_thread(self):
        #
        ##
        while True:
            #
            ## body
            if self.ready:
                #
                self.low_cmd_pub.publish(self.low_cmd)
            #
            time.sleep(self.control_dt)

    #
    ##
    def start(self):
        #
        ##
        self.thread_control.start()
        self.handler_reset()
        self.panel.mainloop()


#
##
if __name__ == "__main__":
    #
    ##
    panel = Replay(0, "eno1")
    panel.start()
        