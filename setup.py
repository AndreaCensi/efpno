import os
from setuptools import setup, find_packages

version = "0.1"

description = """
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor 
"""

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    
long_description = read('README.rst')
    

setup(name='efpno',
      author="Andrea Censi",
      author_email="andrea@cds.caltech.edu",
#      url='AUTHOR_URL',
      
      description=description,
      long_description=long_description,
      keywords="slam mapping",
      license="GPL",
      
      classifiers=[
        'Development Status :: 4 - Beta',
        # 'Intended Audience :: Developers',
        # 'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        # 'Topic :: Software Development :: Quality Assurance',
        # 'Topic :: Software Development :: Documentation',
        # 'Topic :: Software Development :: Testing'
      ],

	  version=version,
#      download_url='http://github.com/GITHUB_USER/GITHUB_PROJECT/tarball/%s' % version,
      
      package_dir={'':'src'},
      packages=find_packages('src'),
      install_requires=[ 'PyContracts' ],
      tests_require=['nose'],
        entry_points={
         'console_scripts': [
           'efpno_test_parsing_stream = efpno.parsing.parse:main',
           'efpno_evaluation = efpno.script.evaluation_main:main',
           'efpno_simplification = efpno.script.graph_simplification_demo:main',
           'efpno_pipe = efpno.script.io:main',
           'efpno_plot = efpno.script.plot:main',
        ]
    }

)

