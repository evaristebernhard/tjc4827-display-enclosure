from cadgen import build123d as bd, srgb
from parameters import *


def box(x,y,z,w,h,d):
    return bd.Pos(x,y,z)*bd.Box(w,h,d,align=(bd.Align.MIN,)*3)


def cyl(x,y,z,r,h):
    return bd.Pos(x,y,z)*bd.Cylinder(r,h,align=(bd.Align.CENTER,bd.Align.CENTER,bd.Align.MIN))


def rounded_plate(x,y,z,w,h,r,d):
    return bd.extrude(bd.Pos(x+w/2,y+h/2,z)*bd.RectangleRounded(w,h,r),amount=d)


def xy_prism(points,z,depth):
    area=sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points)))
    if area<0:points=list(reversed(points))
    return bd.extrude(bd.Pos(0,0,z)*bd.Polygon(*points,align=None),amount=depth)


def rail_void(mirror=False):
    xz=[(RAIL_OUTER_X,RAIL_BOTTOM),(RAIL_INNER_X,RAIL_BOTTOM),
        (RAIL_INNER_X,RAIL_OUTER_TOP+1.2*(RAIL_INNER_X-RAIL_OUTER_X)),
        (RAIL_OUTER_X,RAIL_OUTER_TOP)]
    if mirror:
        xz=[(CASE_W-x,z) for x,z in reversed(xz)]
    # Plane.XZ normal is -Y, negative amount grows along +Y.
    face=bd.Plane.XZ*bd.Polygon(*xz,align=None)
    return bd.extrude(face,amount=-RAIL_Y_END)


def make_front():
    case=rounded_plate(0,0,0,CASE_W,CASE_H,CORNER_R,CASE_D)
    case-=box(WALL,WALL,FRONT_T,CASE_W-2*WALL,CASE_H-2*WALL,CASE_D)
    case-=box(WINDOW_X,WINDOW_Y,-0.1,WINDOW_W,WINDOW_H,FRONT_T+0.2)
    for x,y in SCREEN_PADS:
        case+=cyl(x,y,FRONT_T,SCREEN_PAD_D/2,SCREEN_PAD_TOP-FRONT_T)
    # Small clearance fences: guide the metal mounting ears, not the glass.
    for x in (MODULE_X-2.2,MODULE_X+MODULE_W+0.6):
        for y in (MODULE_Y+7,MODULE_Y+MODULE_H-13):
            case+=box(x,y,FRONT_T,1.6,6.0,7.4)
    case-=rail_void()
    case-=rail_void(mirror=True)
    # Loading mouth is large enough for a pre-wired board carrier.
    case-=box(-0.1,-0.1,ENTRY_BOTTOM,CASE_W+0.2,WALL+0.8,CASE_D)
    case-=box(CASE_W-WALL-0.1,PORT_Y,PORT_Z,WALL+0.2,PORT_H,CASE_D)
    case.label='front_case';case.color=srgb('#526E86')
    return case


def carrier_in_assembly():
    carrier=box(COVER_X,COVER_Y,COVER_BOTTOM,COVER_W,COVER_H,COVER_T)
    # Trailing corner chamfers clear the shell's rounded inner corners.
    back_y=COVER_Y+COVER_H
    for xs in (COVER_X,CASE_W-COVER_X):
        sign=1 if xs<CASE_W/2 else -1
        triangle=[(xs,back_y),(xs+sign,back_y),(xs,back_y-1.0)]
        carrier-=xy_prism(triangle,COVER_BOTTOM-0.1,COVER_T+0.2)
    # Integral entry cap closes the large loading mouth; no separate fasteners.
    carrier+=box(COVER_X,COVER_Y,GATE_BOTTOM,COVER_W,GATE_T,COVER_TOP-GATE_BOTTOM)
    for x,y in STM_PAD_POINTS+ESP_PAD_POINTS:
        carrier+=cyl(x,y,BOARD_PAD_FACE_Z,BOARD_PAD_D/2,BOARD_STANDOFF)
    for x,y in STRAP_SLOTS:
        carrier-=box(x,y,COVER_BOTTOM-0.1,STRAP_SLOT_W,STRAP_SLOT_H,COVER_T+0.2)
    carrier.label='simple_loose_slide_carrier';carrier.color=srgb('#87ADB4')
    return carrier


def carrier_transform(shape):
    # Self-inverse rigid transform: outside face on the print bed, components up.
    return (bd.Pos(0,CASE_H,COVER_TOP)*bd.Rot(X=180))*shape


def make_carrier_print():
    return carrier_transform(carrier_in_assembly())


def electronics_reference():
    # Documented envelope stand-ins, not purchasable CAD or printable parts.
    frame=box(MODULE_X+8.25,MODULE_Y+3.0,SCREEN_FRONT_Z,105.5,67.2,SCREEN_TOTAL_T)
    ear_z=SCREEN_FRONT_Z+SCREEN_EAR_FRONT_TO_GLASS
    for x in (MODULE_X,MODULE_X+MODULE_W-7.2):
        frame+=rounded_plate(x,MODULE_Y,ear_z,7.2,MODULE_H,3.5,1.6)
    frame.label='screen_envelope';frame.color=srgb('#394452')
    stm=box(STM_X,STM_Y,PCB_BACK_Z-STM_FRONT_RESERVE,STM_W,STM_H,STM_FRONT_RESERVE+STM_BACK_RESERVE)
    for x,y in STM_PAD_POINTS:
        stm-=cyl(x,y,PCB_BACK_Z,BOARD_PAD_D/2+0.1,STM_BACK_RESERVE+0.1)
    stm.label='stm32_connected_keepout';stm.color=srgb('#46856A',0.55)
    esp=box(ESP_X,ESP_Y,PCB_BACK_Z-ESP_FRONT_RESERVE,ESP_W,ESP_H,ESP_FRONT_RESERVE+ESP_BACK_RESERVE)
    for x,y in ESP_PAD_POINTS:
        esp-=cyl(x,y,PCB_BACK_Z,BOARD_PAD_D/2+0.1,ESP_BACK_RESERVE+0.1)
    esp.label='esp01_connected_keepout';esp.color=srgb('#CDB570',0.55)
    return bd.Compound(children=[frame,stm,esp],label='reference_keepouts_not_for_printing')
