from sys import version_info

from setuptools import setup, find_packages

if version_info.major == 3 and version_info.minor < 6 or \
        version_info.major < 3:
    print('Your Python interpreter must be 3.6 or greater!')
    exit(1)

from cisvis import __version__

setup(name='cisvis',
      version=__version__,
      description='compound identification service visualization utilities',
      url='https://github.com/berlinguyinca/stasis',
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
      ],
      install_requires=[
      ],
      include_package_data=True,
      zip_safe=False,
      classifiers=[
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Topic :: Scientific/Engineering :: Chemistry',
          'Intended Audience :: Science/Research',
      ])
