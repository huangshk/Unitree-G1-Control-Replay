#
##
from unitree_sdk2py.core.channel import ChannelSubscriber
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_
#
from unitree_sdk2py.core.channel import ChannelPublisher
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_
from unitree_sdk2py.utils.crc import CRC
#
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
#
##
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
        self.subscriber.Init(self.handler, 10)
        #
        self.low_state = None

    #
    ##
    def handler(self,
                low_state: LowState_):
        #
        ##
        self.low_state = low_state

#
##
class LowCmdPublisher:
    #
    ##
    def __init__(self):
        #
        ##
        self.publisher_lowcmd = ChannelPublisher("rt/lowcmd", LowCmd_)
        self.publisher_lowcmd.Init()
        #
        self.crc = CRC()
    
    #
    ##
    def publish(self,
                low_cmd: LowCmd_):
        #
        ##
        low_cmd.crc = self.crc.Crc(low_cmd)
        self.publisher_lowcmd.Write(low_cmd)

#
# ##
# class LowCmd:
#     #
#     ##
#     def __init__(self,
#                  mode_pr,
#                  mode_machine,
#                  motor_cmd):
#         #
#         ##
#         self.low_cmd = unitree_hg_msg_dds__LowCmd_()

#         self.low_cmd.mode_pr = mode_pr

#         self.low_cmd.mode_machine = mode_machine

#         for var_i in range(len(self.low_cmd.motor_cmd)):


#             self.low_cmd.motor_cmd[var_i].q = low_cmd_q
#             #
#             self.low_cmd.mode_pr = 0
#             self.low_cmd.mode_machine = self.mode_machine
#             self.low_cmd.motor_cmd[var_i].mode = 1
#             self.low_cmd.motor_cmd[var_i].dq = 0
#             self.low_cmd.motor_cmd[var_i].kp = 60
#             self.low_cmd.motor_cmd[var_i].kd = 1.5
#             self.low_cmd.motor_cmd[var_i].tau = 5
