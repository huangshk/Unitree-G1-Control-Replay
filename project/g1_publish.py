#
##
from unitree_sdk2py.core.channel import ChannelPublisher
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_
from unitree_sdk2py.utils.crc import CRC

#
##
class LowCmd:
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