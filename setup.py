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
        'pandas==2.0.2',
        'numpy==1.26.4',
        'numpy-stl==3.1.1',
        'scipy==1.10.1',
        'scikit-learn==1.5.2',
        'PyQt5==5.15.9',
        'QtAwesome==1.4.0',
        'vtk==9.4.1',
        'bpy==4.0.0',
    ],
    entry_points={
        'console_scripts': [
            'flapkine = app.main:main',  # <- Adjust this based on your actual main entry
        ],
    },
    python_requires='>=3.6',
)
