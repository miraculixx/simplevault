import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='simplevault',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',  
    description='Simple file based vault system - store and deploy secrets, secured.',
    long_description=README,
    author='miraculixx',
    author_email='miraculixx@gmx.ch',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: Commercial', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # replace these appropriately if you are using Python 3 
        'Programming Language :: Python :: 2', 
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'pyaes==1.3.0',
        'tinys3==0.1.11',
    ], 
    dependency_links=[
    ]
)
