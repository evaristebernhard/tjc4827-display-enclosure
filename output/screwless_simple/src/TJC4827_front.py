from cadgen import step,stl,threemf
from geometry import make_front
@step(out='../STEP/TJC4827_front.step')
@stl(out='../STL/TJC4827_front.stl',mesh_tolerance=0.00023,mesh_angular_tolerance=0.12)
@threemf(out='../3MF/TJC4827_front.3mf',mesh_tolerance=0.00023,mesh_angular_tolerance=0.12)
def TJC4827_front():
    return make_front()
if __name__=='__main__':
    TJC4827_front()
