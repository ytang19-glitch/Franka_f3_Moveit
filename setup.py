import os
from glob import glob

from setuptools import find_packages, setup


package_name = "fr3_moveit_python"


setup(
    name=package_name,
    version="0.0.1",

    packages=find_packages(
        exclude=["test"]
    ),

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

    install_requires=[
        "setuptools",
    ],

    zip_safe=True,

    maintainer="yujietang",
    maintainer_email="your_email@example.com",

    description=(
        "MoveItPy Cartesian pose-goal examples "
        "for the Franka FR3."
    ),

    license="Apache-2.0",

    tests_require=[
        "pytest",
    ],

    entry_points={
        "console_scripts": [
            (
                "cartesian_move = "
                "fr3_moveit_python.cartesian_move:main"
            ),
        ],
    },
)
