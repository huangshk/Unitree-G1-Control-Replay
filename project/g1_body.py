#
##
import copy
#
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
    def to_dict(self,
                low_state: LowState_):
        #
        ##
        low_state_dict = copy.deepcopy(low_state).__dict__
        #
        low_state_dict["imu_state"] = low_state_dict["imu_state"].__dict__
        #
        for var_i in range(len(low_state_dict["motor_state"])):
            low_state_dict["motor_state"][var_i] = low_state_dict["motor_state"][var_i].__dict__
        #
        low_state_dict["sample_info"] = low_state_dict["sample_info"].__dict__
        low_state_dict["wireless_remote"] = str(low_state_dict["wireless_remote"])
        #
        return low_state_dict


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
            if low_cmd.motor_cmd[var_i].q > ConstPi - 1: low_cmd.motor_cmd[var_i].q = ConstPi - 1
            if low_cmd.motor_cmd[var_i].q < -ConstPi + 1: low_cmd.motor_cmd[var_i].q = -ConstPi + 1
        #
        low_cmd.crc = self.crc.Crc(low_cmd)
        self.publisher_lowcmd.Write(low_cmd)
    
    #
    ##
    def to_dict(self,
                low_cmd: LowCmd_):
        #
        ##
        low_cmd_dict = copy.deepcopy(low_cmd).__dict__
        #
        for var_i in range(len(low_cmd_dict["motor_cmd"])):
            low_cmd_dict["motor_cmd"][var_i] = low_cmd_dict["motor_cmd"][var_i].__dict__
        #
        return low_cmd_dict

#
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
                 motor_cmd_tau = 1):
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

#
##
class ArmSdkPublisher:
    #
    ##
    def __init__(self):
        #
        ##
        self.publisher_armsdk = ChannelPublisher("rt/arm_sdk", LowCmd_)
        self.publisher_armsdk.Init()
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
            if low_cmd.motor_cmd[var_i].q > ConstPi - 1: low_cmd.motor_cmd[var_i].q = ConstPi - 1
            if low_cmd.motor_cmd[var_i].q < -ConstPi + 1: low_cmd.motor_cmd[var_i].q = -ConstPi + 1
        #
        low_cmd.motor_cmd[G1Body.kNotUsedJoint].q = 1
        #
        low_cmd.crc = self.crc.Crc(low_cmd)
        self.publisher_armsdk.Write(low_cmd)

import time
import struct
#
##
class RemoteSubscriber:
    #
    ##
    def __init__(self):
        #
        ##
        self.subscriber = ChannelSubscriber("rt/lowstate", LowState_)
        self.subscriber.Init(self.handler, 10)
        #
        self.data = G1Remote

    #
    ##
    def handler(self,
                low_state: LowState_):
        #
        ##
        data_remote = low_state.wireless_remote
        #
        ##
        self.data.Btn_R1 = bool(data_remote[2] & 1)
        self.data.Btn_L1 = bool(data_remote[2] & 2)
        self.data.Btn_Start = bool(data_remote[2] & 4)
        self.data.Btn_Select = bool(data_remote[2] & 8)
        self.data.Btn_R2 = bool(data_remote[2] & 16)
        self.data.Btn_L2 = bool(data_remote[2] & 32)
        self.data.Btn_F1 = bool(data_remote[2] & 64)
        self.data.Btn_F3 = bool(data_remote[2] & 128)

        #
        ##
        self.data.Btn_A = bool(data_remote[3] & 1)
        self.data.Btn_B = bool(data_remote[3] & 2)
        self.data.Btn_X = bool(data_remote[3] & 4)
        self.data.Btn_Y = bool(data_remote[3] & 8)
        self.data.Btn_Up = bool(data_remote[3] & 16)
        self.data.Btn_Right = bool(data_remote[3] & 32)
        self.data.Btn_Down = bool(data_remote[3] & 64)
        self.data.Btn_Left = bool(data_remote[3] & 128)

        #
        ##
        self.data.Rocker_L.X = struct.unpack('<f', data_remote[4:8])[0]
        self.data.Rocker_L.Y = struct.unpack('<f', data_remote[20:24])[0]
        self.data.Rocker_R.X = struct.unpack('<f', data_remote[8:12])[0]
        self.data.Rocker_R.Y = struct.unpack('<f', data_remote[12:16])[0]
