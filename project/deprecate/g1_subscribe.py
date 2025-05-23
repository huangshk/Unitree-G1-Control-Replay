
from unitree_sdk2py.core.channel import ChannelSubscriber
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_

from unitree_sdk2py.idl.unitree_go.msg.dds_ import MotorStates_

from g1_header import *
#
##
class LowStateSubscriber:

    #
    ##
    def __init__(self):
        #
        ##
        self.subscriber = ChannelSubscriber("rt/lowstate", LowState_)
        self.subscriber.Init(self.handler_default, 10)
        #
        self.low_state = None
        self.ready = False

    #
    ##
    def handler_default(self,
                        low_state: LowState_):
        #
        ##
        self.low_state = low_state
        self.ready = True
        # print([var.q / const_pi * 180 for var in low_state.motor_state[15:16]])

        # print(low_state.motor_state[25].q/ const_pi * 180)


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
    def test(self):
        #
        ##
        try:
            print([var.q for var in self.hand_state_r.states[:6]])
            # print([var.q for var in self.hand_state_l.states[6:]])
            print([var_0.q-var_1.q for var_0, var_1 in zip(self.hand_state_r.states[:6], self.hand_state_r.states[6:])])
        except:
            pass


from unitree_sdk2py.core.channel import ChannelFactoryInitialize
if __name__ == "__main__":

    ChannelFactoryInitialize(0, "eno1")
    hand_state_sub = HandStateSubscriber()
    while True:
        hand_state_sub.test()
        time.sleep(0.1)
