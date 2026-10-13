from pathlib import Path
import sys,json
from cadgen import read_step,build123d as bd
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'src'))
from parameters import *
from geometry import carrier_transform,electronics_reference

front=read_step(ROOT/'STEP/TJC4827_front.step').solids()[0]
print_carrier=read_step(ROOT/'STEP/TJC4827_carrier.step')
carrier=carrier_transform(print_carrier).solids()[0]
assert front.is_valid and print_carrier.is_valid
assert len(print_carrier.solids())==1

def overlap(a,b):
    inter=a.intersect(b)
    return float(inter.volume) if hasattr(inter, 'volume') else sum(float(x.volume) for x in (inter or []))

closed_overlap=overlap(front,carrier)
assert closed_overlap<1e-6, f'Carrier interferes in seated position: {closed_overlap}'
refs=electronics_reference().children
for i,shape in enumerate(refs):
    assert overlap(front,shape)<1e-6,f'Reference {i} collides with shell'
    assert overlap(carrier,shape)<1e-6,f'Reference {i} collides with carrier'
screen=refs[0]
board_refs=refs[1:]
for board in board_refs:
    assert overlap(screen,board)<1e-6
    assert screen.distance_to(board)>0
sweep=[]
for y in (-100,-80,-60,-40,-20,-10,-3,-1,-.3,0):
    pose=carrier.moved(bd.Location((0,y,0)))
    interference=overlap(front,pose)
    assert interference<1e-6, f'Loose carrier slide collision at Y={y}: {interference}'
    for board in board_refs:
        moved=board.moved(bd.Location((0,y,0)))
        assert overlap(front,moved)<1e-6,f'Board hits shell during slide at {y}'
        assert overlap(screen,moved)<1e-6,f'Board hits screen during slide at {y}'
    sweep.append({'Y_mm':y,'carrier_overlap_mm3':interference})
for x,y in (STRAP_SLOTS[0],STRAP_SLOTS[2]):
    strap_shape=bd.Pos(x,y+STRAP_SLOT_H,COVER_BOTTOM-STRAP_THICKNESS_RESERVE)*bd.Box(STRAP_SLOT_W,69.5,STRAP_THICKNESS_RESERVE,align=(bd.Align.MIN,)*3)
    assert overlap(strap_shape,carrier)<1e-6
    for board in board_refs:assert overlap(strap_shape,board)<1e-6
assert WINDOW_X<=AA_X and WINDOW_Y<=AA_Y
assert WINDOW_X+WINDOW_W>=AA_X+AA_W and WINDOW_Y+WINDOW_H>=AA_Y+AA_H
report={'revision':'D simple loose-slide','saved_step_valid':True,'single_connected_solids':True,
'case_envelope_mm':[CASE_W,CASE_H,CASE_D],
'carrier_print_envelope_mm':[float(print_carrier.bounding_box().size.X),float(print_carrier.bounding_box().size.Y),float(print_carrier.bounding_box().size.Z)],
'closed_carrier_overlap_mm3':closed_overlap,'carrier_slide_checks':sweep,
'PCB_back_z_mm':PCB_BACK_Z,'nominal_screen_back_z_mm':SCREEN_FRONT_Z+SCREEN_TOTAL_T,
'board_front_reserve_gap_to_screen_mm':PCB_BACK_Z-STM_FRONT_RESERVE-(SCREEN_FRONT_Z+SCREEN_TOTAL_T),
'loose_slide_clearance_mm':{'left_and_right':COVER_X-RAIL_OUTER_X,'bottom':COVER_BOTTOM-RAIL_BOTTOM,'leading_and_trailing':COVER_Y},
'retention':'No snap latch. Secure with temporary tape or hook-and-loop while prototyping.',
'strap_inside_clearance_to_stm_back_reserve_mm':COVER_BOTTOM-STRAP_THICKNESS_RESERVE-(PCB_BACK_Z+STM_BACK_RESERVE),
'window_covers_AA':True,'tested_scope':'Saved front shell and loose-slide carrier validity, board envelopes, no seated overlap, and slide sweep at selected poses. External plugs must be disconnected before opening.',
'unverified':['Real screen ear Z datum','Actual wired board height','Fit on the intended printer and material','Temporary tape retention','Power bank dimensions and output stability']}
(ROOT/'checks/cad_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
