import os
from setuptools import setup, find_packages

version = "0.1"

description = """ A solver for pose network optimization problems. """
long_description = description 


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    
    

setup(name='efpno',
      author="Andrea Censi",
      author_email="andrea@cds.caltech.edu",
      url='http://andreacensi.github.com/efpno/',
      
      description=description,
      long_description=long_description,
      keywords="SLAM mapping robotics pose network optimization",
      license="LGPL",
      
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
      ],

	  version=version,
      
      package_dir={'':'src'},
      packages=find_packages('src'),
      install_requires=[ 'PyContracts', 'PyGeometry', 'networkx', 'RepRep' ],
      tests_require=['nose'],
        entry_points={
         'console_scripts': [
           'efpno_test_parsing_stream = efpno.parsing.parse:main',
           'efpno_evaluation = efpno.statistics.evaluation_main:main',
           'efpno_tc_grid = efpno.graphs.grid:main',
           'efpno_simplify = efpno.script.simplify:main',
           'efpno_pipe = efpno.scripts.pipe:main',
           'efpno_plot = efpno.scripts.plot:main',
           'efpno_solve = efpno.scripts.solve:main',
           'efpno_slam_eval = efpno.scripts.slam_eval:main',
        ]
    }

)

