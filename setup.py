from setuptools import setup, find_packages

setup(
    name='FlapKine',
    version='0.1.0',
    description='Simulation of flapping wing micro air vehicles',
    author='Kalbhavi Vadhiraj',
    author_email='raj.31@iitj.ac.in',
    packages=find_packages(where='.', include=['app', 'app.*', 'src', 'src.*']),
    include_package_data=True,
    install_requires=[
        'streamlit',
        'bpy',  # Blender Python API - make sure it’s installed in the right environment
        'numpy',
        'matplotlib',
        'plotly',
        'pandas',
        'PyQt5',
        'PyQtWebEngine',
        'numpy-stl',
        'opencv-python-headless',
    ],
    entry_points={
        'console_scripts': [
            'flapkine = app.main:main',  # <- Adjust this based on your actual main entry
        ],
    },
    python_requires='>=3.6',
)
