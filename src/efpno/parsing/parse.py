import sys
from ..math import np, SE2_from_xytheta
from . import AddVertex2D, AddEdge2D, Unknown

def parse_line(line):
    # remove ending ';'
    if line[-1] == ';':
        line = line[:-1]
    if line[-1] == '\n':
        line = line[:-1]
    # tries to parse something as int, float, or str
    def try_parse(x):
        try:
            return int(x)
        except:
            try:
                return float(x)
            except:
                return x
            
    return map(try_parse, line.split())

def cmd_vertex2(line):
    args = parse_line(line)
    id = args[1]
    if len(args) > 2:
        xyt = args[2:5]
        pose = SE2_from_xytheta(np.array(xyt))
    else:
        pose = None
        
    return AddVertex2D(id, pose)

#EDGE2 2344 1345 1.08126 -0.0222521 -3.13184 1 0 1 1 0 0

def cmd_edge2(line):
    args = parse_line(line)
    id1 = args[1]
    id2 = args[2]
    x = args[3]
    y = args[4]
    th = args[5]
    pose = SE2_from_xytheta(np.array([x, y, th]))
    inf = np.identity(3)
    return AddEdge2D(id1=id1, id2=id2, pose=pose, inf=inf)

commands = {}
commands['VERTEX2'] = cmd_vertex2
commands['VERTEX_SE2'] = cmd_vertex2
commands['EDGE2'] = cmd_edge2
commands['EDGE_SE2'] = cmd_edge2

#
#ADD VERTEX_XYT 0;
#ADD VERTEX_XYT 1;
#ADD EDGE_XYT 0 0 1 .1 .2 .3 1 0 0 1 0 1;
#FIX 1;


def parse(stream, raise_if_unknown):
    for line in stream:
        for command in commands:
            if line.startswith(command):
                yield commands[command](line)
                break
        else:
            if raise_if_unknown:
                raise Exception('Unknown command: %r' % line)
            else:
                yield Unknown(line)

def main():
    raise_if_unknown = True
    count = 0
    for x in parse(sys.stdin, raise_if_unknown=raise_if_unknown):
#        print x
        if count % 100 == 0:
            print count
        count += 1
        pass
    
    
