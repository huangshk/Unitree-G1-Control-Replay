
from unitree_sdk2py.core.channel import ChannelSubscriber
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_

from g1_header import const_pi

#
##
class LowState:

    #
    ##
    def __init__(self):

        self.subscriber = ChannelSubscriber("rt/lowstate", LowState_)
        #
        ##
        self.subscriber.Init(self.default_handler, 10)
        #
        self.low_state = None
        self.ready = False

    #
    ##
    def default_handler(self,
                        low_state: LowState_):
        #
        ##
        self.low_state = low_state
        self.ready = True
        # print([var.q / const_pi * 180 for var in low_state.motor_state[15:16]])

        # print(low_state.motor_state[25].q/ const_pi * 180)