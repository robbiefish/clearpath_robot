#!/usr/bin/env python3

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

from clearpath_generator_common.common import LaunchFile, Package
from clearpath_generator_common.launch.writer import LaunchWriter
from clearpath_generator_common.launch.generator import LaunchGenerator
from clearpath_generator_robot.launch.sensors import SensorLaunch

from clearpath_config.platform.platform import Platform

import os


class RobotLaunchGenerator(LaunchGenerator):
    def generate_sensors(self) -> None:
        sensors_service_launch_writer = LaunchWriter(self.sensors_service_launch_file)
        sensors = self.clearpath_config.sensors.get_all_sensors()

        for sensor in sensors:
            if sensor.get_launch_enabled():
                sensor_launch = SensorLaunch(
                        sensor,
                        self.sensors_launch_path,
                        self.sensors_params_path)
                sensor_writer = LaunchWriter(sensor_launch.get_launch_file())
                # Add default sensor launch file
                sensor_writer.add_launch_file(sensor_launch.get_default_launch_file())
                # Generate sensor launch file
                sensor_writer.generate_file()
                # Add sensor to top level sensors launch file
                sensors_service_launch_writer.add_launch_file(sensor_launch.get_launch_file())

        sensors_service_launch_writer.generate_file()

    def generate_platform(self) -> None:
        platform_service_launch_writer = LaunchWriter(self.platform_service_launch_file)
        platform_service_launch_writer.add_launch_file(self.platform_launch_file)

        if self.platform_model == Platform.J100:
            # Add micro ros agent
            uros_node = LaunchFile.Node(
                name='micro_ros_agent',
                package='micro_ros_agent',
                executable='micro_ros_agent',
                arguments=[
                    'serial', '--dev', '/dev/clearpath/j100'
                ])
            platform_service_launch_writer.add_node(uros_node)

            # Set domain ID on MCU
            set_domain_id = LaunchFile.Process(
                name='set_domain_id',
                cmd=[
                    ['\'export ROS_DOMAIN_ID=0;\''],
                    ['FindExecutable(name=\'ros2\')',
                     '\' service call platform/mcu/set_domain_id \'',
                     '\' clearpath_platform_msgs/srv/SetDomainId \'',
                     '\'"domain_id: \'',
                     'EnvironmentVariable(\'ROS_DOMAIN_ID\', default_value=\'0\')',
                     '\'"\'']
                ])
            platform_service_launch_writer.add_process(set_domain_id)

            # IMU filter
            imu_filter_config = LaunchFile.LaunchArg(
                'imu_filter',
                default_value=os.path.join(self.platform_params_path, 'imu_filter.yaml')
            )
            platform_service_launch_writer.declare_launch_arg(imu_filter_config)

            imu_filter_node = LaunchFile.Node(
                package='imu_filter_madgwick',
                executable='imu_filter_madgwick_node',
                name='imu_filter_node',
                parameters=['imu_filter'],
                remappings=[
                  ('\'imu/data_raw\'', '\'platform/sensors/imu_0/data_raw\''),
                  ('\'imu/mag\'', '\'platform/sensors/imu_0/magnetic_field\''),
                  ('\'imu/data\'', '\'platform/sensors/imu_0/data\'')
                ],
            )
            platform_service_launch_writer.add_node(imu_filter_node)

            # Wireless watcher
            wireless_watcher_launch = LaunchFile(
                name='watcher',
                package=Package('wireless_watcher'),
                args={
                    'connected_topic': 'platform/wifi_connected'
                }
            )
            platform_service_launch_writer.add_launch_file(wireless_watcher_launch)

        platform_service_launch_writer.generate_file()