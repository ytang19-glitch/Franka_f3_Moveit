import os
from glob import glob

from setuptools import find_packages, setup


package_name = "fr3_moveit_python"


setup(

    # Package information
    name=package_name,
    version="0.0.1",

    # Python packages to install
    packages=find_packages(
        exclude=["test"]
    ),

    # Install package resources
    data_files=[
        (
            "share/ament_index/resource_index/packages",
            ["resource/" + package_name],
        ),
        (
            os.path.join(
                "share",
                package_name,
            ),
            ["package.xml"],
        ),
        (
            os.path.join(
                "share",
                package_name,
                "launch",
            ),
            glob("launch/*.launch.py"),
        ),
    ],

    # Runtime dependency
    install_requires=[
        "setuptools",
    ],

    zip_safe=True,

    # Maintainer information
    maintainer="yujietang",
    maintainer_email="ytang19@ualberta.ca",

    # Package description
    description=(
        "MoveItPy Cartesian pose-goal examples "
        "for the Franka FR3."
    ),
    

    license="Apache-2.0",

    tests_require=[
        "pytest",
    ],

    # ROS 2 executable commands; can be utlized as extension module 
    entry_points={
        "console_scripts": [
            "cartesian_move = fr3_moveit_python.cartesian_move:main",
            "gripper_control = fr3_moveit_python.gripper_control:main",
            "motion_test = fr3_moveit_python.motion_test:main",
            "pick_place = fr3_moveit_python.pick_place:main",
        ],
    },
)
