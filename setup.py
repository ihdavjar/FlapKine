# setup.py
from setuptools import setup, find_packages

setup(
    name='flapping_wing_mav_simulation',
    version='0.1.0',
    description='Simulation of flapping wing micro air vehicles',
    author='Kalbhavi Vadhiraj',
    author_email='raj.31@iitj.ac.in',
    packages=find_packages(include=['src', 'src.*']),
    include_package_data=True,
    install_requires=[
        'streamlit',
        'bpy',  # Add other dependencies here
    ],
    entry_points={
        'console_scripts': [
            'flapping_wing_mav_simulation = blender.generate_frames:main',
        ],
    },
)
