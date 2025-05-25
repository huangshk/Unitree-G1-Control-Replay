#
##
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from g1_audio import AudioPlayer

#
##
if __name__ =="__main__":
    #
    ##
    ChannelFactoryInitialize(0, "eno1")
    #
    audio_player = AudioPlayer()
    audio_player.play("audio/imperial_best.wav")
