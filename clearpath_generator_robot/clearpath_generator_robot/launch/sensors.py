# Software License Agreement (BSD)
#
# @author    Roni Kreinin <rkreinin@clearpathrobotics.com>
# @copyright (c) 2023, Clearpath Robotics, Inc., All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of Clearpath Robotics nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Redistribution and use in source and binary forms, with or without
# modification, is not permitted without the express permission
# of Clearpath Robotics.

from clearpath_config.sensors.types.sensor import BaseSensor
from clearpath_config.sensors.types.lidars_2d import HokuyoUST10, SickLMS1XX
from clearpath_config.sensors.types.lidars_3d import VelodyneLidar
from clearpath_config.sensors.types.cameras import IntelRealsense
from clearpath_config.sensors.types.imu import Microstrain
from clearpath_config.sensors.types.gps import (
    Garmin18x,
    NovatelSmart6,
    NovatelSmart7,
    SwiftNavDuro
)

from clearpath_generator_common.common import LaunchFile, Package, ParamFile
from clearpath_generator_common.launch.writer import LaunchWriter


class SensorLaunch():
    class BaseLaunch():
        CLEARPATH_SENSORS = 'clearpath_sensors'
        TOPIC_NAMESPACE = 'sensors/'
        CLEARPATH_SENSORS_PACKAGE = Package(CLEARPATH_SENSORS)

        # Launch arguments
        PARAMETERS = 'parameters'
        NAMESPACE = 'namespace'

        def __init__(self,
                     sensor: BaseSensor,
                     robot_namespace: str,
                     launch_path: str,
                     param_path: str) -> None:
            self.sensor = sensor
            self._robot_namespace = robot_namespace
            self.parameters = ParamFile(self.name, path=param_path)

            # Generated launch file
            self.launch_file = LaunchFile(
                self.name,
                path=launch_path)

            # Set launch args for default launch file
            self.launch_args = [
                (self.PARAMETERS, self.parameters.full_path),
                (self.NAMESPACE, self.namespace)
            ]

            self.default_sensor_launch_file = LaunchFile(
                self.model,
                package=self.CLEARPATH_SENSORS_PACKAGE,
                args=self.launch_args)

        def generate(self):
            sensor_writer = LaunchWriter(self.launch_file)
            # Add default sensor launch file
            sensor_writer.add(self.default_sensor_launch_file)
            # Generate sensor launch file
            sensor_writer.generate_file()

        @property
        def namespace(self) -> str:
            """Return sensor namespace"""
            if self._robot_namespace in ('', '/'):
                return f'{self.TOPIC_NAMESPACE}{self.sensor.name}'
            else:
                return f'{self._robot_namespace}/{self.TOPIC_NAMESPACE}{self.sensor.name}'

        @property
        def name(self) -> str:
            """Return sensor name"""
            return self.sensor.name

        @property
        def model(self) -> str:
            """Return sensor model"""
            return self.sensor.SENSOR_MODEL

    MODEL = {
        HokuyoUST10.SENSOR_MODEL: BaseLaunch,
        SickLMS1XX.SENSOR_MODEL: BaseLaunch,
        IntelRealsense.SENSOR_MODEL: BaseLaunch,
        Microstrain.SENSOR_MODEL: BaseLaunch,
        VelodyneLidar.SENSOR_MODEL: BaseLaunch,
        SwiftNavDuro.SENSOR_MODEL: BaseLaunch,
        Garmin18x.SENSOR_MODEL: BaseLaunch,
        NovatelSmart6.SENSOR_MODEL: BaseLaunch,
        NovatelSmart7.SENSOR_MODEL: BaseLaunch
    }

    def __new__(cls,
                sensor: BaseSensor,
                robot_namespace: str,
                launch_path: str,
                param_path: str) -> BaseLaunch:
        return SensorLaunch.MODEL[sensor.SENSOR_MODEL](
            sensor,
            robot_namespace,
            launch_path,
            param_path)
