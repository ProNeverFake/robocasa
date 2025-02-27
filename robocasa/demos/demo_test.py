import robocasa

import os

import argparse
import time
import xml.etree.ElementTree as ET

import mujoco
import mujoco.viewer
from pynput.keyboard import Listener
from robosuite.devices import Device
from termcolor import colored

from robocasa.models.robots.robot_utils import sample_robot_model

class DemoKeyboard(Device):
    """
    键盘控制类
    """
    def __init__(self):
        self._reset_state = 0 
        self._kill_state = 0
        self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def start_control(self):
        self._reset_state = 0
        self._kill_state = 0

    def get_controller_state(self):
        return dict(
            reset=self._reset_state,
            kill=self._kill_state,
        )

    def on_press(self, key):
        pass

    def on_release(self, key):
        try:
            if key.char == "q":
                self._kill_state = 1
            elif key.char == "n":
                self._reset_state = 1
        except AttributeError:
            pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mjcf",
        type=str,
        help="(可选)指定机器人模型xml文件路径,不指定则随机采样"
    )
    args = parser.parse_args()

    cam_settings = {
        "distance": 2.0,
        "elevation": -30,
    }

    device = DemoKeyboard()

    while True:
        if args.mjcf is not None:
            filepath = args.mjcf
        else:
            robot_info = sample_robot_model()
            filepath = robot_info["mjcf_path"]
            print()
            print(colored(f"机器人模型路径: {filepath}", "green"))

        model = mujoco.MjModel.from_xml_path(filepath)
        data = mujoco.MjData(model)

        if args.mjcf is None:
            print()
            print(colored("(按N查看下一个机器人, 按Q退出演示)", "yellow"))
        else:
            print(colored("(按Q退出演示)", "yellow"))

        device.start_control()

        viewer = mujoco.viewer.launch_passive(
            model,
            data,
            show_right_ui=False,
        )

        viewer.cam.distance = cam_settings["distance"] 
        viewer.cam.elevation = cam_settings["elevation"]

        time.sleep(0.5)

        while viewer.is_running():
            if device.get_controller_state()["kill"]:
                exit()
            if device.get_controller_state()["reset"]:
                break

        viewer.close()
        del viewer

        if args.mjcf is not None:
            break
