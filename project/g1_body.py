#
##
from unitree_sdk2py.core.channel import ChannelSubscriber
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_
#
from unitree_sdk2py.core.channel import ChannelPublisher
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_
from unitree_sdk2py.utils.crc import CRC
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