import time
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
# import struct
import json
import time
import cyclonedds.idl.types as types
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient



# audio_client = AudioClient()  
# audio_client._RegistApi(1001, 1)
# audio_client.SetTimeout(10.0)
# audio_client.Init()

# audio_client.TtsMaker("English", 1)
# time.sleep(8)

import wave
# audio = wave.open("audio_test.wav", "r")
# print(audio.getnchannels())
# print(audio.getsampwidth())
# print(audio.getframerate())
# print(audio.getnframes())
# print(audio.getparams())
# num_frame = audio.getnframes()

# var_bytes = audio.readframes(num_frame)

# print(len(var_bytes))
# var_byte_list = struct.unpack("B", var_bytes)
# print(var_bytes[0:1]) 

# print(int.from_bytes(var_bytes[0:1], "big"))

# print(type(var_bytes[0:1]) )

# var_byte_list = [var_bytes[var_i : var_i+1] for var_i in range(len(var_bytes))]
# print(var_byte_list)
# print(len(var_byte_list))
# print(type(types.uint8(int.from_bytes(var_bytes[0:1], "big"))))

from unitree_sdk2py.rpc.client import Client
from unitree_sdk2py.rpc.client_stub import ClientStub
from unitree_sdk2py.idl.unitree_api.msg.dds_ import Request_ as Request
from unitree_sdk2py.idl.unitree_api.msg.dds_ import RequestHeader_ as RequestHeader
from unitree_sdk2py.idl.unitree_api.msg.dds_ import RequestLease_ as RequestLease
from unitree_sdk2py.idl.unitree_api.msg.dds_ import RequestIdentity_ as RequestIdentity
from unitree_sdk2py.idl.unitree_api.msg.dds_ import RequestPolicy_ as RequestPolicy

# class ApiClient(Client):
#     #
#     ##
#     def __init__(self, 
#                  serviceName: str, 
#                  enabaleLease: bool = False):
#         #
#         ##
#         super().__init__(serviceName, enabaleLease)

#     #
#     ##
#     def call_with_binary(self,
#                          apiId: int,
#                          parameter: str,
#                          data: types.sequence[types.uint8]):
#         #
#         ##
#         ret, proirity, leaseId = self.__CheckApi(apiId)
#         #
#         if ret == 0:
#             print("hh")
#             header = self.__SetHeader(apiId, leaseId, proirity, False)
            
#             request = Request(header, parameter, data)
#             future = self.__stub.SendRequest(request, self.__timeout)


class WavClient(AudioClient):
    def __init__(self):
        super().__init__()
    
    def play_wav(self,
                 path_wav = "audio/imperial_best.wav"):
        
        audio = wave.open(path_wav, "r")

        print(audio.getparams())

        num_frame = audio.getnframes()
        # byte_per_frame = 2
        framerate = audio.getframerate()
        var_bytes = audio.readframes(num_frame)

        # var_byte_list = [var_bytes[var_i : var_i+1] for var_i in range(len(var_bytes))]
        # var_byte_list = []
        # for frame_i in range(num_frame):
        #     var_byte_list.append(var_bytes[frame_i+1 : frame_i+2])
        #     var_byte_list.append(var_bytes[frame_i : frame_i+1])


        # print(len(var_byte_list))

        # var_uint8_list = [types.uint8(int.from_bytes(var_bytes[0:1], "little"))]

        var_uint8_list = []
        for frame_i in range(num_frame):
            if framerate == 24000 and frame_i % 3 == 0: continue
            var_uint8_list.append(int.from_bytes(var_bytes[frame_i*2 : frame_i*2 + 1], "big"))
            var_uint8_list.append(int.from_bytes(var_bytes[frame_i*2 + 1 : frame_i*2 + 2], "big"))
            # var_uint8_list.append(var_bytes[frame_i : frame_i+1])
            # var_uint8_list.append(var_bytes[frame_i+1 : frame_i+2])
            # pass
        print(var_bytes[:10])
        print(var_uint8_list[:10])
        parameter = {
            "app_name":"example",
            "stream_id": str(time.time()),
        }

        p_json = json.dumps(parameter)

        ROBOT_API_ID_AUDIO_START_PLAY = 1003
        apiId = ROBOT_API_ID_AUDIO_START_PLAY

        ret, priority, leaseId = 0,0,0#self.__CheckApi(apiId)

        self.__stub = ClientStub("voice")
        self.__stub.Init()

        #
        if ret == 0:
            print("hh")

            identity = RequestIdentity(time.monotonic_ns(), apiId)
            lease = RequestLease(leaseId)
            policy = RequestPolicy(priority, False)
            header = RequestHeader(identity, lease, policy)
            # print(header)
            # header = self.__SetHeader(apiId, leaseId, proirity, False)

            request = Request(header, p_json, var_uint8_list)
            future = self.__stub.SendRequest(request, 2.0)

            # print(future)
            result = future.GetResult(2.0)
            print(result)


if __name__ =="__main__":

    ChannelFactoryInitialize(0, "eno1")

    wav_client = WavClient()
    wav_client.SetVolume(100)
    wav_client.play_wav()

        
