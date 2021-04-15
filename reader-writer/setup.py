from sys import version_info
from setuptools import setup

if version_info.major == 3 and version_info.minor < 6 or \
        version_info.major < 3:
    print('Your Python interpreter must be 3.6 or greater!')
    exit(1)

setup(name='reader-writer',
      description='A tool for taking cis-client results and printing them',
      url='https://github.com/metabolomics-us/carpy/tree/master/reader-writer',
      author='parker ladd bremer',
      author_email='plbremer@ucdavis.com',
      #need confirmation
      license='??????????????????????????????????????????????????????????????????',
      packages=['readerwriter'],
      scripts=[
      ],
      setup_requires=['pytest-runner'],
      tests_require=[
          'pytest',
          'pytest-watch',
      ],
      #directly copied, need confirmation
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
          'License :: ????????????????????????????????????/',
          'Topic :: Scientific/Engineering',
          'Intended Audience :: Science/Research',
      ])
