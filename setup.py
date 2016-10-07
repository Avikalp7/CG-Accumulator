from setuptools import setup
setup(
  name = 'CG-Acc',
  packages = ['CG-Acc'], # this must be the same as the name above
  version = '1.2.1',
  description = 'A console-based software to help accumulate CGPA / SGPA data and extract useful results for the students of IIT KGP.',
  author = 'Avikalp Srivastava',
  author_email = 'avikalp22@gmail.com',
  url = 'https://github.com/Avikalp7/CG-Accumulator', 
  # download_url = 'https://github.com/Avikalp7/Golden-Shoe/tarball/0.1',
  keywords = ['IIT', 'KGP', 'CGPA', 'CG-Acc', 'Avikalp Srivastava', 'CG Accumulator', 'Python', 'CG Acc'], 
  
  license = 'MIT',
  
  classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],

    install_requires=['requests==2.10.0', 'bs4', 'prettytable', 'eventlet'],
)
