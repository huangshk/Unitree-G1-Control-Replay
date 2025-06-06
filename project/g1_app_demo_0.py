#
##
import os
import time
import json
import threading
#
##
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
#
##
from g1_header import *
from g1_body import LowStateSubscriber, LowCmdInit, ArmSdkPublisher, RemoteSubscriber
from g1_hand import HandCmdPublisher, HandCmdInit

#
##
class Demo:
    #
    ##
    def __init__(self,
                 domain,
                 netface,
                 control_dt = 0.01,
                 default_duration = 0.5,
                 path_snapshot = "snapshot",
                 path_default = "snapshot/default.json"):
        #
        ##
        self.control_dt = control_dt
        self.default_duration = default_duration
        self.path_snapshot = path_snapshot
        with open(path_default) as default_file:
            self.default_set = json.load(default_file)
        #
        ##
        ChannelFactoryInitialize(domain, netface)
        #
        ##
        self.low_state_sub = LowStateSubscriber()
        self.remote_sub = RemoteSubscriber()
        time.sleep(0.1)
        self.low_state_init = self.low_state_sub.low_state
        #
        ##
        self.low_cmd = LowCmdInit(self.low_state_init.mode_machine).low_cmd
        self.arm_sdk_pub = ArmSdkPublisher()
        #
        ##
        self.hand_cmd_pub = HandCmdPublisher()
        self.hand_l_cmd = HandCmdInit().hand_cmd
        self.hand_r_cmd = HandCmdInit().hand_cmd
        #
        # self.init_event()
        self.script_to_run = None
        #
        self.thread_control = threading.Thread(target = self.worker_control)
        # self.thread_event = threading.Thread(target = self.worker_event)
        #
        self.flag_ready = False
        self.flag_reset = False
        # self.flag_run = False

    #
    ##
    def check_event(self):
        #
        ##
        event_dict = {
            #
            ## script: trigger
            "reset": [self.remote_sub.data.Btn_Down, self.remote_sub.data.Btn_A],
            "2025_06_03_18_39_31_407775.jsonscript": [self.remote_sub.data.Btn_Up, self.remote_sub.data.Btn_Y],
            
        }
        #
        return event_dict

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
    def worker_main(self):
        #
        ##
        while True:
            #
            ##
            event_dict = self.check_event()
            #
            for script in event_dict.keys():
                #
                if all(event_dict[script]):
                    #
                    time.sleep(0.5)
                    #
                    if all(event_dict[script]):
                        #
                        print("Event", script)
                        #
                        if script == "reset":
                            #
                            self.handler_reset()
                        #
                        elif self.script_to_run is None:

                            self.script_to_run = script
                            thread_run = threading.Thread(target = self.worker_run)
                            thread_run.start()
                        #
                        break
            #
            time.sleep(self.control_dt)
    
    #
    ##
    def worker_run(self):
        #
        ##
        if self.script_to_run is not None:
            with open(self.path_snapshot + "/" + self.script_to_run) as file:   
                script_dict = json.load(file)
                #
                self.run_target_list(target_list = script_dict["target_list"], 
                                     flag_body_list = script_dict["flag_body_list"], 
                                     flag_hand_list = script_dict["flag_hand_list"], 
                                     duration_list = script_dict["duration_list"],
                                     repeat_list = script_dict["repeat_list"],
                                     flag_body_parent = True,
                                     flag_hand_parent = True)
        #
        ##
        self.script_to_run = None
        print("end")

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
    def worker_control(self):
        #
        ##
        while True:
            #
            ##
            if self.flag_ready:
                #
                self.arm_sdk_pub.publish(self.low_cmd)
                self.hand_cmd_pub.publish_l(self.hand_l_cmd)
                self.hand_cmd_pub.publish_r(self.hand_r_cmd)
            #
            time.sleep(self.control_dt)

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
            #
            self.low_cmd.motor_cmd[var_i].q = target_q[var_i]
            #
            time.sleep(self.control_dt)

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
        # self.thread_event.start()
        self.worker_main()
        # while True:
        #     time.sleep(self.control_dt)

#
##
if __name__ == "__main__":
    #
    ##
    app_demo = Demo(0, "eno1")
    app_demo.start()
