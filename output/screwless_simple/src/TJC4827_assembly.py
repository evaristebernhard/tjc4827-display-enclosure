from cadgen import build123d as bd, step
from TJC4827_front import TJC4827_front
from TJC4827_carrier import TJC4827_carrier
from geometry import carrier_transform
@step(out='../STEP/TJC4827_assembly.step')
def TJC4827_assembly():
    front=TJC4827_front()
    carrier=carrier_transform(TJC4827_carrier())
    return bd.Compound(children=[front,carrier],label='TJC4827_simple_D')
if __name__=='__main__':
    TJC4827_assembly()
