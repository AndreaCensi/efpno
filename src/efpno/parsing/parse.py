import sys
from ..math import np, SE2_from_xytheta
from . import AddVertex2D, AddEdge2D, Unknown
from efpno.parsing.structures import Equiv, SolveState, QueryState, Fix

def parse_line(line):
    # remove ending ';'
    if len(line) == 0:
        return []
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
        if len(args) != 4:
            raise Exception('Malformed vertex command with params %r' % rest)
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

# Note the ID
# 'ADD EDGE_XYT 5568 3419 3483 0.0641306 -0.0208247 0.00406006 2000 0 0 2000 0 2000;

def cmd_edge_xyt(cmd, rest): #@UnusedVariable
    args = parse_line(rest)
    if len(args) != 12:
        raise Exception('Malformed params: %r\n parsed as %s' % (rest, args))
    edge_id = args[0]
    id1 = args[1]
    id2 = args[2]
    assert isinstance(edge_id, int)
    assert isinstance(id1, int)
    assert isinstance(id2, int)
    x = args[3]
    y = args[4]
    th = args[5]
    pose = SE2_from_xytheta(np.array([x, y, th]))
    # TODO: read covariance
    inf = np.identity(3)
    return AddEdge2D(id1=id1, id2=id2, pose=pose, inf=inf)

def cmd_equiv(cmd, rest): #@UnusedVariable
    args = parse_line(rest)
    id1 = args[0]
    id2 = args[1]
    return Equiv(id1=id1, id2=id2)
    
def cmd_solve_state(cmd, rest): #@UnusedVariable
    args = parse_line(rest)
    if args: raise Exception('No arguments expected')
    return SolveState()

# QUERY_STATE;
# QUERY_STATE 1 2;
def cmd_query_state(cmd, rest): #@UnusedVariable
    args = parse_line(rest)
    return QueryState(args)

def cmd_fix(cmd, rest): #@UnusedVariable
    args = parse_line(rest)
    if len(args) != 1:
        raise Exception('Expected only one arg, got %r' % rest)
    return Fix(args[0])
    
commands = {}
# Wow, please find some agreement on these!
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
commands['ADD EDGE_XYT'] = cmd_edge_xyt
commands['EQUIV'] = cmd_equiv
commands['FIX'] = cmd_fix
commands['SOLVE_STATE'] = cmd_solve_state
commands['QUERY_STATE'] = cmd_query_state

def parse_command_stream(stream, raise_if_unknown=False):
    while True:
        oline = stream.readline()
        if oline == '': break
#        sys.stderr.write('< %r\n' % line)
#        sys.stderr.flush()
        line = oline.strip()
        if not line: 
            continue
        if line[-1] == '\n': line = line[:-1]
        if line[-1] == ';': line = line[:-1]
    
        for command in commands:
            if line.startswith(command):
                rest = line[len(command):]
                try:
                    result = commands[command](command, rest)
                except Exception as e:
                    msg = 'Could not parse line %r;\n%s' % (oline, e)
                    raise Exception(msg)
                yield result
                break
        else:
            if raise_if_unknown:
                raise Exception('Unknown command: %r' % line)
            else:
                yield Unknown(line)

parse = parse_command_stream # TODO: remove old name

def main():
    raise_if_unknown = True
    count = 0
    for x in parse(sys.stdin, raise_if_unknown=raise_if_unknown): 
        if count % 100 == 0:
            print count
        count += 1
        pass
    
    
