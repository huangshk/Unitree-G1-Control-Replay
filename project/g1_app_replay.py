import time

import tkinter
from tkinter import ttk

from g1_header import *
from g1_body import LowStateSubscriber, LowCmdPublisher, LowCmdInit
from g1_hand import HandStateSubscriber, HandCmdPublisher, HandCmdInit

class Replay:
    def __init__(self,
                 control_dt = 0.01,
                 path_snapshot = "snapshot"):
        
        self.control_dt = control_dt
        self.body_motors = [motor_id for (motor_id, _) in G1Body.__dict__.items() if (motor_id[0] != "_" and motor_id != "kNotUsedJoint")]

        
        self.low_state_sub = LowStateSubscriber()


        
        self.low_cmd_pub = LowCmdPublisher()
        self.low_cmd = LowCmdInit(self.low_state_init.mode_machine).low_cmd

    def init_panel(self):
        #
        ##
        self.panel = tkinter.Tk(className = " Imperial AESE G1 Replay ")
        #
        self.frame = ttk.Frame(self.panel, padding = 10)
        self.frame.grid()
        #
        font_title = ("Arial", 16, "bold")
        font_content = ("Arial", 14, "bold")

        
        ttk.Button(self.frame, text = "Run", command = self.handler_run).grid(column = 0, row = 0)
        ttk.Button(self.frame, text = "Reset", command = self.handler_reset).grid(column = 1, row = 0)
        
        ttk.Label(self.frame, text = "Target", font = font_title).grid(column = 0, row = 1, pady = 2)
        ttk.Label(self.frame, text = "Duration", font = font_title).grid(column = 1, row = 1, pady = 2)

    def handler_run(self):
        pass

    def handler_reset(self):
        pass




    def forward(self,
                target_q: list,
                duration: float):
        
        num_step = duration / self.control_dt

        source_q = []
        #
        for var_i, _ in enumerate(self.body_motors):
            #
            source_q.append(self.low_state_sub.low_state.motor_state[var_i].q)

        for var_t in range(num_step):
            #
            for var_i, _ in enumerate(self.body_motors):

                self.low_cmd.motor_cmd[var_i].q = source_q[var_i] + (target_q[var_i] - source_q[var_i]) / num_step * (var_t + 1)

            time.sleep(self.control_dt)


    #
    ##
    def control_thread(self):
        #
        ##
        while True:
            #
            ## body
            self.low_cmd_pub.publish(self.low_cmd)
            time.sleep(self.control_dt)

    #
    ##
    def start(self):
        #
        ##
        pass
        