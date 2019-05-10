from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="gDrive",
    version="0.0.1",
    install_requires=requirements,
    author="Island Global Management LLC",
    author_email="jonathan@island-global.com",
    description="Basic Authorization and File Retrieval from GDrive"
)
