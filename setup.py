from setuptools import setup, find_packages
import os

setup(name = 'oosheet',
      version = '0.1',
      description = 'OpenOffice.org Spreadsheet scripting library',
      long_description = open(os.path.join(os.path.dirname(__file__), "README")).read(),
      author = "Luis Fagundes",
      author_email = "lhfagundes@hacklab.com.br",
      license = "The MIT License",
      packages = find_packages(),
      install_requires = ['uno'],
#      url = 'http://oosheet.hacklab.com.br/',
      classifiers = [
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Office/Business :: Financial :: Spreadsheet',
        ],
      
)
