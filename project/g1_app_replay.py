#
##
import os
import time
import datetime
import json
import threading
import tkinter
from tkinter import ttk
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
                 enable_arm_sdk = False,
                 path_snapshot = "snapshot",
                 path_default = "snapshot/default.json"):
        #
        ##
        self.control_dt = control_dt
        self.num_target = num_target
        self.default_duration = default_duration
        self.enable_arm_sdk = enable_arm_sdk
        self.path_snapshot = path_snapshot
        with open(path_default) as default_file:
            self.default_set = json.load(default_file)
        #
        ##
        self.init_panel()
        #
        ##
        ChannelFactoryInitialize(domain, netface)
        #
        self.low_state_sub = LowStateSubscriber()
        time.sleep(0.1)
        self.low_state_init = self.low_state_sub.low_state
        #
        ##
        if enable_arm_sdk:  self.low_cmd_pub = ArmSdkPublisher()
        else:               self.low_cmd_pub = LowCmdPublisher()
        #
        self.low_cmd = LowCmdInit(self.low_state_init.mode_machine).low_cmd
        #
        self.hand_cmd_pub = HandCmdPublisher()
        self.hand_l_cmd = HandCmdInit().hand_cmd
        self.hand_r_cmd = HandCmdInit().hand_cmd
        #
        self.thread_control = threading.Thread(target = self.worker_control)
        #
        self.flag_ready = False
        self.flag_reset = False

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
        self.button_reset.grid(column = 5, row = self.num_target + 2)
        #
        self.button_export = ttk.Button(self.frame, text = "Export", command = self.handler_export)
        self.button_export.grid(column = 2, row = self.num_target + 2)
        
        ttk.Label(self.frame, text = "Target", font = font_title).grid(column = 1, row = 0, pady = 2)
        ttk.Label(self.frame, text = "Duration (s)", font = font_title).grid(column = 2, row = 0, pady = 2)
        ttk.Label(self.frame, text = "Repeat", font = font_title).grid(column = 5, row = 0, pady = 2)
        ttk.Label(self.frame, text = "Body", font = font_title).grid(column = 3, row = 0, pady = 2)
        ttk.Label(self.frame, text = "Hand", font = font_title).grid(column = 4, row = 0, pady = 2)

        target_path_list = os.listdir(self.path_snapshot)
        target_path_list.sort(reverse = True)
        target_path_list.insert(0, "hold")
        target_path_list.insert(0, "")

        self.target_box_list = [ttk.Combobox(self.frame, width = 100, values = target_path_list, font = font_content) for _ in range(self.num_target)]

        self.duration_box_list = [ttk.Entry(self.frame, justify = tkinter.CENTER, font = font_content) for _ in range(self.num_target)]
        self.repeat_box_list = [ttk.Entry(self.frame, justify = tkinter.CENTER, font = font_content) for _ in range(self.num_target)]

        self.enable_body_bool = [tkinter.BooleanVar(value = False) for _ in range(self.num_target)]
        self.enable_body_list = [ttk.Checkbutton(self.frame, variable = enable_body, onvalue = True, offvalue = False) for enable_body in self.enable_body_bool]
        
        self.enable_hand_bool = [tkinter.BooleanVar(value = False) for _ in range(self.num_target)]
        self.enable_hand_list = [ttk.Checkbutton(self.frame, variable = enable_hand, onvalue = True, offvalue = False) for enable_hand in self.enable_hand_bool]
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
    def extract_panel(self):
        #
        ##
        target_list = [target_box.get() for target_box in self.target_box_list]
        flag_body_list = [enable_body.get() for enable_body in self.enable_body_bool]
        flag_hand_list = [enable_hand.get() for enable_hand in self.enable_hand_bool]
        duration_list = [duration_box.get() for duration_box in self.duration_box_list]
        repeat_list = [repeat_box.get() for repeat_box in self.repeat_box_list]
        #
        return target_list, flag_body_list, flag_hand_list, duration_list, repeat_list

    #
    ##
    def handler_reset(self):
        #
        ##
        self.flag_reset = True
        time.sleep(0.5)
        #
        ##
        target_q = [self.default_set["low_cmd"]["motor_cmd"][motor_i]["q"] for motor_i in range(G1NumBodyJoint)]
        self.forward_body(target_q, 2.0)
        #
        ##
        hand_l_target_q = [0.5 for _ in range(G1NumHandJoint)]
        hand_r_target_q = [0.5 for _ in range(G1NumHandJoint)]
        self.forward_hand(hand_l_target_q, hand_r_target_q)
        #
        ##
        self.flag_reset = False

    #
    ##
    def handler_run(self):
        #
        ##
        if not self.flag_reset:
            #
            thread_run = threading.Thread(target = self.worker_run)
            thread_run.start()

    #
    ##
    def handler_export(self):
        #
        ##
        if not self.flag_reset:
            #
            thread_export = threading.Thread(target = self.worker_export)
            thread_export.start()

    #
    ##
    def worker_control(self):
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
    def worker_run(self):
        #
        ##
        target_list, flag_body_list, flag_hand_list, duration_list, repeat_list = self.extract_panel()
        self.run_target_list(target_list, flag_body_list, flag_hand_list, duration_list, repeat_list)
        
    #
    ##
    def worker_export(self):
        #
        ##
        var_time = str(datetime.datetime.now()).replace("-", "_").replace(" ", "_").replace(".", "_").replace(":", "_")
        #
        ##
        target_list, flag_body_list, flag_hand_list, duration_list, repeat_list = self.extract_panel()
        #
        export_dict = {
            "target_list": target_list,
            "flag_body_list": flag_body_list,
            "flag_hand_list": flag_hand_list,
            "duration_list": duration_list,
            "repeat_list": repeat_list,
        }
        #
        with open(self.path_snapshot + "/" + var_time + ".jsonscript", "w", encoding = "utf-8") as file:
            #
            json.dump(export_dict, file, indent = 4)

        target_path_list = os.listdir(self.path_snapshot)
        target_path_list.sort(reverse = True)
        target_path_list.insert(0, "hold")

        for target_box in self.target_box_list:

            target_box["values"] = target_path_list

        #
        print("Export", var_time)

    # #
    # ##
    # def run(self,
    #         target_list: list,
    #         flag_body_list: list,
    #         flag_hand_list: list,
    #         duration_list: list,
    #         repeat_list: list,
    #         flag_body_parent = True,
    #         flag_hand_parent = True):
    #     '''
    #     flag_body_parent for recursive calls
    #     flag_hand_parent for recursive calls
    #     '''
    #     #
    #     ##
    #     index = 0
    #     #
    #     while index < len(target_list):
    #         #
    #         ##
    #         if self.flag_reset: break
    #         #
    #         ##
    #         if target_list[index].split(".")[-1] == "json":
    #             #
    #             ##
    #             with open(self.path_snapshot + "/" +  target_list[index]) as file:   target_dict = json.load(file)
    #             #
    #             ##
    #             if flag_body_list[index] and flag_body_parent:
                    
    #                 target_q = [target_dict["low_cmd"]["motor_cmd"][var_i]["q"] for var_i in range(G1NumBodyJoint)]

    #                 if duration_list[index] != "":  duration = float(duration_list[index])
    #                 else:                           duration = self.default_duration

    #                 self.forward_body(target_q, duration)
    #             #
    #             ##
    #             if flag_hand_list[index] and flag_hand_parent:
    #                 #
    #                 hand_l_target_q = [target_dict["hand_l_cmd"]["cmds"][var_i]["q"] for var_i in range(G1NumHandJoint)]
    #                 hand_r_target_q = [target_dict["hand_r_cmd"]["cmds"][var_i]["q"] for var_i in range(G1NumHandJoint)]
    #                 self.forward_hand(hand_l_target_q, hand_r_target_q)

    #         #   
    #         ## recursive calls
    #         elif target_list[index].split(".")[-1] == "jsonscript":
    #             #
    #             ##
    #             with open(self.path_snapshot + "/" + target_list[index]) as file:   script_dict = json.load(file)
    #             #
    #             self.run(target_list = script_dict["target_list"], 
    #                      flag_body_list = script_dict["flag_body_list"], 
    #                      flag_hand_list = script_dict["flag_hand_list"], 
    #                      duration_list = script_dict["duration_list"],
    #                      repeat_list = script_dict["repeat_list"],
    #                      flag_body_parent = flag_body_list[index] and flag_body_parent,
    #                      flag_hand_parent = flag_hand_list[index] and flag_hand_parent)
                
    #         #
    #         ##
    #         elif target_list[index] == "hold":
    #             #
    #             if duration_list[index] != "":  time.sleep(float(duration_list[index]))
    #             else:                           time.sleep(self.default_duration)
            
    #         #
    #         ##
    #         if repeat_list[index] != "" and int(repeat_list[index]) < len(target_list):     index = int(repeat_list[index])
    #         #
    #         else:       index = index + 1

    #
    ##
    def run_target_dict(self,
                        target_dict,
                        duration,
                        flag_body,
                        flag_hand):
        #
        ##
        if flag_body:
            #
            target_q = [target_dict["low_cmd"]["motor_cmd"][var_i]["q"] for var_i in range(G1NumBodyJoint)]
            self.forward_body(target_q, duration)
        #
        ##
        if flag_hand:
            #
            hand_l_target_q = [target_dict["hand_l_cmd"]["cmds"][var_i]["q"] for var_i in range(G1NumHandJoint)]
            hand_r_target_q = [target_dict["hand_r_cmd"]["cmds"][var_i]["q"] for var_i in range(G1NumHandJoint)]
            self.forward_hand(hand_l_target_q, hand_r_target_q)

    #
    ##
    def run_target_list(self,
                        target_list,
                        flag_body_list: list,
                        flag_hand_list: list,
                        duration_list: list,
                        repeat_list: list,
                        flag_body_parent = True,
                        flag_hand_parent = True):
        '''
        flag_body_parent for recursive calls
        flag_hand_parent for recursive calls
        '''
        #
        ##
        index = 0
        #
        while index < len(target_list):
            #
            ##
            if self.flag_reset: break
            #
            ##
            if target_list[index].split(".")[-1] == "json":
                #
                with open(self.path_snapshot + "/" +  target_list[index]) as file:   
                    target_dict = json.load(file)
                #
                if duration_list[index] != "":  duration = float(duration_list[index])
                else:                           duration = self.default_duration
                #
                self.run_target_dict(target_dict,
                                     duration,
                                     flag_body = flag_body_list[index] and flag_body_parent,
                                     flag_hand = flag_hand_list[index] and flag_hand_parent)
            #   
            ## recursive calls
            elif target_list[index].split(".")[-1] == "jsonscript":
                #
                with open(self.path_snapshot + "/" + target_list[index]) as file:   
                    script_dict = json.load(file)
                #
                self.run_target_list(target_list = script_dict["target_list"], 
                                     flag_body_list = script_dict["flag_body_list"], 
                                     flag_hand_list = script_dict["flag_hand_list"], 
                                     duration_list = script_dict["duration_list"],
                                     repeat_list = script_dict["repeat_list"],
                                     flag_body_parent = flag_body_list[index] and flag_body_parent,
                                     flag_hand_parent = flag_hand_list[index] and flag_hand_parent)
            #
            ##
            elif target_list[index] == "hold":
                #
                if duration_list[index] != "":  time.sleep(float(duration_list[index]))
                else:                           time.sleep(self.default_duration)

            #
            ##
            if repeat_list[index] != "":
                if int(repeat_list[index]) >= 0 and int(repeat_list[index]) < len(target_list):     
                    index = int(repeat_list[index])
            #
            else:
                index = index + 1

    #
    ##
    def forward_body(self,
                     target_q: list,
                     duration: float):
        #
        ##
        if duration < self.default_duration: duration = self.default_duration
        #
        num_step = int(duration / self.control_dt) 
        #
        ##
        if self.flag_ready:
            #
            source_q = [self.low_cmd.motor_cmd[var_i].q for var_i in range(G1NumBodyJoint)]
        #
        else:
            source_q = [self.low_state_sub.low_state.motor_state[var_i].q for var_i in range(G1NumBodyJoint)]
        # 
        ##
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
    def forward_hand(self,
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
    app_replay = Replay(0, "eno1")
    app_replay.start()
        