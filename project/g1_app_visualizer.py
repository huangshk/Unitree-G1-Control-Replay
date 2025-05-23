#
##
import time
import threading
#
import mujoco
import mujoco.viewer
#
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
#
from g1_header import *
from g1_body import LowStateSubscriber


#
##
class Visualizer():
    #
    ##
    def __init__(self,
                 domain,
                 netface,
                 path_scene = "scene/scene_29dof.xml",
                 simulate_dt = 0.005,
                 viewer_dt = 0.02):
        #
        ##
        ChannelFactoryInitialize(domain, netface)
        self.low_state_sub = LowStateSubscriber()
        #
        self.mujoco_model = mujoco.MjModel.from_xml_path(path_scene)
        self.mujoco_data = mujoco.MjData(self.mujoco_model)
        self.mujoco_qpos_default = self.mujoco_data.qpos.copy()
        #
        self.viewer = mujoco.viewer.launch_passive(self.mujoco_model, self.mujoco_data)
        #
        self.thread_lock = threading.Lock()
        #
        self.simulate_dt = simulate_dt
        self.viewer_dt = viewer_dt
        #
        self.mujoco_model.opt.timestep = simulate_dt

    #
    ##
    def start(self):
        #
        ##
        thread_viewer = threading.Thread(target = self.viewer_thread)
        thread_simulate = threading.Thread(target = self.simulate_thread)
        #
        thread_viewer.start()
        thread_simulate.start()

    #
    ##
    def simulate_thread(self):
        #
        ##
        while self.viewer.is_running() and self.low_state_sub.low_state is not None:
            #
            self.thread_lock.acquire()
            #
            self.mujoco_data.qvel = 0
            self.mujoco_data.qpos = self.mujoco_qpos_default
            #
            ##
            for joint_i in range(G1NumBodyJoint):
                #
                self.mujoco_data.qpos[joint_i + 7] = self.low_state_sub.low_state.motor_state[joint_i].q
            #
            mujoco.mj_step(self.mujoco_model, self.mujoco_data)
            #
            self.thread_lock.release()
            #
            time.sleep(self.simulate_dt)
        
    #
    ##
    def viewer_thread(self):
        #
        ##
        while self.viewer.is_running():
            #
            self.thread_lock.acquire()
            #
            self.viewer.sync()
            #
            self.thread_lock.release()
            #
            time.sleep(self.viewer_dt)


if __name__ == "__main__":
    #
    ##
    visualizer = Visualizer(0, "eno1")
    visualizer.start()