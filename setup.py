from setuptools import find_packages, setup

setup(
    name='pgorm',
    packages=find_packages(include=[ 'pgorm' ]),
    version='0.1.4',
    description='micro orm for  Postgres dataBase (wrapper psycopg2)',
    install_requires=['psycopg2==2.9.10'],
    author='ionson100@gmail.com',
)