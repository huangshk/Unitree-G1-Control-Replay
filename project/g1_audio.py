
import time
import json
import wave


from unitree_sdk2py.g1.audio.g1_audio_api import AUDIO_SERVICE_NAME, ROBOT_API_ID_AUDIO_START_PLAY
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient


from unitree_sdk2py.rpc.client_stub import ClientStub
from unitree_sdk2py.idl.unitree_api.msg.dds_ import Request_ as Request
from unitree_sdk2py.idl.unitree_api.msg.dds_ import RequestIdentity_ as RequestIdentity
from unitree_sdk2py.idl.unitree_api.msg.dds_ import RequestLease_ as RequestLease
from unitree_sdk2py.idl.unitree_api.msg.dds_ import RequestPolicy_ as RequestPolicy
from unitree_sdk2py.idl.unitree_api.msg.dds_ import RequestHeader_ as RequestHeader

#
##
class AudioPlayer:
    #
    ##
    def __init__(self,
                 volume = 85):
        #
        ##
        self.audio_client = AudioClient()  
        self.audio_client.SetTimeout(10.0)
        self.audio_client.Init()
        self.audio_client.SetVolume(volume)

        self.rpc_client = ClientStub(AUDIO_SERVICE_NAME)
        self.rpc_client.Init()

    #
    ##
    def play(self,
             path_wav):
        #
        ##
        audio = wave.open(path_wav, "r")
        # print(audio.getparams())
        num_frame = audio.getnframes()
        framerate = audio.getframerate()
        var_frames = audio.readframes(num_frame)
        #
        ##
        stream_uint8 = []
        #
        for frame_i in range(num_frame):
            #
            if framerate == 24000 and frame_i % 3 == 0: continue
            #
            stream_uint8.append(int.from_bytes(var_frames[frame_i * 2 : frame_i * 2 + 1], "big"))
            stream_uint8.append(int.from_bytes(var_frames[frame_i * 2 + 1 : frame_i * 2 + 2], "big"))
        #
        ##
        parameter = json.dumps({
            "app_name":"example",
            "stream_id": str(time.time()),
        })
        #
        ##
        identity = RequestIdentity(id = time.monotonic_ns(), api_id = ROBOT_API_ID_AUDIO_START_PLAY)
        lease = RequestLease(id = 0)
        policy = RequestPolicy(priority = 0, noreply = False)
        header = RequestHeader(identity, lease, policy)
        #
        request = Request(header, parameter, stream_uint8)
        future = self.rpc_client.SendRequest(request, 1.0)
        #
        print(future.GetResult(1.0))