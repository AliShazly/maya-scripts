import math

def crossp(a, b):
    """Cross product of two 3D vectors"""
    a1, a2, a3 = a
    b1, b2, b3 = b
    return (a2*b3 - a3*b2, a3*b1 - a1*b3, a1*b2 - a2*b1)

def dotp(a, b):
    """Dot product of two equal-dimensioned vectors"""
    return sum(aterm * bterm for aterm,bterm in zip(a, b))

# https://cs.brown.edu/research/pubs/pdfs/1999/Moller-1999-EBA.pdf
def get_rotation_matrix(f, t):
    """Get rotation matrix from one vector (f) to another (t)"""
    v = crossp(f, t)
    c = dotp(f, t)
    h = (1 - c) / (1 - (c ** 2))
    vx, vy, vz = v
    rotation_matrix = [
            [c + h*vx**2, h*vx*vy - vz, h*vx*vz + vy],
            [h*vx*vy+vz, c+h*vy**2, h*vy*vz-vx],
            [h*vx*vz - vy, h*vy*vz + vx, c+h*vz**2]
    ]
    return rotation_matrix

# https://www.learnopencv.com/rotation-matrix-to-euler-angles/
def rotation_matrix_to_euler(R):
    """Convert rotation matrix (R) to euler [x, y, z] format"""
    sy = math.sqrt(R[0][0] * R[0][0] +  R[1][0] * R[1][0])
     
    singular = sy < 1e-6
 
    if  not singular :
        x = math.atan2(R[2][1] , R[2][2])
        y = math.atan2(-R[2][0], sy)
        z = math.atan2(R[1][0], R[0][0])
    else :
        x = math.atan2(-R[1][2], R[1][1])
        y = math.atan2(-R[2][0], sy)
        z = 0
 
    return [x, y, z]

