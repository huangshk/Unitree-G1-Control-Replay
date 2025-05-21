
from unitree_sdk2py.core.channel import ChannelSubscriber
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_

#
##
class LowStateSubscriber:

    #
    ##
    def __init__(self):
        #
        ##
        self.subscriber = ChannelSubscriber("rt/lowstate", LowState_)
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


# #
# ##
# class HandState:
#     #
#     ##
#     def __init__(self,
#                  enable_state_l = True,
#                  enable_state_r = True,
#                  enable_touch_l = True,
#                  enable_touch_r = True):
#         #
#         ##
#         self.hand_state_l, self.hand_state_r = None, None
#         self.hand_touch_l, self.hand_touch_r = None, None
#         #
#         ##
#         if enable_state_l:
#             #
#             self.subscriber_state_l = ChannelSubscriber("rt/inspire_hand/state/l", state)
#             self.subscriber_state_l.Init(self.handler_state_l, 10)
#         #
#         ##
#         if enable_state_r:
#             #
#             self.subscriber_state_r = ChannelSubscriber("rt/inspire_hand/state/r", state)
#             self.subscriber_state_r.Init(self.handler_state_r, 10)
#         #
#         ##
#         if enable_touch_l:
#             #
#             self.subscriber_touch_l = ChannelSubscriber("rt/inspire_hand/touch/l", state)
#             self.subscriber_touch_l.Init(self.handler_touch_l, 10)

#         if enable_touch_r:
#             #
#             self.subscriber_touch_r = ChannelSubscriber("rt/inspire_hand/touch/r", N)
#             self.subscriber_touch_r.Init(self.handler_touch_r, 10)

#     #
#     ##
#     def handler_state_l(self, hand_state_l: state):
#         #
#         self.hand_state_l = hand_state_l

#     #
#     ##
#     def handler_state_r(self, hand_state_r: state):
#         #
#         self.hand_state_r = hand_state_r
    
#     #
#     ##
#     def handler_touch_l(self, hand_touch_l: state):
#         #
#         self.hand_touch_l = hand_touch_l

#     #
#     ##
#     def handler_touch_r(self, hand_touch_r: state):
#         #
#         self.hand_touch_r = hand_touch_r