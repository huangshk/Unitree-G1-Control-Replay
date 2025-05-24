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
        for var_i in range(len(low_cmd.motor_cmd)):
            #
            if low_cmd.motor_cmd[var_i].q > ConstPi: low_cmd.motor_cmd[var_i].q = ConstPi - 0.1
            if low_cmd.motor_cmd[var_i].q < -ConstPi: low_cmd.motor_cmd[var_i].q = -ConstPi + 0.1
        #
        low_cmd.crc = self.crc.Crc(low_cmd)
        self.publisher_lowcmd.Write(low_cmd)


##
class LowCmdInit:
    #
    ##
    def __init__(self,
                 mode_machine,
                 mode_pr = 0,
                 motor_cmd_mode = 1,
                 motor_cmd_dq = 0,
                 motor_cmd_kp = 60,
                 motor_cmd_kd = 1.5,
                 motor_cmd_tau = 0):
        #
        ##
        self.low_cmd = unitree_hg_msg_dds__LowCmd_()

        self.low_cmd.mode_machine = mode_machine
        #
        self.low_cmd.mode_pr = mode_pr
        #
        for var_i in range(G1NumBodyJoint):
            #
            self.low_cmd.motor_cmd[var_i].q = None
            #
            self.low_cmd.motor_cmd[var_i].mode = motor_cmd_mode
            self.low_cmd.motor_cmd[var_i].dq = motor_cmd_dq
            self.low_cmd.motor_cmd[var_i].kp = motor_cmd_kp
            self.low_cmd.motor_cmd[var_i].kd = motor_cmd_kd
            self.low_cmd.motor_cmd[var_i].tau = motor_cmd_tau
