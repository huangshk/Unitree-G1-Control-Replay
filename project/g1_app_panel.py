#
##
import time
import tkinter
from tkinter import ttk
import threading
#
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
from unitree_sdk2py.idl.unitree_go.msg.dds_ import MotorCmd_, MotorCmds_
#
from g1_header import *
from g1_body import LowStateSubscriber, LowCmdPublisher
from g1_hand import HandStateSubscriber, HandCmdPublisher

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
                 control_dt = 0.001):
        #
        ##
        self.control_range = control_range
        self.monitor_dt = monitor_dt
        self.control_dt = control_dt
        #
        ChannelFactoryInitialize(domain, netface)
        #
        self.low_state_sub = LowStateSubscriber()
        self.hand_state_sub = HandStateSubscriber()
        #
        self.low_state_init = self.low_state_sub.low_state
        self.hand_l_state_init = self.hand_state_sub.hand_l_state
        self.hand_r_state_init = self.hand_state_sub.hand_r_state
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
        self.low_cmd = self.init_low_cmd()

        self.hand_cmd_pub = HandCmdPublisher()
        self.hand_l_cmd = MotorCmds_([MotorCmd_(0, 0.5, 0, 0, 0, 0, [0, 0, 0]) for _ in range(6)])
        self.hand_r_cmd = MotorCmds_([MotorCmd_(0, 0.5, 0, 0, 0, 0, [0, 0, 0]) for _ in range(6)])
        #
        self.init_panel()
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
                if var_column < 5: motor_id = self.body_motors[sum(row_per_column[:var_column]) + var_row]
                elif var_column == 5: motor_id = self.hand_l_motors[var_row]
                elif var_column == 6: motor_id = self.hand_r_motors[var_row]
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
                ttk.Label(self.frame, text = motor_id, font = font_content).grid(column = var_column, row = var_row * 2 + 2)
                #
                ## monitor
                ttk.Label(self.frame, textvariable = self.motor_state_q[motor_id], 
                          font = ("Arial", 12)).grid(column = var_column, row = max(row_per_column) * 2 + 1 + var_row * 2 + 1)

                ttk.Label(self.frame, text = motor_id + "\n", 
                          font = font_content).grid(column = var_column, row = max(row_per_column) * 2 + 1 + var_row * 2 + 2)
                
    #
    ##
    def init_low_cmd(self):
        #
        ##
        low_cmd = unitree_hg_msg_dds__LowCmd_()
        low_cmd.mode_pr = 0
        low_cmd.mode_machine = self.low_state_init.mode_machine
        #
        for var_i in range(len(self.body_motors)):
            #
            low_cmd.motor_cmd[var_i].mode = 1
            low_cmd.motor_cmd[var_i].dq = 0
            low_cmd.motor_cmd[var_i].kp = 60
            low_cmd.motor_cmd[var_i].kd = 1.5
            low_cmd.motor_cmd[var_i].tau = 0
        #
        return low_cmd

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
                    self.motor_state_q[motor_id].set(f"{hand_r_state[var_i].q:.6f}")
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
            for var_i, motor_id in enumerate(self.body_motors):
                #
                update_body = self.panel_scale[motor_id].get()
                #
                low_cmd_q = self.low_state_init.motor_state[var_i].q + update_body / self.control_range * ConstPi # / 2
                #
                if low_cmd_q > ConstPi: low_cmd_q = ConstPi - 0.1
                if low_cmd_q < -ConstPi: low_cmd_q = -ConstPi + 0.1
                #
                self.low_cmd.motor_cmd[var_i].q = low_cmd_q
            #
            self.low_cmd_pub.publish(self.low_cmd)


            for var_i, motor_id in enumerate(self.hand_l_motors):
                
                update_hand_l = self.panel_scale[motor_id].get()

                hand_l_q = (update_hand_l / self.control_range + 1.0) / 2  # self.hand_l_state_init.states[var_i].q + 
                #
                if hand_l_q > 1.0: hand_l_q = 1.0
                if hand_l_q < 0.0: hand_l_q = 0.0

                self.hand_l_cmd.cmds[var_i].q = hand_l_q

            self.hand_cmd_pub.publish_l(self.hand_l_cmd)
                

            for var_i, motor_id in enumerate(self.hand_r_motors):
                
                update_hand_r = self.panel_scale[motor_id].get()

                hand_r_q = (update_hand_r / self.control_range + 1.0) / 2 

                if hand_r_q > 1.0: hand_r_q = 1.0
                if hand_r_q < 0.0: hand_r_q = 0.0

                self.hand_r_cmd.cmds[var_i].q = hand_r_q

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