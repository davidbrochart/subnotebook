from setuptools import setup

setup(
    name='subnotebook',
    version='0.0.1',
    description='Call notebooks as functions',
    author='David Brochart',
    author_email='david.brochart@gmail.com',
    packages=['subnotebook'],
    install_requires = [
        'ipython',
        'nbformat>=5',
        'nbclient>=0.2.0',
        'nteract-scrapbook @ git+https://github.com/davidbrochart/scrapbook@return_data#egg=nteract-scrapbook',
        'nest_asyncio'
    ],
    python_requires = '>=3.6',
)
