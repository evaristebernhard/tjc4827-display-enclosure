from pathlib import Path
import sys,json
import numpy as np
from cadgen import read_step
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'checks'))
from mesh_utils import read_stl,check_triangles,check_3mf
report={}
for name in ('front','carrier'):
    step=read_step(ROOT/'STEP'/f'TJC4827_{name}.step')
    solids=step.solids()
    volume=sum(float(s.volume) for s in solids)
    stl=read_stl(ROOT/'STL'/f'TJC4827_{name}.stl')
    bounds=np.ptp(stl.reshape(-1,3),axis=0).tolist()
    report[name]={
        'stl':check_triangles(stl,volume,bounds),
        '3mf':check_3mf(ROOT/'3MF'/f'TJC4827_{name}.3mf',volume,bounds)
    }
(ROOT/'checks/mesh_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
