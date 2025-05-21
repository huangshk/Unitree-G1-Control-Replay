import time
import numpy as np

import threading

import mujoco
import mujoco.viewer

from unitree_sdk2py.core.channel import ChannelFactoryInitialize

from g1_header import const_pi
from g1_subscribe import LowState

#
##
class ElasticBand:
    #
    ##
    def __init__(self):
        #
        ##
        self.stiffness = 200
        self.damping = 100
        self.point = np.array([0, 0, 3])
        self.length = 0
        self.enable = True

    #
    ##
    def advance(self, 
                x, 
                dx):
        """
        [input] δx: desired position - current position
                dx: current velocity
        """
        #
        ##
        δx = self.point - x
        distance = np.linalg.norm(δx)
        direction = δx / distance
        v = np.dot(dx, direction)
        f = (self.stiffness * (distance - self.length) - self.damping * v) * direction
        return f

    #
    ##
    def key_callback(self, 
                     key):
        #
        ##
        glfw = mujoco.glfw.glfw
        #
        if key == glfw.KEY_7:
            self.length -= 0.1
        #
        if key == glfw.KEY_8:
            self.length += 0.1
        #
        if key == glfw.KEY_9:
            self.enable = not self.enable

#
##
class Visualizer():
    #
    ##
    def __init__(self,
                 domain = 0,
                 netface = "eno1",
                 path_scene = "scene/scene_29dof.xml",
                 enable_elastic_band = False,
                 simulate_dt = 0.005,
                 viewer_dt = 0.02):
        #
        ##
        ChannelFactoryInitialize(domain, netface)
        self.low_state = LowState()
        #
        self.mujoco_model = mujoco.MjModel.from_xml_path(path_scene)
        self.mujoco_data = mujoco.MjData(self.mujoco_model)

        self.enable_elastic_band = enable_elastic_band
        #
        if self.enable_elastic_band:

            self.elastic_band = ElasticBand()

            self.band_attached_link = self.mujoco_model.body("torso_link").id

            self.viewer = mujoco.viewer.launch_passive(self.mujoco_model, 
                                                       self.mujoco_data, 
                                                       key_callback = self.elastic_band.key_callback)

        else:

            self.viewer = mujoco.viewer.launch_passive(self.mujoco_model, self.mujoco_data)

        self.thread_lock = threading.Lock()

        self.simulate_dt = simulate_dt
        self.viewer_dt = viewer_dt

        self.mujoco_model.opt.timestep = simulate_dt

        self.count_init = 0

    def start(self):

        thread_viewer = threading.Thread(target = self.viewer_thread)
        thread_simulate = threading.Thread(target = self.simulate_thread)
        
        thread_viewer.start()
        thread_simulate.start()

    # def real2mujoco(self,
    #                 motor_state):
    #     #
    #     ##
    #     mujoco_data_ctrl = []
    #     #
    #     const_range = [88, 88, 88, 139, 50, 50,
    #                    88, 88, 88, 139, 50, 50,
    #                    88, 50, 50,
    #                    25, 25, 25, 25, 25, 5, 5,
    #                    25, 25, 25, 25, 25, 5, 5]
    #     #
    #     for var_state, var_range in zip(motor_state, const_range):
    #         #
    #         mujoco_data_ctrl.append(var_state.q / const_pi * var_range)
    #     #
    #     return mujoco_data_ctrl

    #
    ##
    def simulate_thread(self):
        #
        ##
        while self.viewer.is_running() and self.low_state.ready:

            self.thread_lock.acquire()
            if self.enable_elastic_band:
                self.mujoco_data.xfrc_applied[self.band_attached_link, :3] = self.elastic_band.advance(
                    self.mujoco_data.qpos[:3], self.mujoco_data.qvel[:3])
            
            # low_state = self.low_state.low_state
            # if self.mujoco_data != None:
            #     for motor_i in range(self.mujoco_model.nu):

            #         self.mujoco_data.ctrl[motor_i] = (
            #         low_state.motor_state[motor_i].tau
            #         + low_state.motor_state[motor_i].kp
            #         * (low_state.motor_state[motor_i].q - self.mujoco_data.sensordata[motor_i])
            #         + low_state.motor_state[motor_i].kd
            #         * (
            #             low_state.motor_state[motor_i].dq
            #             - self.mujoco_data.sensordata[motor_i + self.mujoco_model.nu]
            #         )
            #     )

            # print(self.mujoco_data)
            # print(self.mujoco_data.body)
            # print(len(self.low_state.low_state.motor_state))
            # self.mujoco_data.qacc = 0
            # self.mujoco_data.qvel = 0
            
            if self.count_init > 10:
                self.mujoco_data.qvel = 0
                self.mujoco_data.qpos = self.mujoco_qpos_latest

                for joint_i in range(29):
                
                # if joint_i != 25: continue
                # print(self.low_state.low_state.motor_state[joint_i].q)
                    self.mujoco_data.qpos[joint_i + 7] = self.low_state.low_state.motor_state[joint_i].q
            else:
                self.count_init += 1
                self.mujoco_qpos_latest = self.mujoco_data.qpos.copy()

            # real_q_array = np.array([var.q for var in self.low_state.low_state.motor_state[0:29]])

            # print(self.mujoco_data.qpos[7:].shape)

            # print(type(self.mujoco_data.qpos))
            mujoco.mj_step(self.mujoco_model, self.mujoco_data)
            # print(self.mujoco_data.sensordata.shape)
            # print(self.mujoco_model.nu)
            
            # print(low_state.motor_state[22].q/ const_pi * 180)

            # self.mujoco_data.ctrl[0:21] = 0
            # self.mujoco_data.ctrl[23:] = 0
            # self.mujoco_data.ctrl[22] = low_state.motor_state[22].q/ const_pi * 180 *25/180
            # self.mujoco_data.ctrl = self.real2mujoco(low_state.motor_state)
            # print(self.mujoco_data.qpos[-5:-1])
            # print(self.mujoco_data.qpos[:10])


            self.thread_lock.release()
            
            time.sleep(self.simulate_dt)
        

    def viewer_thread(self):
        #
        ##
        while self.viewer.is_running():
            #
            self.thread_lock.acquire()
            self.viewer.sync()
            self.thread_lock.release()
            time.sleep(self.viewer_dt)


if __name__ == "__main__":
    #
    ##
    visualizer = Visualizer()
    visualizer.start()