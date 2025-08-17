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
          zip_safe=False,
          install_requires=[
              'requests>=2.25.0',
              'beautifulsoup4>=4.9.0', 
              'pandas>=1.3.0',
              'numpy>=1.20.0',
          ],
          extras_require={
              'dev': [
                  'pytest>=6.0.0',
                  'pytest-cov>=2.10.0',
                  'mkdocs>=1.3.0',
                  'mkdocs-material>=8.0.0',
              ],
              'optional': [
                  'nflschedule>=0.2.0',
                  'nflnames>=0.1.0', 
                  'browser_cookie3>=0.17.0',
              ]
          }
        )


if __name__ == '__main__':
    run()
