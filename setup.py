# setup.py
from setuptools import setup, find_packages

setup(
    name='flapping_wing_mav_simulation',
    version='0.1.0',
    description='Simulation of flapping wing micro air vehicles',
    author='Kalbhavi Vadhiraj',
    author_email='raj.31@iitj.ac.in',
    packages=find_packages(include=['src', 'src.*', 'app', 'app.*']),
    include_package_data=True,
    install_requires=[
        'streamlit',
        'bpy',  # Add other dependencies here
        'numpy',
        'matplotlib',
        'plotly',
        'pandas',
        'PyQt5',
        'PyQtWebEngine',
        'numpy-stl'

    ],
    entry_points={
        'console_scripts': [
            'flapping_wing_mav_simulation = FlapKine:main'
        ],
    },
    python_requires='>=3.6',
)
