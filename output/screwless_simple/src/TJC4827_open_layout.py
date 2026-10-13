from cadgen import build123d as bd,step
from TJC4827_front import TJC4827_front
from TJC4827_carrier import TJC4827_carrier
from geometry import carrier_transform,electronics_reference
@step(out='../STEP/TJC4827_simple_open_layout.step')
def TJC4827_simple_open_layout():
    refs=electronics_reference().children
    carrier=TJC4827_carrier().moved(bd.Location((160,0,0)))
    stm=carrier_transform(refs[1]).moved(bd.Location((160,0,0)))
    esp=carrier_transform(refs[2]).moved(bd.Location((160,0,0)))
    return bd.Compound(children=[TJC4827_front(),refs[0],carrier,stm,esp],label='open_layout_for_review_not_for_printing')
if __name__=='__main__':
    TJC4827_simple_open_layout()
