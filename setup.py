"""
setup.py

installation script
"""

from setuptools import setup, find_packages

PACKAGE_NAME = "nflprojections"


def run():
    setup(name=PACKAGE_NAME,
          version="0.2",
          description="python library for collecting and combining NFL projections",
          author="Eric Truett",
          author_email="sansbacon@gmail.com",
          license="MIT",
          packages=find_packages(),
          package_data={PACKAGE_NAME: ['data/*.*']},
          zip_safe=False
        )


if __name__ == '__main__':
    run()
