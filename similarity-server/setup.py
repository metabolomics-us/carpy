from sys import version_info

from setuptools import setup, find_packages

if version_info.major == 3 and version_info.minor < 8 or \
        version_info.major < 3:
    print('Your Python interpreter must be 3.8 or greater!')
    exit(1)

setup(name='similarity-server',
      description='Similarity algorithms as lambdas',
      url='https://github.com/metabolomics-us/carpy/tree/master/similarity-server',
      author='Diego Pedrosa',
      author_email='linuxmant@gmail.com',
      license='GPLv3',
      packages=find_packages(),
      scripts=[],
      setup_requires=['pytest-runner'],
      tests_require=[
          'pytest',
          'pytest-mock',
          'pytest-cov',
          'moto'
      ],
      install_requires=[
          'boto3',
          'botocore',
          'simplejson'
      ],
      include_package_data=True,
      zip_safe=False,
      classifiers=[
          'Programming Language :: Python :: 3.8',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Topic :: Scientific/Engineering',
          'Intended Audience :: Science/Research',
      ])
