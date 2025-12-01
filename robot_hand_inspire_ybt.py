# this file is legacy, need to fix.
import numpy as np

from enum import IntEnum
import threading
import time
import lcm
from exlcm import hand_motor_cmd_t
from exlcm import hand_motor_state_t
from multiprocessing import Process, shared_memory, Array, Lock

inspire_tip_indices = [4, 9, 14, 19, 24]
Inspire_Num_Motors = 6

class Inspire_Controller:
    def __init__(self, left_trigger_array=None, right_trigger_array=None,
                 dual_hand_data_lock=None, dual_hand_state_array=None,
                 dual_hand_action_array=None, fps=100.0, Unit_Test=False):
        print("Initialize Inspire_Controller with Trigger Control...")
        self.fps = fps
        self.Unit_Test = Unit_Test
        
        # 初始化LCM
        self.lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=255")
        self.subscription = self.lc.subscribe("HAND_MOTOR_STATE", self.hand_handler)

        # 共享数组用于手部状态
        self.left_hand_state_array = Array('d', Inspire_Num_Motors, lock=True)
        self.right_hand_state_array = Array('d', Inspire_Num_Motors, lock=True)

        # 初始化订阅线程
        self.subscribe_state_thread = threading.Thread(target=self._subscribe_hand_state)
        self.subscribe_state_thread.daemon = True
        self.subscribe_state_thread.start()

        # 等待连接
        # while True:
        #     if any(self.right_hand_state_array):
        #         break
        #     time.sleep(0.01)
        #     print("[Inspire_Controller] Waiting to subscribe lcm...")

        # 启动控制进程
        hand_control_process = Process(
            target=self.control_process, 
            args=(left_trigger_array, right_trigger_array,
                  self.left_hand_state_array, self.right_hand_state_array,
                  dual_hand_data_lock, dual_hand_state_array, dual_hand_action_array)
        )
        hand_control_process.daemon = True
        hand_control_process.start()

        print("Initialize Inspire_Controller with Trigger Control OK!\n")

    def control_process(self, left_trigger_array, right_trigger_array,
                              left_hand_state_array, right_hand_state_array,
                              dual_hand_data_lock=None, dual_hand_state_array=None, 
                              dual_hand_action_array=None):
        self.running = True

        # 初始化手部控制命令
        self.hand_cmd = hand_motor_cmd_t()
        
        # 初始化为全开状态
        left_q_target = np.ones(Inspire_Num_Motors, dtype=float)
        right_q_target = np.ones(Inspire_Num_Motors, dtype=float)

        try:
            while self.running:
                start_time = time.time()
                
                # 读取触发器输入
                left_trigger = 0.0
                right_trigger = 0.0
                # if left_trigger_array is not None:
                #     left_trigger = left_trigger_array.value
                #     print("left_trigger:",left_trigger)
                # if right_trigger_array is not None:
                #     right_trigger = right_trigger_array.value
                
                if left_trigger_array is not None:
                    with left_trigger_array.get_lock():  # ✅ 获取锁
                        left_trigger = left_trigger_array.value
                    # print(f"[CONTROL] 左手触发器值: {left_trigger:.2f}")
                if right_trigger_array is not None:
                    with right_trigger_array.get_lock():  # ✅ 获取锁
                        right_trigger = right_trigger_array.value
                    # print(f"[CONTROL] 右手触发器值: {right_trigger:.2f}")

                # 基于触发器控制手部
                left_q_target = self._trigger_to_hand_control(left_trigger, is_left=True)
                right_q_target = self._trigger_to_hand_control(right_trigger, is_left=False)

                # 获取手部状态数据
                state_data = np.concatenate((
                    np.array(left_hand_state_array[:]), 
                    np.array(right_hand_state_array[:])
                ))

                # 组合动作数据
                action_data = np.concatenate((left_q_target, right_q_target))

                # 更新共享数组
                if dual_hand_action_array and dual_hand_data_lock:
                    with dual_hand_data_lock:
                        dual_hand_action_array[:] = action_data

                # 发送控制命令
                self.ctrl_dual_hand(left_q_target, right_q_target)
                
                # 控制频率
                current_time = time.time()
                time_elapsed = current_time - start_time
                sleep_time = max(0, (1 / self.fps) - time_elapsed)
                time.sleep(sleep_time)
                
        finally:
            print("Inspire_Controller has been closed.")

    def _trigger_to_hand_control(self, trigger_value, is_left=True):
        """
        将触发器输入转换为手部控制
        trigger_value: 0.0-1.0 触发器值
        is_left: 是否是左手
        """
        # 初始化所有关节为张开状态
        q_target = np.ones(Inspire_Num_Motors, dtype=float)
        
        # 触发器值直接控制抓握力度
        # trigger_value = 0.0: 全开 (1.0)
        # trigger_value = 1.0: 全闭 (0.0)
        grip_strength = 1.0 - trigger_value
        
        # 应用到所有手指
        for i in range(4):  # 小指、无名指、中指、食指
            q_target[i] = grip_strength
        
        # 拇指弯曲（与主要手指同步）
        q_target[4] = grip_strength
        
        # 拇指旋转（保持中间位置）
        q_target[5] = 0.5
        
        return q_target

    # 其他方法保持不变...
    def hand_handler(self, channel, data):
        hand_state = hand_motor_state_t.decode(data)
        if hand_state is not None:
            for idx, id in enumerate(Inspire_Left_Hand_JointIndex):
                self.right_hand_state_array[idx] = hand_state.q[id]
            for idx, id in enumerate(Inspire_Right_Hand_JointIndex):
                self.left_hand_state_array[idx] = hand_state.q[id]

    def _subscribe_hand_state(self):
        while True:
            self.lc.handle()
            time.sleep(0.002)

    def ctrl_dual_hand(self, left_q_target, right_q_target):
        for idx, id in enumerate(Inspire_Left_Hand_JointIndex):             
            self.hand_cmd.q_des[id] = left_q_target[idx]         
        for idx, id in enumerate(Inspire_Right_Hand_JointIndex):             
            self.hand_cmd.q_des[id] = right_q_target[idx] 
            # print("self.hand_cmd.q_des[id]:",self.hand_cmd.q_des[id])
        self.lc.publish("HAND_MOTOR_CMD", self.hand_cmd.encode())

# 枚举定义保持不变
class Inspire_Right_Hand_JointIndex(IntEnum):
    kRightHandPinky = 0
    kRightHandRing = 1
    kRightHandMiddle = 2
    kRightHandIndex = 3
    kRightHandThumbBend = 4
    kRightHandThumbRotation = 5

class Inspire_Left_Hand_JointIndex(IntEnum):
    kLeftHandPinky = 6
    kLeftHandRing = 7
    kLeftHandMiddle = 8
    kLeftHandIndex = 9
    kLeftHandThumbBend = 10
    kLeftHandThumbRotation = 11