from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient
ChannelFactoryInitialize(0, "eno1")
audio_client = AudioClient()  
# audio_client._RegistApi(1001, 1)
audio_client.SetTimeout(10.0)
audio_client.Init()
audio_client.SetVolume(100)
audio_client.TtsMaker("English", 1)
