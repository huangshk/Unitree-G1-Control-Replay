
import copy

from unitree_sdk2py.core.channel import ChannelSubscriber

from unitree_sdk2py.idl.unitree_go.msg.dds_ import MotorStates_


from unitree_sdk2py.core.channel import ChannelPublisher

from unitree_sdk2py.idl.unitree_go.msg.dds_ import MotorCmds_, MotorCmd_
#
##
from g1_header import *

#
##
class HandStateSubscriber:
    '''
    sudo ./aese_h1_inspire_service/build/inspire_hand -s /dev/ttyUSB1 --namespace hand_r
    sudo ./aese_h1_inspire_service/build/inspire_hand -s /dev/ttyUSB2 --namespace hand_l
    '''
    #
    ##
    def __init__(self):
        #
        ##
        self.hand_l_state, self.hand_r_state = None, None
        #
        ##
        self.subscriber_l = ChannelSubscriber("rt/hand_l/state", MotorStates_)
        self.subscriber_l.Init(self.handler_l, 10)
        #
        self.subscriber_r = ChannelSubscriber("rt/hand_r/state", MotorStates_)
        self.subscriber_r.Init(self.handler_r, 10)
       
    #
    ##
    def handler_l(self, hand_l_state: MotorStates_):
        #
        self.hand_l_state = hand_l_state

    #
    ##
    def handler_r(self, hand_r_state: MotorStates_):
        #
        self.hand_r_state = hand_r_state

    #
    ##
    def to_dict(self,
                hand_state: MotorStates_):
        #
        ##
        hand_state_dict = copy.deepcopy(hand_state).__dict__
        #
        for var_i in range(len(hand_state_dict["states"])):
            hand_state_dict["states"][var_i] = hand_state_dict["states"][var_i].__dict__
        #
        hand_state_dict["sample_info"] = hand_state_dict["sample_info"].__dict__
        #
        return hand_state_dict

#
##
class HandCmdPublisher:
    #
    ##
    def __init__(self):
        #
        ##
        self.publish_hand_l = ChannelPublisher("rt/hand_l/cmd", MotorCmds_)
        self.publish_hand_l.Init()
        #
        ##
        self.publish_hand_r = ChannelPublisher("rt/hand_r/cmd", MotorCmds_)
        self.publish_hand_r.Init()
    
    #
    ##
    def publish_l(self,
                  hand_cmd: MotorCmds_):
        #
        ##
        for var_i in range(len(hand_cmd.cmds)):
            #
            if hand_cmd.cmds[var_i].q > 0.99: hand_cmd.cmds[var_i].q = 0.99
            if hand_cmd.cmds[var_i].q < 0.01: hand_cmd.cmds[var_i].q = 0.01
        #
        self.publish_hand_l.Write(hand_cmd)

    #
    ##
    def publish_r(self,
                  hand_cmd: MotorCmds_):
        #
        ##
        for var_i in range(len(hand_cmd.cmds)):
            #
            if hand_cmd.cmds[var_i].q > 0.99: hand_cmd.cmds[var_i].q = 0.99
            if hand_cmd.cmds[var_i].q < 0.01: hand_cmd.cmds[var_i].q = 0.01
        #
        self.publish_hand_r.Write(hand_cmd)

    #
    ##
    def to_dict(self,
                hand_cmd: MotorCmds_):
        #
        ##
        hand_cmd_dict = copy.deepcopy(hand_cmd).__dict__
        #
        for var_i in range(len(hand_cmd_dict["cmds"])):
            hand_cmd_dict["cmds"][var_i] = hand_cmd_dict["cmds"][var_i].__dict__
        #
        return hand_cmd_dict

#
##
class HandCmdInit:
    #
    ##
    def __init__(self,
                 motor_qs = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]):
        #
        ##
        self.hand_cmd = MotorCmds_([MotorCmd_(0, motor_q, 0, 0, 0, 0, [0, 0, 0]) for motor_q in motor_qs])