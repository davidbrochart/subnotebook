from setuptools import setup

setup(
    name='subnotebook',
    version='0.0.1',
    description='Call notebooks as functions',
    author='David Brochart',
    author_email='david.brochart@gmail.com',
    packages=['subnotebook'],
    install_requires = [
        'nbformat>=5'
    ],
    python_requires = '>=3.6',
)
