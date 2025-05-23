
from unitree_sdk2py.core.channel import ChannelSubscriber

from unitree_sdk2py.idl.unitree_go.msg.dds_ import MotorStates_


from unitree_sdk2py.core.channel import ChannelPublisher

from unitree_sdk2py.idl.unitree_go.msg.dds_ import MotorCmds_

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