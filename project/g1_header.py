

from unitree_sdk2py.core.channel import ChannelFactoryInitialize

const_pi = 3.141592654

#
##
class Initial:
    #
    ##
    def __init__(self,
                 domain = 0,
                 interface = "eno1"):
        #
        ##
        self.init_channel(domain, interface)

    #
    ##
    def init_channel(self,
                     domain,
                     interface):
        #
        ##
        ChannelFactoryInitialize(domain, interface)