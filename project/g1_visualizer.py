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

    #
    ##
    def start(self):

        thread_viewer = threading.Thread(target = self.viewer_thread)
        thread_simulate = threading.Thread(target = self.simulate_thread)
        
        thread_viewer.start()
        thread_simulate.start()

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
            #
            ##
            if self.count_init > 10:
                self.mujoco_data.qvel = 0
                self.mujoco_data.qpos = self.mujoco_qpos_latest

                for joint_i in range(29):
                
                    self.mujoco_data.qpos[joint_i + 7] = self.low_state.low_state.motor_state[joint_i].q
            else:

                self.count_init += 1
                self.mujoco_qpos_latest = self.mujoco_data.qpos.copy()

            mujoco.mj_step(self.mujoco_model, self.mujoco_data)
            
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