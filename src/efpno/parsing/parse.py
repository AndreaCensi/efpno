import sys
from ..math import np, SE2_from_xytheta
from . import AddVertex2D, AddEdge2D, Unknown
from efpno.parsing.structures import Equiv

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

def cmd_vertex2(cmd, rest): #@UnusedVariable
    args = parse_line(rest)
    id = args[0]
    if len(args) > 1:
        xyt = args[1:4]
        pose = SE2_from_xytheta(np.array(xyt))
    else:
        pose = None
        
    return AddVertex2D(id, pose)

#EDGE2 2344 1345 1.08126 -0.0222521 -3.13184 1 0 1 1 0 0

def cmd_edge2(cmd, rest): #@UnusedVariable
    args = parse_line(rest)
    if len(args) < 5:
        raise Exception('Malformed params: %r\n parsed as %s' % (rest, args))
    id1 = args[0]
    id2 = args[1]
    x = args[2]
    y = args[3]
    th = args[4]
    pose = SE2_from_xytheta(np.array([x, y, th]))
    # TODO: read covariance
    inf = np.identity(3)
    return AddEdge2D(id1=id1, id2=id2, pose=pose, inf=inf)

def cmd_equiv(cmd, rest):
    args = parse_line(rest)
    id1 = args[0]
    id2 = args[1]
    return Equiv(id1=id1, id2=id2)
    
    
commands = {}
commands['VERTEX2'] = cmd_vertex2
commands['VERTEX_SE2'] = cmd_vertex2
commands['VERTEX_XYT'] = cmd_vertex2
commands['ADD VERTEX2'] = cmd_vertex2
commands['ADD VERTEX_SE2'] = cmd_vertex2
commands['ADD VERTEX_XYT'] = cmd_vertex2
commands['EDGE2'] = cmd_edge2
commands['EDGE_SE2'] = cmd_edge2
commands['EDGE_XYT'] = cmd_edge2
commands['ADD EDGE2'] = cmd_edge2 # XXX
commands['ADD EDGE_SE2'] = cmd_edge2
commands['ADD EDGE_XYT'] = cmd_edge2
commands['EQUIV'] = cmd_equiv

#
#ADD VERTEX_XYT 0;
#ADD VERTEX_XYT 1;
#ADD EDGE_XYT 0 0 1 .1 .2 .3 1 0 0 1 0 1;
#FIX 1;


def parse(stream, raise_if_unknown):
    for line in stream:
        if line[-1] == '\n': line = line[:-1]
        if line[-1] == ';': line = line[:-1]
    
        for command in commands:
            if line.startswith(command):
                rest = line[len(command):]
                yield commands[command](command, rest)
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
    
    
