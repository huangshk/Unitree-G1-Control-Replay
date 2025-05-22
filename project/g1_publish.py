#
##
from unitree_sdk2py.core.channel import ChannelPublisher
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_
from unitree_sdk2py.utils.crc import CRC
from unitree_sdk2py.idl.unitree_go.msg.dds_ import MotorCmd_, MotorCmds_
from g1_header import *
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
##
class ArmSDK:
    #
    ##
    def __init__(self):
        #
        ##
        self.publisher_armsdk = ChannelPublisher("rt/arm_sdk", LowCmd_)
        self.publisher_armsdk.Init()
    
    #
    ##
    def publish(self):
        pass


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

# on g1
# sudo ./aese_h1_inspire_service/build/inspire_hand -s /dev/ttyUSB1 --namespace hand_r
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
if __name__ == "__main__":

    ChannelFactoryInitialize(0, "eno1")
    hand_cmd_pub = HandCmdPublisher()
    hand_cmd = MotorCmds_([MotorCmd_(0, 1, 0, 0, 0, 0,[0,0,0]) for _ in range(6)])
    hand_cmd_pub.publish_r(hand_cmd)
    time.sleep(1)
    hand_cmd.cmds[0].q = 0.05
    hand_cmd.cmds[1].q = 0.05
    hand_cmd.cmds[2].q = 0.05
    hand_cmd.cmds[3].q = 0.05
    hand_cmd.cmds[4].q = 0.5

    hand_cmd.cmds[5].q = 0.5
    # hand_cmd.cmds().resize(12)
    print(hand_cmd)
    hand_cmd_pub.publish_r(hand_cmd)
    # hand_cmd_pub.publish_l(hand_cmd)