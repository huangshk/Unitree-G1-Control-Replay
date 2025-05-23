#
##
ConstPi = 3.141592654

G1NumBodyJoint = 29

#
##
class G1Body:

    # Left leg
    L_HipPitch = 0
    L_HipRoll = 1
    L_HipYaw = 2
    L_Knee = 3
    L_AnklePitch = 4
    # LeftAnkleB = 4
    L_AnkleRoll = 5
    # LeftAnkleA = 5

    # Right leg
    R_HipPitch = 6
    R_HipRoll = 7
    R_HipYaw = 8
    R_Knee = 9
    R_AnklePitch = 10
    # RightAnkleB = 10
    R_AnkleRoll = 11
    # RightAnkleA = 11

    WaistYaw = 12
    WaistRoll = 13          # NOTE: INVALID for g1 23dof/29dof with waist locked
    # WaistA = 13             # NOTE: INVALID for g1 23dof/29dof with waist locked
    WaistPitch = 14         # NOTE: INVALID for g1 23dof/29dof with waist locked
    # WaistB = 14             # NOTE: INVALID for g1 23dof/29dof with waist locked

    # Left arm
    L_ShoulderPitch = 15
    L_ShoulderRoll = 16
    L_ShoulderYaw = 17
    L_Elbow = 18
    L_WristRoll = 19
    L_WristPitch = 20     # NOTE: INVALID for g1 23dof
    L_WristYaw = 21       # NOTE: INVALID for g1 23dof

    # Right arm
    R_ShoulderPitch = 22
    R_ShoulderRoll = 23
    R_ShoulderYaw = 24
    R_Elbow = 25
    R_WristRoll = 26
    R_WristPitch = 27    # NOTE: INVALID for g1 23dof
    R_WristYaw = 28      # NOTE: INVALID for g1 23dof

    kNotUsedJoint = 29      # NOTE: Weight

#
##
class G1Hand:
    #
    class L:
        #
        Pinky = 0
        Ring = 1
        Middle = 2
        Index = 3
        ThumbBend = 4
        ThumbRotate = 5

    class R:
        #
        Pinky = 0
        Ring = 1
        Middle = 2
        Index = 3
        ThumbBend = 4
        ThumbRotate = 5

# print(len([motor_id for (motor_id, _) in G1Joint.__dict__.items() if motor_id[0] != "_"]))