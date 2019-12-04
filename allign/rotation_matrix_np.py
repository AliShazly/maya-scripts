import math
import numpy as np

# https://cs.brown.edu/research/pubs/pdfs/1999/Moller-1999-EBA.pdf
def get_rotation_matrix(f, t):
    """Get rotation matrix from one vector (f) to another (t)"""
    v = np.cross(f, t)
    u = v / np.linalg.norm(v)
    c = np.dot(f, t)
    h = (1 - c) / (1 - (c ** 2))
    vx, vy, vz = v
    rotation_matrix = [
            [c + h*vx**2, h*vx*vy - vz, h*vx*vz + vy],
            [h*vx*vy+vz, c+h*vy**2, h*vy*vz-vx],
            [h*vx*vz - vy, h*vy*vz + vx, c+h*vz**2]
    ]
    return np.array(rotation_matrix)

# https://www.learnopencv.com/rotation-matrix-to-euler-angles/
def rotation_matrix_to_euler(R):
    """Convert rotation matrix (R) to euler [x, y, z] format"""
    sy = math.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])
     
    singular = sy < 1e-6
 
    if  not singular :
        x = math.atan2(R[2,1] , R[2,2])
        y = math.atan2(-R[2,0], sy)
        z = math.atan2(R[1,0], R[0,0])
    else :
        x = math.atan2(-R[1,2], R[1,1])
        y = math.atan2(-R[2,0], sy)
        z = 0
 
    return np.array([x, y, z])

