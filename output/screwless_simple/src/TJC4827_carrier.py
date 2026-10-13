from cadgen import step,stl,threemf
from geometry import make_carrier_print
@step(out='../STEP/TJC4827_carrier.step')
@stl(out='../STL/TJC4827_carrier.stl',mesh_tolerance=0.00023,mesh_angular_tolerance=0.12)
@threemf(out='../3MF/TJC4827_carrier.3mf',mesh_tolerance=0.00023,mesh_angular_tolerance=0.12)
def TJC4827_carrier():
    return make_carrier_print()
if __name__=='__main__':
    TJC4827_carrier()
