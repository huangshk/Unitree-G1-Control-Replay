#
##
import os
import time
import datetime
import copy
import json
import threading
import tkinter
from tkinter import ttk
#
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
#
from g1_header import *
from g1_body import LowStateSubscriber, LowCmdPublisher, LowCmdInit
from g1_hand import HandStateSubscriber, HandCmdPublisher, HandCmdInit

#
##
class Tuner:
    #
    ##
    def __init__(self,
                 domain,
                 netface,
                 control_dt = 0.01,
                 control_range = 100.0,
                 default_duration = 1.0,
                 path_snapshot = "snapshot",
                 path_default = "snapshot/default.json"):
        #
        ##
        self.control_dt = control_dt
        self.control_range = control_range
        self.default_duration = default_duration
        self.path_snapshot = path_snapshot
        with open(path_default) as default_file:
            self.default_set = json.load(default_file)
        #
        ##
        self.body_motors = [motor_id for (motor_id, _) in G1Body.__dict__.items() if (motor_id[0] != "_" and motor_id != "kNotUsedJoint")]
        self.hand_l_motors = ["L_Hand_" + motor_id for (motor_id, _) in G1Hand.L.__dict__.items() if motor_id[0] != "_"]
        self.hand_r_motors = ["R_Hand_" + motor_id for (motor_id, _) in G1Hand.R.__dict__.items() if motor_id[0] != "_"]
        #
        ##
        self.init_panel()
        #
        ##
        ChannelFactoryInitialize(domain, netface)
        #
        self.low_state_sub = LowStateSubscriber()
        self.hand_state_sub = HandStateSubscriber()
        time.sleep(0.1)
        self.low_state_init = self.low_state_sub.low_state
        #
        self.low_cmd_pub = LowCmdPublisher()
        self.low_cmd = LowCmdInit(self.low_state_init.mode_machine).low_cmd
        self.low_cmd_init = LowCmdInit(self.low_state_init.mode_machine).low_cmd
        #
        self.hand_cmd_pub = HandCmdPublisher()
        self.hand_l_cmd = HandCmdInit().hand_cmd
        self.hand_r_cmd = HandCmdInit().hand_cmd
        self.hand_l_cmd_init = HandCmdInit().hand_cmd
        self.hand_r_cmd_init = HandCmdInit().hand_cmd
        #
        ##
        self.thread_control = threading.Thread(target = self.worker_control)
        #
        self.flag_ready = False
        self.flag_reset = False

    #
    ##
    def init_panel(self):
        #
        ##
        self.panel = tkinter.Tk(className = " Imperial AESE G1 Tuner ")
        #
        self.frame_0 = ttk.Frame(self.panel, padding = 20)
        self.frame_1 = ttk.Frame(self.panel, padding = 10)
        self.frame_0.grid()
        self.frame_1.grid()
        #
        # font_title = ("Arial", 16, "bold")
        font_content = ("Arial", 12, "bold")
        self.panel.option_add('*TCombobox*Listbox.font', font_content)

        file_list = os.listdir(self.path_snapshot)
        target_json_list = [target_json for target_json in file_list if target_json.split(".")[-1] in ["json", "jsonscript"]]
        target_json_list.sort(reverse = True)

        self.target_box = ttk.Combobox(self.frame_0, width = 100, values = target_json_list, font = font_content)
        self.target_box.grid(row = 0, column = 0, padx = 10)

        self.button_run = ttk.Button(self.frame_0, text = "Run", command = self.handler_run)
        self.button_run.grid(row = 0, column = 1, padx = 10)
        self.button_snapshot = ttk.Button(self.frame_0, text = "Snapshot", command = self.handler_snapshot)
        self.button_snapshot.grid(row = 0, column = 2, padx = 10)
        self.button_reset = ttk.Button(self.frame_0, text = "Reset", command = self.handler_reset)
        self.button_reset.grid(row = 0, column = 3, padx = 10)

        self.spinbox_dict = {}
        row_per_column = [6, 6, 3, 7, 7, 6, 6]
        #
        ##
        for var_column in range(len(row_per_column)):
            #
            for var_row in range(row_per_column[var_column]):
                #
                ##
                if var_column < 5:
                    index = sum(row_per_column[:var_column]) + var_row 
                    motor_id = self.body_motors[index]
                elif var_column == 5: 
                    index = var_row
                    motor_id = self.hand_l_motors[index]
                elif var_column == 6: 
                    index = var_row
                    motor_id = self.hand_r_motors[index]

                sub_frame = ttk.Frame(self.frame_1, padding = 10, width = 20)
                sub_frame.grid(column = var_column, row = var_row + 1)
                #
                ##
                ttk.Label(sub_frame, text = str(index) + " " + motor_id, 
                          font = font_content).grid(column = 0, row = 1, padx = 10)
                #
                self.spinbox_dict[motor_id] = ttk.Spinbox(sub_frame, from_ = -self.control_range, to_ = self.control_range, 
                                                          increment = 1, width = 10, justify = tkinter.CENTER, 
                                                          command = self.handler_spinbox)
                self.spinbox_dict[motor_id].set(0)
                self.spinbox_dict[motor_id].grid(column = 0, row = 0, padx = 10)

    #
    ##
    def handler_reset(self):
        #
        ##
        self.flag_reset = True
        time.sleep(0.5)
        #
        ##
        target_body_q = [self.default_set["low_cmd"]["motor_cmd"][var_i]["q"] for var_i in range(G1NumBodyJoint)]
        self.forward_body(target_body_q, self.default_duration * 2.0)
        #
        ##
        hand_l_target_q = [0.5 for _ in range(G1NumHandJoint)]
        hand_r_target_q = [0.5 for _ in range(G1NumHandJoint)]
        self.forward_hand(hand_l_target_q, hand_r_target_q)

        for spinbox in self.spinbox_dict.values():  spinbox.set(0)
        #
        for var_i in range(G1NumBodyJoint):
            self.low_cmd_init.motor_cmd[var_i].q = target_body_q[var_i]
        #
        for var_i in range(G1NumHandJoint):
            self.hand_l_cmd_init.cmds[var_i].q = 0.5
            self.hand_r_cmd_init.cmds[var_i].q = 0.5
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
    def handler_snapshot(self):
        #
        ##
        if not self.flag_reset:
            #
            thread_snapshot = threading.Thread(target = self.worker_snapshot)
            thread_snapshot.start()

    #
    ##
    def handler_spinbox(self):
        #
        ##
        if not self.flag_reset:
            #
            thread_spinbox = threading.Thread(target = self.worker_spinbox)
            thread_spinbox.start()

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
        # if self.target_box.get().split(".")[-1] == "json":
        #     #
        #     with open(self.path_snapshot + "/" + self.target_box.get()) as file:

        #         target_dict = json.load(file)
        #     #
        #     ##
        #     target_q = [target_dict["low_cmd"]["motor_cmd"][var_i]["q"] for var_i in range(G1NumBodyJoint)]
        #     self.forward_body(target_q, self.default_duration)
        #     #
        #     hand_l_target_q = [target_dict["hand_l_cmd"]["cmds"][var_i]["q"] for var_i in range(G1NumHandJoint)]
        #     hand_r_target_q = [target_dict["hand_r_cmd"]["cmds"][var_i]["q"] for var_i in range(G1NumHandJoint)]
        #     self.forward_hand(hand_l_target_q, hand_r_target_q)
        #     #
        #     ##
        #     for var_i in range(G1NumBodyJoint):
        #         self.low_cmd_init.motor_cmd[var_i].q = target_dict["low_cmd"]["motor_cmd"][var_i]["q"]
        #     #
        #     for var_i in range(G1NumHandJoint):
        #         self.hand_l_cmd_init.cmds[var_i].q = hand_l_target_q[var_i]
        #         self.hand_r_cmd_init.cmds[var_i].q = hand_r_target_q[var_i]
        #     #
        #     for spinbox in self.spinbox_dict.values():  spinbox.set(0)

        self.run_target_list(target_list = [self.target_box.get()],
                             flag_body_list = [True],
                             flag_hand_list = [True],
                             duration_list = [self.default_duration],
                             repeat_list = [""],
                             flag_body_parent = True,
                             flag_hand_parent = True)
        #
        ##
        for var_i in range(G1NumBodyJoint):
            self.low_cmd_init.motor_cmd[var_i].q = copy.deepcopy(self.low_cmd.motor_cmd[var_i].q)
        #
        for var_i in range(G1NumHandJoint):
            self.hand_l_cmd_init.cmds[var_i].q = copy.deepcopy(self.hand_l_cmd.cmds[var_i].q)
            self.hand_r_cmd_init.cmds[var_i].q = copy.deepcopy(self.hand_r_cmd.cmds[var_i].q)
        #
        for spinbox in self.spinbox_dict.values():  spinbox.set(0)
        
    #
    ##
    def worker_snapshot(self):
        #
        ##
        var_time = str(datetime.datetime.now()).replace("-", "_").replace(" ", "_").replace(".", "_").replace(":", "_")
        #
        snapshot = {}
        #
        snapshot["low_state"] = self.low_state_sub.to_dict(self.low_state_sub.low_state)
        if self.hand_state_sub.hand_l_state is not None:
            snapshot["hand_l_state"] = self.hand_state_sub.to_dict(self.hand_state_sub.hand_l_state)
        if self.hand_state_sub.hand_r_state is not None:
            snapshot["hand_r_state"] = self.hand_state_sub.to_dict(self.hand_state_sub.hand_r_state)
        #
        snapshot["low_cmd"] = self.low_cmd_pub.to_dict(self.low_cmd)
        snapshot["hand_l_cmd"] = self.hand_cmd_pub.to_dict(self.hand_l_cmd)
        snapshot["hand_r_cmd"] = self.hand_cmd_pub.to_dict(self.hand_r_cmd)
        #
        with open(self.path_snapshot + "/" + var_time + ".json", "w", encoding = "utf-8") as file:
            #
            json.dump(snapshot, file, indent = 4)
        #
        ##
        file_list = os.listdir(self.path_snapshot)
        target_json_list = [target_json for target_json in file_list if target_json.split(".")[-1] == "json"]
        target_json_list.sort(reverse = True)
        self.target_box["values"] = target_json_list
        #
        print("Snapshot", var_time)

    #
    ##
    def worker_spinbox(self):
        #
        ##
        for var_i, motor_id in enumerate(self.body_motors):
            
            update_body = float(self.spinbox_dict[motor_id].get())

            low_cmd_q = self.low_cmd_init.motor_cmd[var_i].q + update_body / self.control_range * ConstPi # / 2
            #
            self.low_cmd.motor_cmd[var_i].q = low_cmd_q
        #
        ##
        for var_i, motor_id in enumerate(self.hand_l_motors):
            
            update_hand_l = float(self.spinbox_dict[motor_id].get())

            hand_l_q = self.hand_l_cmd_init.cmds[var_i].q + (update_hand_l / self.control_range) / 2

            self.hand_l_cmd.cmds[var_i].q = hand_l_q
        #
        ##
        for var_i, motor_id in enumerate(self.hand_r_motors):
            
            update_hand_r = float(self.spinbox_dict[motor_id].get())

            hand_r_q = self.hand_r_cmd_init.cmds[var_i].q + (update_hand_r / self.control_range) / 2

            self.hand_r_cmd.cmds[var_i].q = hand_r_q

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
                print(target_list[index])
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
                     target_body_q: list,
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

                self.low_cmd.motor_cmd[var_i].q = source_q[var_i] + (target_body_q[var_i] - source_q[var_i]) / num_step * (var_t + 1)

            self.flag_ready = True

            time.sleep(self.control_dt)
        #
        for var_i in range(G1NumBodyJoint):

            self.low_cmd.motor_cmd[var_i].q = target_body_q[var_i]

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
    app_tuner = Tuner(0, "eno1")
    app_tuner.start()
