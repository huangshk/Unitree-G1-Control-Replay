#
##
import os
import time
import json
import tkinter
from tkinter import ttk
import threading
#
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
#
from g1_header import *
from g1_body import LowStateSubscriber, LowCmdPublisher, LowCmdInit, ArmSdkPublisher
from g1_hand import HandStateSubscriber, HandCmdPublisher, HandCmdInit

#
##
class Replay:
    #
    ##
    def __init__(self,
                 domain,
                 netface,
                 control_dt = 0.005,
                 num_target = 10,
                 default_duration = 0.5,
                 path_snapshot = "snapshot",
                 path_default = "snapshot/default.json"):
        #
        ##
        self.control_dt = control_dt
        self.num_target = num_target
        self.default_duration = default_duration
        self.path_snapshot = path_snapshot
        with open(path_default) as default_file:
            self.default_set = json.load(default_file)
        #
        ChannelFactoryInitialize(domain, netface)
        #
        self.low_state_sub = LowStateSubscriber()
        time.sleep(0.1)
        self.low_state_init = self.low_state_sub.low_state
        #
        ##
        self.low_cmd_pub = LowCmdPublisher()
        # self.low_cmd_pub = ArmSdkPublisher()
        self.low_cmd = LowCmdInit(self.low_state_init.mode_machine).low_cmd
        #
        self.hand_cmd_pub = HandCmdPublisher()
        self.hand_l_cmd = HandCmdInit().hand_cmd
        self.hand_r_cmd = HandCmdInit().hand_cmd
        #
        self.init_panel()
        self.flag_ready = False
        self.flag_run = False
        #
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
        ttk.Label(self.frame, text = "Repeat", font = font_title).grid(column = 5, row = 0, pady = 2)
        ttk.Label(self.frame, text = "Body", font = font_title).grid(column = 3, row = 0, pady = 2)
        ttk.Label(self.frame, text = "Hand", font = font_title).grid(column = 4, row = 0, pady = 2)

        target_json_list = os.listdir(self.path_snapshot)
        target_json_list.sort(reverse = True)
        target_json_list.insert(0, "hold")

        self.target_box_list = [ttk.Combobox(self.frame, width = 100, values = target_json_list, font = font_content) for _ in range(self.num_target)]

        self.duration_box_list = [ttk.Entry(self.frame, justify = tkinter.CENTER, font = font_content) for _ in range(self.num_target)]
        self.repeat_box_list = [ttk.Entry(self.frame, justify = tkinter.CENTER, font = font_content) for _ in range(self.num_target)]

        self.enable_body_flag = [tkinter.BooleanVar(value = False) for _ in range(self.num_target)]
        self.enable_body_list = [ttk.Checkbutton(self.frame, variable = enable_body, onvalue = True, offvalue = False) for enable_body in self.enable_body_flag]
        
        self.enable_hand_flag = [tkinter.BooleanVar(value = False) for _ in range(self.num_target)]
        self.enable_hand_list = [ttk.Checkbutton(self.frame, variable = enable_hand, onvalue = True, offvalue = False) for enable_hand in self.enable_hand_flag]
        #
        for var_i in range(self.num_target):
            #
            ttk.Label(self.frame, text = var_i, font = font_content).grid(column = 0, row = var_i + 1, padx = 10)
            self.target_box_list[var_i].grid(column = 1, row = var_i + 1, pady = 10, padx = 10)
            self.duration_box_list[var_i].grid(column = 2, row = var_i + 1, pady = 10, padx = 10)
            self.repeat_box_list[var_i].grid(column = 5, row = var_i + 1, pady = 10, padx = 10)
            self.enable_body_list[var_i].grid(column = 3, row = var_i + 1, pady = 10, padx = 20)
            self.enable_hand_list[var_i].grid(column = 4, row = var_i + 1, pady = 10, padx = 20)

    #
    ##
    def handler_run(self):
        #
        ##
        thread_run = threading.Thread(target = self.run_thread)
        self.flag_run = True
        thread_run.start()

    #
    ##
    def run_thread(self):
        #
        ##
        var_i = 0
        #
        while var_i < self.num_target:
            #
            if self.target_box_list[var_i].get().split(".")[-1] == "json":
                #
                with open(self.path_snapshot + "/" + self.target_box_list[var_i].get()) as file:

                    targe_dict = json.load(file)
                #
                if self.enable_body_flag[var_i].get():
                    
                    target_q = [targe_dict["low_cmd"]["motor_cmd"][motor_i]["q"] for motor_i in range(G1NumBodyJoint)]
                    #
                    if self.duration_box_list[var_i].get() != "":
                        #
                        duration = float(self.duration_box_list[var_i].get())
                    #
                    else:
                        duration = self.default_duration
                    #
                    self.forward(target_q, duration)
                #
                if self.enable_hand_flag[var_i].get():
                    #
                    hand_l_target_q = [targe_dict["hand_l_cmd"]["cmds"][motor_i]["q"] for motor_i in range(G1NumHandJoint)]
                    hand_r_target_q = [targe_dict["hand_r_cmd"]["cmds"][motor_i]["q"] for motor_i in range(G1NumHandJoint)]
                    self.hand(hand_l_target_q, hand_r_target_q)
            #
            elif self.target_box_list[var_i].get() == "hold":
                #
                if self.duration_box_list[var_i].get() != "":
                    #
                    time.sleep(float(self.duration_box_list[var_i].get()))
                else:
                    #
                    time.sleep(self.default_duration)
            #
            ##
            if self.repeat_box_list[var_i].get() != "" and int(self.repeat_box_list[var_i].get()) < self.num_target:

                var_i = int(self.repeat_box_list[var_i].get())
            #
            else:
                #
                var_i = var_i + 1
            #
            ##
            if not self.flag_run: break

    #
    ##
    def handler_reset(self):
        #
        ##
        self.button_run["state"] = tkinter.DISABLED
        #
        self.flag_run = False

        time.sleep(0.5)
        #
        target_q = [self.default_set["low_cmd"]["motor_cmd"][motor_i]["q"] for motor_i in range(G1NumBodyJoint)]
        #
        self.forward(target_q, 2)

        hand_l_target_q = [0.5 for _ in range(G1NumHandJoint)]
        hand_r_target_q = [0.5 for _ in range(G1NumHandJoint)]
        self.hand(hand_l_target_q, hand_r_target_q)
        #
        self.button_run["state"] = tkinter.NORMAL

    #
    ##
    def forward(self,
                target_q: list,
                duration: float):
        
        if duration < self.default_duration: duration = self.default_duration

        num_step = int(duration / self.control_dt) 

        if self.flag_ready:
            source_q = [self.low_cmd.motor_cmd[motor_i].q for motor_i in range(G1NumBodyJoint)]
        else:
            source_q = [self.low_state_sub.low_state.motor_state[motor_i].q for motor_i in range(G1NumBodyJoint)]
        # 
        for var_t in range(num_step):
            #
            for var_i in range(G1NumBodyJoint):

                self.low_cmd.motor_cmd[var_i].q = source_q[var_i] + (target_q[var_i] - source_q[var_i]) / num_step * (var_t + 1)

            self.flag_ready = True
            time.sleep(self.control_dt)
        #
        for var_i in range(G1NumBodyJoint):

            self.low_cmd.motor_cmd[var_i].q = target_q[var_i]

    #
    ##
    def hand(self,
             hand_l_target_q,
             hand_r_target_q):
        #
        ##
        for var_i in range(G1NumHandJoint):
            #
            self.hand_l_cmd.cmds[var_i].q = hand_l_target_q[var_i]
            #
            self.hand_r_cmd.cmds[var_i].q = hand_r_target_q[var_i]

    #
    ##
    def control_thread(self):
        #
        ##
        while True:
            #
            ##
            if self.flag_ready:
                #
                self.low_cmd_pub.publish(self.low_cmd)
                self.hand_cmd_pub.publish_l(self.hand_l_cmd)
                self.hand_cmd_pub.publish_r(self.hand_r_cmd)
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
    replay = Replay(0, "eno1")
    replay.start()
        