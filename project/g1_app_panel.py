#
##
import time
import copy
import datetime
import json
import tkinter
from tkinter import ttk
import threading
#
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
#
from g1_header import *
from g1_body import LowStateSubscriber, LowCmdPublisher, LowCmdInit
from g1_hand import HandStateSubscriber, HandCmdPublisher, HandCmdInit

#
##
class Panel:
    #
    ##
    def __init__(self,
                 domain,
                 netface,
                 control_range = 100.0,
                 monitor_dt = 0.1,
                 control_dt = 0.01,
                 default_path = "snapshot/default.json"):
        #
        ##
        self.control_range = control_range
        self.monitor_dt = monitor_dt
        self.control_dt = control_dt
        self.default_path = default_path
        #
        ChannelFactoryInitialize(domain, netface)
        #
        self.low_state_sub = LowStateSubscriber()
        self.hand_state_sub = HandStateSubscriber()
        #
        self.low_state_init = self.low_state_sub.low_state
        #
        self.body_motors = [motor_id for (motor_id, _) in G1Body.__dict__.items() if (motor_id[0] != "_" and motor_id != "kNotUsedJoint")]
        self.hand_l_motors = ["L_Hand_" + motor_id for (motor_id, _) in G1Hand.L.__dict__.items() if motor_id[0] != "_"]
        self.hand_r_motors = ["R_Hand_" + motor_id for (motor_id, _) in G1Hand.R.__dict__.items() if motor_id[0] != "_"]
        #
        self.motor_state_q = {}
        #
        self.panel_scale = {}
        self.panel_scale_cache = {}
        #
        self.low_cmd_pub = LowCmdPublisher()
        self.low_cmd = LowCmdInit(self.low_state_init.mode_machine).low_cmd

        self.hand_cmd_pub = HandCmdPublisher()
        self.hand_l_cmd = HandCmdInit().hand_cmd
        self.hand_r_cmd = HandCmdInit().hand_cmd
        #
        self.init_panel()
        self.handler_reset()
        #
        self.thread_monitor = threading.Thread(target = self.monitor_thread)
        self.thread_control = threading.Thread(target = self.control_thread)

    #
    ##
    def init_panel(self,
                   row_per_column = [6, 6, 3, 7, 7, 6, 6]):
        #
        ##
        self.panel = tkinter.Tk(className = " Imperial AESE G1 Panel ")
        self.frame = ttk.Frame(self.panel, padding = 10)
        self.frame.grid()
        #
        font_title = ("Arial", 16, "bold")
        font_content = ("Arial", 14, "bold")
        #
        ttk.Label(self.frame, text = "Control", font = font_title).grid(column = len(row_per_column)//2, row = 0, pady = 2)
        ttk.Label(self.frame, text = "\nMonitor", font = font_title).grid(column = len(row_per_column)//2, 
                                                                                   row = max(row_per_column) * 2 + 1, pady = 2)
        #
        for motor_id in self.body_motors:   self.motor_state_q[motor_id] = tkinter.StringVar(value = 0)
        for motor_id in self.hand_l_motors:   self.motor_state_q[motor_id] = tkinter.StringVar(value = 0)
        for motor_id in self.hand_r_motors:   self.motor_state_q[motor_id] = tkinter.StringVar(value = 0)
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
                #
                ## control
                self.panel_scale[motor_id] = tkinter.Scale(self.frame, orient = tkinter.HORIZONTAL, 
                                                           from_ = - self.control_range, to_ = self.control_range, 
                                                           length = 250, showvalue = True, resolution = 1)
                #
                self.panel_scale[motor_id].grid(column = var_column, row = var_row * 2 + 1)
                #
                self.panel_scale_cache[motor_id] = 0
                #
                ttk.Label(self.frame, text = str(index) + " " + motor_id, 
                          font = font_content).grid(column = var_column, row = var_row * 2 + 2)
                #
                ## monitor
                ttk.Label(self.frame, textvariable = self.motor_state_q[motor_id], 
                          font = ("Arial", 12)).grid(column = var_column, row = max(row_per_column) * 2 + 1 + var_row * 2 + 1)

                ttk.Label(self.frame, text = str(index) + " " + motor_id + "\n", 
                          font = font_content).grid(column = var_column, row = max(row_per_column) * 2 + 1 + var_row * 2 + 2)
        #
        ##
        ttk.Button(self.frame, text = "Snapshot", command = self.handler_snapshot).grid(column = 0, row = 0)

        ttk.Button(self.frame, text = "Reset", command = self.handler_reset).grid(column = len(row_per_column) - 1, row = 0)
        #
        ##
        self.enable_control = tkinter.BooleanVar(value = False)
        self.button_enable_control = ttk.Checkbutton(self.frame, text = "Enable Control", 
                                                     variable = self.enable_control, command = self.handler_enable_control,
                                                     onvalue = True, offvalue = False)
        self.button_enable_control.grid(column = len(row_per_column)//2 + 1, row = 0)
        
    #
    ##
    def handler_snapshot(self):
        #
        ##
        var_time = str(datetime.datetime.now()).replace("-", "_").replace(" ", "_").replace(".", "_").replace(":", "_")
        #
        snapshot = {}
        #
        snapshot["low_state"] = self.low_state_sub.to_dict(self.low_state_sub.low_state)
        snapshot["hand_l_state"] = self.hand_state_sub.to_dict(self.hand_state_sub.hand_l_state)
        snapshot["hand_r_state"] = self.hand_state_sub.to_dict(self.hand_state_sub.hand_r_state)
        #
        snapshot["low_cmd"] = self.low_cmd_pub.to_dict(self.low_cmd)
        snapshot["hand_l_cmd"] = self.hand_cmd_pub.to_dict(self.hand_l_cmd)
        snapshot["hand_r_cmd"] = self.hand_cmd_pub.to_dict(self.hand_r_cmd)
        #
        with open(var_time + ".json", "w", encoding = "utf-8") as file:
            #
            json.dump(snapshot, file, indent = 4)
        #
        print("Snapshot", var_time)

    #
    ##
    def handler_enable_control(self):
        #
        ##
        if self.enable_control:
            #
            for scale in self.panel_scale.values():   scale.set(0)

    #
    ##
    def handler_reset(self):
        #
        ##
        self.enable_control.set(False)
        #
        for scale in self.panel_scale.values():   scale.set(0)
        #
        default_file = open(self.default_path)
        default_set = json.load(default_file)
        #
        ##
        source_q, target_q = [],[]
        #
        for var_i, _ in enumerate(self.body_motors):
            #
            source_q.append(self.low_state_sub.low_state.motor_state[var_i].q)
            target_q.append(default_set["low_cmd"]["motor_cmd"][var_i]["q"])
        #
        for var_t in range(200):
            
            for var_i, _ in enumerate(self.body_motors):

                self.low_cmd.motor_cmd[var_i].q = source_q[var_i] + (target_q[var_i] - source_q[var_i]) / 200 * (var_t + 1)

            self.low_cmd_pub.publish(self.low_cmd)
            #
            time.sleep(0.01)

        self.enable_control.set(True)
        #
        self.low_state_init = self.low_state_sub.low_state
        self.low_cmd_init = copy.deepcopy(self.low_cmd)
        
    #
    ##
    def monitor_thread(self):
        #
        ##
        while True:
            #
            ##
            if self.low_state_sub.low_state is not None:
                body_state = self.low_state_sub.low_state.motor_state 
                for var_i, motor_id in enumerate(self.body_motors):
                    self.motor_state_q[motor_id].set(f"{body_state[var_i].q:.6f}")
            #
            ##
            if self.hand_state_sub.hand_l_state is not None:
                hand_l_state = self.hand_state_sub.hand_l_state.states
                for var_i, motor_id in enumerate(self.hand_l_motors):
                    self.motor_state_q[motor_id].set(f"{hand_l_state[var_i+6].q:.6f}")
            #
            ##
            if self.hand_state_sub.hand_r_state is not None:
                hand_r_state = self.hand_state_sub.hand_r_state.states
                for var_i, motor_id in enumerate(self.hand_r_motors):
                    self.motor_state_q[motor_id].set(f"{hand_r_state[var_i+6].q:.6f}")
            #
            time.sleep(self.monitor_dt)

    #
    ##
    def control_thread(self):
        #
        ##
        while True:
            #
            ## body
            for var_i, motor_id in enumerate(self.body_motors):
                #
                update_body = self.panel_scale[motor_id].get()
                #
                # low_cmd_q = self.low_state_init.motor_state[var_i].q + update_body / self.control_range * ConstPi # / 2
                low_cmd_q = self.low_cmd_init.motor_cmd[var_i].q + update_body / self.control_range * ConstPi # / 2
                #
                self.low_cmd.motor_cmd[var_i].q = low_cmd_q
            #
            ## left hand
            for var_i, motor_id in enumerate(self.hand_l_motors):
                
                update_hand_l = self.panel_scale[motor_id].get()

                hand_l_q = (update_hand_l / self.control_range + 1.0) / 2

                self.hand_l_cmd.cmds[var_i].q = hand_l_q
            #
            # right hand
            for var_i, motor_id in enumerate(self.hand_r_motors):
                
                update_hand_r = self.panel_scale[motor_id].get()

                hand_r_q = (update_hand_r / self.control_range + 1.0) / 2 

                self.hand_r_cmd.cmds[var_i].q = hand_r_q
            #
            ##
            if self.enable_control.get():
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
        self.thread_monitor.start()
        self.thread_control.start()
        self.panel.mainloop()

#
##
if __name__ == "__main__":
    #
    ##
    panel = Panel(0, "eno1")
    panel.start()