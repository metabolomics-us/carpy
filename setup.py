from sys import version_info
from setuptools import setup

if version_info.major == 3 and version_info.minor < 6 or \
        version_info.major < 3:
    print('Your Python interpreter must be 3.6 or greater!')
    exit(1)

from stasis import __version__

setup(name='stasis',
      version=__version__,
      description='Sample Tracking and Supplementary Information System',
      url='https://github.com/berlinguyinca/stasis',
      author='Gert Wohlgemuth',
      author_email='wohlgemuth@ucdavis.edu',
      license='GPLv3',
      packages=['stasis'],
      scripts=[],
      setup_requires=['pytest-runner'],
      tests_require=['pytest', 'pytest-mock', 'pytest-cov', 'moto'],
      install_requires=[
          'boto3',
          'untangle',
          'jsonschema',
          'watchdog',
          'simplejson'
      ],
      include_package_data=True,
      zip_safe=False,
      classifiers=[
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Topic :: Office/Business :: Financial :: Investment',
          'Intended Audience :: Science/Research',
      ])
