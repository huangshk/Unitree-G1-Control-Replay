#
##
import time
#
from g1_header import Initial
from g1_subscribe import LowState


#
##
def run():
    #
    ##
    Initial()
    #
    LowState()
    #
    while True: time.sleep(1)

#
##
if __name__ == "__main__":
    #
    ##
    run()