import time
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from g1_body import RemoteSubscriber

#
##
if __name__ =="__main__":
    #
    ##
    ChannelFactoryInitialize(0, "eno1")
    #
    remote_sub = RemoteSubscriber()
    #
    while True:
        time.sleep(0.5)
        print(remote_sub.data.__dict__)