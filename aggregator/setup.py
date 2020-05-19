from sys import version_info

from setuptools import setup

if version_info.major == 3 and version_info.minor < 6 or \
        version_info.major < 3:
    print('Your Python interpreter must be 3.6 or greater!')
    exit(1)

setup(name='crag',
      version='0.0.1',
      description='Sample Aggregation module',
      url='https://github.com/berlinguyinca/carpy',
      authors='Diego Pedrosa, Gert Wohlgemuth',
      author_emails='dpedrosa@ucdavis.edu, wohlgemuth@ucdavis.edu',
      license='GPLv3',
      packages=['crag'],
      scripts=["bin/crag_local.py", "bin/crag_aws.py"],
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
