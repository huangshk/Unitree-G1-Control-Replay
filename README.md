# Unitree G1 Robot Control & Replay Platform

This repository provides a platform to run a Unitree G1 robot in 4 steps:
1. control the degrees of all 29 joints;
2. snapshot the degrees of all joints;
3. compose a script including all snapshots;
4. run the script to replay all joint degrees sequentially.

Such a paradigm offers several advantages:
1. It doesn't involve any kind of learning (_e.g._, reinforcement learning), making it easy for any users without deep learning background to run a humanoid robot.
2. Similarly, it doesn't require any kinematic knowledge, and users can run the robot in a "What You See Is What You Get" manner.
3. Joint degress, snapshots, and scripts are independent of source code, making it applicable to any kinds of tasks.
4. Snapshots and scripts can be easily modified, letting users tune current joint degrees or extend existing tasks.

Overall, this platform enables users to run the Unitree G1 robot for any tasks without knowing complicated robotics stuffs.
