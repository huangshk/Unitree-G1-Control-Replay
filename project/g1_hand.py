
from unitree_sdk2py.core.channel import ChannelSubscriber

from unitree_sdk2py.idl.unitree_go.msg.dds_ import MotorStates_


from unitree_sdk2py.core.channel import ChannelPublisher

from unitree_sdk2py.idl.unitree_go.msg.dds_ import MotorCmd_, MotorCmds_

#
##
class HandStateSubscriber:
    #
    ##
    def __init__(self,
                 enable_state_l = True,
                 enable_state_r = True):
        #
        ##
        self.hand_state_l, self.hand_state_r = None, None
        #
        ##
        if enable_state_l:
            #
            self.subscriber_state_l = ChannelSubscriber("rt/hand_l/state", MotorStates_)
            self.subscriber_state_l.Init(self.handler_state_l, 10)
        #
        ##
        if enable_state_r:
            #
            self.subscriber_state_r = ChannelSubscriber("rt/hand_r/state", MotorStates_)
            self.subscriber_state_r.Init(self.handler_state_r, 10)
       
    #
    ##
    def handler_state_l(self, hand_state_l: MotorStates_):
        #
        self.hand_state_l = hand_state_l

    #
    ##
    def handler_state_r(self, hand_state_r: MotorStates_):
        #
        self.hand_state_r = hand_state_r

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
        self.publish_hand_l.Write(hand_cmd)

    #
    ##
    def publish_r(self,
                  hand_cmd: MotorCmds_):
        #
        ##
        self.publish_hand_r.Write(hand_cmd)