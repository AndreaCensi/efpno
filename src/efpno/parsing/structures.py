from collections import namedtuple

AddVertex2D = namedtuple('AddVertex2d', 'id pose') 
#AddVertex3D = namedtuple('AddVertex3d', 'id', 'pose')
AddEdge2D = namedtuple('AddEdge2D', 'id1 id2 pose inf')
Fix = namedtuple('Fix', 'id')
Solve = namedtuple('Solve', '')
Query = namedtuple('Query', '')
Equiv = namedtuple('Equiv', 'id1 id2')

Unknown = namedtuple('Unknown', 'line')
#
#ADD VERTEX_XYT 0;
#ADD VERTEX_XYT 1;
#ADD EDGE_XYT 0 0 1 .1 .2 .3 1 0 0 1 0 1;
#FIX 1;
#SOLVE_STATE;
#QUERY_STATE;
#ADD VERTEX_XYT 2;
#ADD EDGE_XYT 1 1 2 .1 .2 .3 1 0 0 1 0 1;
#SOLVE_STATE;
#QUERY_STATE;
