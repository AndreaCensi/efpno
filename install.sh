EFPNO
=====

This is a Python program that solves the pose network optimization problem.
It is entering the `RSS2011 SLAM evaluation workshop`__ with the expectation of being the slowest, least precise entry. 

.. __: http://slameval.willowgarage.com/workshop/

This is because it is designed to solve the global pose optimization, using only the pose-to-pose constraints. Contrary to most methods, the optimization step is not iterative, but rather the solution is found in one shot. (There is, however, an initial graph simplication phase which is iterative).

Documentation (a technical report) is being written, check back soon :-).

Examples

These are examples of optimization instances
<img>


Right now, it is written in Python and takes 2-3 minutes to run on these examples. I think it could get easily under 1 second if written in C++ (we will see).

Also, there are many "dead" parts in the code, which would benefit from some cleanup.



Downloading
-----------

For downloading the branch to be used for RSS2011, use this Git command: ::

	$ git clone -b RSS2011 git://github.com/AndreaCensi/efpno.git

Otherwise, simply use: ::

	$ git clone git://github.com/AndreaCensi/efpno.git
	
to download a more current version.

Installation instructions
---------------------------------

These installation instructions have been tested on Ubuntu 10.04.

First, install the requirements that come as Ubuntu packages: ::

	$ sudo apt-get install python-pip python-numpy python-scipy git-core python-nose
	
Then, install a few Python packages using ``pip``: ::
	 
	$ sudo pip install --upgrade PyContracts
	$ sudo pip install --upgrade PyGeometry
	$ sudo pip install --upgrade RepRep

At this point, install the executables: ::

	$ cd efpno
	$ sudo python setup.py develop



Overview of executables included
---------------------------------

Various executable are installed.

``efpno_slam_eval`` implements the SLAM evaluation protocol. It is very slow (~2 minutes for a graph with 3500 nodes). It only makes sense to analyze it in batch mode.

This is an example of using the ``evaluation`` program: ::

	evaluation `which efpno_slam_eval` /data/manhattanOlson3500.txt  0 > log


``efpno_solve`` reads a graph and optimizes it. Usage: ::

	efpno_solve [options] logfile > output


``efpno_simplify`` only does the simplification step. Usage: ::

	efpno_solve [options] logfile > output

	
``efpno_plot`` creates a few figures. Usage: ::

	efpno_plot [options] --outdir REPORT_DIR  logfile 
	

