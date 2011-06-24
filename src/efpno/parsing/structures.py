from collections import namedtuple

AddVertex2D = namedtuple('AddVertex2d', 'id pose') 
#AddVertex3D = namedtuple('AddVertex3d', 'id', 'pose')
AddEdge2D = namedtuple('AddEdge2D', 'id1 id2 pose inf')
Equiv = namedtuple('Equiv', 'id1 id2')


# Evaluation
SolveState = namedtuple('SolveState', '')
QueryState = namedtuple('QueryState', 'ids')
Fix = namedtuple('Fix', 'id')


# Catch all
Unknown = namedtuple('Unknown', 'line')
