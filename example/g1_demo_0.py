import sys
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.core.channel import ChannelPublisher
from unitree_sdk2py.core.channel import ChannelSubscriber

from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_

from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient

from g1_header import G1JointIndex, Pi

#
##
def high_init(high_client:LocoClient):
    #
    ## init
    print("Zero Torque")
    high_client.ZeroTorque()
    time.sleep(1)
    #
    print("Damp")
    high_client.Damp()
    time.sleep(1)
    #
    print("Lock Stand")
    high_client.SetFsmId(4)
    time.sleep(10)
    #
    print("Main Operation")
    high_client.Start()

#
##
class LowClient:
    #
    ##
    def __init__(self):
        #
        ##
        self.time_ = 0.0
        self.control_dt_ = 0.02 
        #
        self.init_pub_sub()

    #
    ##
    def init_pub_sub(self):
        #
        ## publisher for low level control
        # self.arm_sdk_pub = ChannelPublisher("rt/arm_sdk", LowCmd_)
        # self.arm_sdk_pub.Init()
        #
        ## subscriber for low level state reading
        self.low_state_sub = ChannelSubscriber("rt/lowstate", LowState_)
        self.low_state_sub.Init(self.low_state_handler, 10)

    #
    ##
    def low_state_handler(self, 
                          var_low_state: LowState_):
        #
        ##
        self.var_low_state = var_low_state
        #
        # print(len(var_low_state.motor_state))
        #
        print([var.q/Pi*180 for var in var_low_state.motor_state[15:16]])

    #
    ##
    # def low_cmd(self):
        #
        ##



#
##
def run():#
    #
    ## pub/sub init
    ChannelFactoryInitialize(0, sys.argv[1])
    #
    ## high level init
    # high_client = LocoClient()  
    # high_client.SetTimeout(10.0)
    # high_client.Init()
    # high_init(high_client)

    low_client = LowClient()

    while True:        
        time.sleep(1)

#
##
if __name__ == "__main__":
    #
    ##
    run()
    
