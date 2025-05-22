
from .inspire_hand_defaut import *
from .inspire_dds import inspire_hand_touch,inspire_hand_ctrl,inspire_hand_state
from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize
from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.utils.thread import Thread

from pymodbus.client import ModbusTcpClient
from pymodbus.client import ModbusSerialClient

import numpy as np
import struct
import sys
import time
 
class ModbusDataHandlerDouble:
    def __init__(self, data=data_sheet, history_length=100, network=None, ip=None, port=6000, device_id=[1,2], use_serial=False, serial_port='/dev/ttyUSB0', baudrate=115200, states_structure=None, initDDS=True, max_retries=5, retry_delay=2):
        """_summary_
        Calling self.read() in a loop reads and returns the data, and publishes the DDS message at the same time        
        Args:
            data (dict, optional): Tactile sensor register definition. Defaults to data_sheet.
            history_length (int, optional): Hand state history_length. Defaults to 100.
            network (str, optional): Name of the DDS NIC. Defaults to None.
            ip (str, optional): ModbusTcp IP. Defaults to None will use 192.1686.11.210.
            port (int, optional): ModbusTcp IP port. Defaults to 6000.
            device_id (int, optional): Hand ID. Defaults to 1.
            LR (str, optional): Topic suffix l or r. Defaults to 'r'.
            use_serial (bool, optional): Whether to use serial mode. Defaults to False.
            serial_port (str, optional): Serial port name. Defaults to '/dev/ttyUSB0'.
            baudrate (int, optional): Serial baud rate. Defaults to 115200.
            states_structure (list, optional): List of tuples for state registers. Each tuple should contain (attribute_name, start_address, length, data_type). If None ,will publish All Data
            initDDS (bool, optional): Run ChannelFactoryInitialize(0),only need run once in all program
            max_retries (int, optional): Number of retries for connecting to Modbus server. Defaults to 3.
            retry_delay (int, optional): Delay between retries in seconds. Defaults to 2.
        Raises:
            ConnectionError: raise when connection fails after max_retries
        """        
        self.data = data
        self.history_length = history_length
        self.history = {
            'POS_ACT': [np.zeros(history_length) for _ in range(6)],
            'ANGLE_ACT': [np.zeros(history_length) for _ in range(6)],
            'FORCE_ACT': [np.zeros(history_length) for _ in range(6)],
            'CURRENT': [np.zeros(history_length) for _ in range(6)],
            'ERROR': [np.zeros(history_length) for _ in range(6)],
            'STATUS': [np.zeros(history_length) for _ in range(6)],
            'TEMP': [np.zeros(history_length) for _ in range(6)]
        }
        self.use_serial = use_serial
        
        self.states_structure = states_structure or [
            ('pos_act', 1534, 6, 'short'),
            ('angle_act', 1546, 6, 'short'),
            ('force_act', 1582, 6, 'short'),
            ('current', 1594, 6, 'short'),
            ('err', 1606, 3, 'byte'),
            ('status', 1612, 3, 'byte'),
            ('temperature', 1618, 3, 'byte')
        ]
        if self.use_serial:
            self.client = ModbusSerialClient(method='rtu', port=serial_port, baudrate=baudrate, timeout=1)
        else:
            if ip==None:
                self.client = ModbusTcpClient(defaut_ip, port=6000)
            else:
                self.client = ModbusTcpClient(ip, port=port)
                
        # 尝试连接 Modbus 服务器，带重试机制
        self.connect_to_modbus(max_retries, retry_delay)     
        self.device_id = device_id
       # 初始化 ChannelFactory
        try:
            if initDDS:
                if network is None:
                    ChannelFactoryInitialize(0, network)
                else:
                    ChannelFactoryInitialize(0)
                
        except Exception as e:
            print(f"Error during ChannelFactory initialization: {e}")
            # 这里可以添加日志记录或其他恢复机制
            return
        
        self.client.write_register(1004,1,self.device_id[0]) #reser error
        self.client.write_register(1004,1,self.device_id[1]) #reser error

        if not self.use_serial:
            self.pub = ChannelPublisher("rt/inspire_hand/touch/l", inspire_hand_touch)
            self.pub.Init()

            self.pub2 = ChannelPublisher("rt/inspire_hand/touch/r", inspire_hand_touch)
            self.pub2.Init()

        self.state_pub = ChannelPublisher("rt/inspire_hand/state/l", inspire_hand_state)
        self.state_pub.Init()
        
        self.state_pub2 = ChannelPublisher("rt/inspire_hand/state/r", inspire_hand_state)
        self.state_pub2.Init()  
         
        self.sub = ChannelSubscriber("rt/inspire_hand/ctrl/l", inspire_hand_ctrl)
        self.sub.Init(self.write_registers_callback, 10)
        
        self.sub = ChannelSubscriber("rt/inspire_hand/ctrl/r", inspire_hand_ctrl)
        self.sub.Init(self.write_registers_callback, 10)           
                   
    def connect_to_modbus(self, max_retries, retry_delay):
        """连接到 Modbus 服务器，并在失败时重试"""
        retries = 0
        while retries < max_retries:
            try:
                if not self.client.connect():
                    raise ConnectionError("Failed to connect to Modbus server.")
                print("Modbus client connected successfully.")
                return
            except ConnectionError as e:
                print(f"Connection attempt {retries + 1} failed: {e}")
                retries += 1
                if retries < max_retries:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("Max retries reached. Could not connect.")
                    raise   
    def write_registers_callback(self,msg:inspire_hand_ctrl):
        with modbus_lock:
            if msg.mode & 0b0001:  # 模式 1 - 角度
                self.client.write_registers(1486, msg.angle_set, self.device_id[0])
                self.client.write_registers(1486, msg.angle_set, self.device_id[1])

                # print('angle_set')
            if msg.mode & 0b0010:  # 模式 2 - 位置
                self.client.write_registers(1474, msg.pos_set, self.device_id[0])
                self.client.write_registers(1474, msg.pos_set, self.device_id[1])

                # print('pos_set')

            if msg.mode & 0b0100:  # 模式 4 - 力控
                self.client.write_registers(1498, msg.force_set, self.device_id[0])
                self.client.write_registers(1498, msg.force_set, self.device_id[1])

                # print('force_set')

            if msg.mode & 0b1000:  # 模式 8 - 速度
                self.client.write_registers(1522, msg.speed_set, self.device_id[0])
                self.client.write_registers(1522, msg.speed_set, self.device_id[1])

    def read(self):
        if not self.use_serial:
            touch_msg = get_inspire_hand_touch()
            touch_msg2 = get_inspire_hand_touch()

            matrixs = {}
            matrixs2 = {}

            for i, (name, addr, length, size, var) in enumerate(self.data):
                value = self.read_and_parse_registers(addr, length // 2,'short',device_id=self.device_id[0])
                value2 = self.read_and_parse_registers(addr, length // 2,'short',device_id=self.device_id[1])

                if value is not None:
                    setattr(touch_msg, var, value)
                    setattr(touch_msg2, var, value2)

                    matrix = np.array(value).reshape(size)
                    matrixs2 = np.array(value2).reshape(size)

                    matrixs[var]=matrix
                    matrixs2[var]=matrixs2

                    # matrixs.append(matrix)
            self.pub.Write(touch_msg)
            self.pub2.Write(touch_msg2)

        else:
            matrixs = {}
        # Read the states for POS_ACT, ANGLE_ACT, etc.
        states_msg = get_inspire_hand_state()
        states_msg2 = get_inspire_hand_state()

        for attr_name, start_address, length, data_type in self.states_structure:
            setattr(states_msg, attr_name, self.read_and_parse_registers(start_address, length, data_type,device_id=self.device_id[0]))
            setattr(states_msg2, attr_name, self.read_and_parse_registers(start_address, length, data_type,device_id=self.device_id[1]))

        self.state_pub.Write(states_msg)
        self.state_pub2.Write(states_msg2)

        return [{'states':{
            'POS_ACT': states_msg.pos_act,
            'ANGLE_ACT': states_msg.angle_act,
            'FORCE_ACT': states_msg.force_act,
            'CURRENT': states_msg.current,
            'ERROR': states_msg.err,
            'STATUS': states_msg.status,
            'TEMP': states_msg.temperature
        },'touch':matrixs
                },{'states':{
            'POS_ACT': states_msg2.pos_act,
            'ANGLE_ACT': states_msg2.angle_act,
            'FORCE_ACT': states_msg2.force_act,
            'CURRENT': states_msg2.current,
            'ERROR': states_msg2.err,
            'STATUS': states_msg2.status,
            'TEMP': states_msg2.temperature
        },'touch':matrixs
                }]

    def read_and_parse_registers(self, start_address, num_registers, data_type='short',device_id=1):
         with modbus_lock:
            # 读取寄存器
            response = self.client.read_holding_registers(start_address, num_registers, device_id)

            if not response.isError():
                if data_type == 'short':
                    # 将读取的寄存器打包为二进制数据
                    packed_data = struct.pack('>' + 'H' * num_registers, *response.registers)
                    # 将寄存器解包为带符号的 16 位整数 (short)
                    angles = struct.unpack('>' + 'h' * num_registers, packed_data)
                    return angles
                elif data_type == 'byte':
                    # 将每个 16 位寄存器拆分为两个 8 位 (uint8) 数据
                    byte_list = []
                    for reg in response.registers:
                        high_byte = (reg >> 8) & 0xFF  # 高 8 位
                        low_byte = reg & 0xFF          # 低 8 位
                        byte_list.append(high_byte)
                        byte_list.append(low_byte)
                    return byte_list
            else:
                print("Error reading registers")
                return None
            


