from sys import version_info
from setuptools import setup

if version_info.major == 3 and version_info.minor < 6 or \
        version_info.major < 3:
    print('Your Python interpreter must be 3.6 or greater!')
    exit(1)

setup(name='cis-client',
      description='CIS client implementation',
      url='https://github.com/metabolomics-us/carpy/tree/master/cis-client',
      author='berlinguyinca',
      author_email='berlinguyinca@gmail.com',
      license='GPLv3',
      packages=['cisclient'],
      scripts=[
      ],
      setup_requires=['pytest-runner'],
      tests_require=[
          'pytest',
          'pytest-watch',
      ],
      install_requires=[
          'requests',
          'jsonschema',
          'pytest',
          'simplejson',
      ],
      include_package_data=True,
      zip_safe=False,
      classifiers=[
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Topic :: Scientific/Engineering',
          'Intended Audience :: Science/Research',
      ])
