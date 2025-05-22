from version import __version__
from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='FlapKine',
    version=__version__,
    author='Kalbhavi Vadhiraj',
    author_email='raj.31@iitj.ac.in',
    description='A Simulation Toolkit for the Kinematics of Flapping-Wing Micro Aerial Vehicles',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(where='.', include=['app', 'app.*', 'src', 'src.*']),
    include_package_data=True,
    install_requires=[
        'pandas==2.0.2',
        'numpy==1.26.4',
        'numpy-stl==3.1.1',
        'scipy==1.10.1',
        'scikit-learn==1.5.2',
        'PyQt5==5.15.9',
        'QtAwesome==1.4.0',
        'vtk==9.4.1',
        'opencv-python-headless==4.10.0.84',
    ],
    entry_points={
        'console_scripts': [
            'flapkine = app.main:main',  # <- Adjust this based on your actual main entry
        ],
    },
    python_requires='==3.10.3',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
)
