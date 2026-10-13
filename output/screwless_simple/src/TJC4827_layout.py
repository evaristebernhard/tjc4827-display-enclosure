from cadgen import build123d as bd, step
from TJC4827_front import TJC4827_front
from TJC4827_carrier import TJC4827_carrier
from geometry import carrier_transform,electronics_reference
@step(out='../STEP/TJC4827_layout.step')
def TJC4827_layout():
    return bd.Compound(children=[TJC4827_front(),carrier_transform(TJC4827_carrier()),electronics_reference()],label='TJC4827_simple_layout_references_not_for_printing')
if __name__=='__main__':
    TJC4827_layout()
