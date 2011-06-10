from ..math import SE2_to_distance, pose_average, np, place
from ..graphs import DiGraph, reconstruct
from ..meat import  solve_dense


def place_other_nodes(G, paths, landmarks, Sl, nref):
    ndim = 2
    nlandmarks = len(landmarks)
    n = G.number_of_nodes()
    
    S = np.zeros((ndim, n))
    for i in range(n):
#                self.progress('placing other nodes', i, n)
        i_to_landmarks = [(l, len(paths[landmarks[l]][i])) 
                          for l in range(nlandmarks)]

        shortest = sorted(i_to_landmarks, key=lambda x:x[1])[:nref]
        references = np.zeros((ndim, nref))
        distances = np.zeros(nref)
        for r in range(len(shortest)):
            l, length = shortest[r]
            #  print('node %5d to landmark %5d = %5d steps' % (i, l, length))
            diff = reconstruct(G, paths[landmarks[l]][i])
            references[:, r] = Sl[:, l]
            distances[r] = SE2_to_distance(diff)
        S[:, i] = place(references, distances)
    return S

def place_other_nodes_simple(G, paths, landmarks, landmarks_solution):
    nlandmarks = len(landmarks)
    n = G.number_of_nodes()
    
    G2 = DiGraph()
    for i in range(n):
        i_to_landmarks = [(l, len(paths[landmarks[l]][i])) 
                          for l in range(nlandmarks)]
        l = sorted(i_to_landmarks, key=lambda x:x[1])[0][0]
        diff = reconstruct(G, paths[landmarks[l]][i])
        landmark_pose = landmarks_solution.node[l]['pose']
        pose = np.dot(landmark_pose, diff)
        
        G2.add_node(i, pose=pose)
    return G2 


def place_other_nodes_mref(G, paths, landmarks, landmarks_solutions, nref):
    nlandmarks = len(landmarks)
    n = G.number_of_nodes()
    
    G2 = DiGraph()
    
    for i in range(n):
        # We should not move landmarks... should we?
#        if i in landmarks:
#            G2.add_node(i, pose=landmarks_solutions.node[i]['pose'])
#            continue
            
#                self.progress('placing other nodes', i, n)
        i_to_landmarks = [(l, len(paths[landmarks[l]][i])) 
                          for l in range(nlandmarks)]

        shortest = sorted(i_to_landmarks, key=lambda x:x[1])[:nref]
        guesses = []
        for r in range(len(shortest)):
            l, length = shortest[r]
            #  print('node %5d to landmark %5d = %5d steps' % (i, l, length))
            lpose = landmarks_solutions.node[l]['pose']
            diff = reconstruct(G, paths[landmarks[l]][i])
            guess = np.dot(lpose, diff)
            guesses.append(guess)
        
        G2.add_node(i, pose=pose_average(guesses))

    return G2

from networkx import subgraph #@UnresolvedImport

def place_other_nodes_multi(G, paths, landmarks, landmarks_solution):
    nlandmarks = len(landmarks)
    n = G.number_of_nodes()
    
    G2 = DiGraph()
    
    landmark_group = {}
    for l in range(nlandmarks):
        landmark_group[l] = []
        
    for i in range(n):
        i_to_landmarks = [(l, len(paths[landmarks[l]][i])) 
                          for l in range(nlandmarks)]
        l_closest_to_i = sorted(i_to_landmarks, key=lambda x:x[1])[0][0]
        landmark_group[l_closest_to_i].append(i)
    
    for l in range(nlandmarks):
        landmark_pose = landmarks_solution.node[l]['pose']
        nchildren = len(landmark_group[l])
        print('Landmark %d has %d children' % (l, nchildren))
        # a landmark is always its own child
        if nchildren == 1:
            G2.add_node(landmark_group[l][0], pose=landmark_pose)
            continue
        if nchildren == 0: continue

        nodes = landmark_group[l] + [landmarks[l]]
        Gsub = subgraph(G, nodes) 
        
        Gsub_solution = solve_dense(Gsub, fix_node=landmarks[l],
                              fix_pose=landmark_pose)
        
        for i in landmark_group[l]:
            G2.add_node(i, pose=Gsub_solution.node[i]['pose'])
        
    return G2 
