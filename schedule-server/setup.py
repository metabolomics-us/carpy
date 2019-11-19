from sys import version_info

from setuptools import setup, find_packages

if version_info.major == 3 and version_info.minor < 6 or \
        version_info.major < 3:
    print('Your Python interpreter must be 3.6 or greater!')
    exit(1)


setup(name='stasis',
      version='0.0.1',
      description='Sample scheduling and processing api, which links stasis and the aggregator',
      url='https://github.com/berlinguyinca/carpy',
      author='Gert Wohlgemuth',
      author_email='wohlgemuth@ucdavis.edu',
      license='GPLv3',
      packages=find_packages(),
      scripts=[],
      setup_requires=['pytest-runner'],
      tests_require=[
          'pytest',
          'pytest-mock',
          'pytest-cov',
          'moto',
          # 'moto==1.3.3'
      ],
      install_requires=[
          'boto3',
          'botocore',
          'untangle',
          'jsonschema',
          'watchdog',
          'simplejson',
          'boltons'
      ],
      include_package_data=True,
      zip_safe=False,
      classifiers=[
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Topic :: Scientific/Engineering :: Chemistry',
          'Intended Audience :: Science/Research',
      ])
