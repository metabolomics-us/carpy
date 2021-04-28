from sys import version_info
from setuptools import setup

if version_info.major == 3 and version_info.minor < 8 or \
        version_info.major < 3:
    print('Your Python interpreter must be 3.8 or greater!')
    exit(1)

setup(name='similarity-client',
      description='Similarity algorithms client implementation',
      url='https://github.com/metabolomics-us/carpy/tree/master/similarity-client',
      author='diego',
      author_email='linuxmant@gmail.com',
      license='GPLv3',
      packages=['similarity_client'],
      scripts=[],
      setup_requires=['pytest-runner'],
      tests_require=[
          'pytest',
          'pytest-watch',
      ],
      install_requires=[
          'requests',
          'pytest',
      ],
      include_package_data=True,
      zip_safe=False,
      classifiers=[
          'Programming Language :: Python :: 3.8',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Topic :: Scientific/Engineering',
          'Intended Audience :: Science/Research',
      ])
