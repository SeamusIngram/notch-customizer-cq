import cadquery as cq
from cadquery import exporters
import math
from ocp_vscode import show, show_object, reset_show, set_port, set_defaults, get_defaults
set_port(3939)

reset_show() # use for reapeated shift-enter execution to clean object buffer
set_defaults(axes=True, black_edges=True, transparent=False, collapse=1, grid=(True, True, True))

#fname = "gate_0-6mm"
fname = "gateplate-stock"
#fname = 'shell_front'
path = f'gates/{fname}.step'
result = cq.importers.importStep(path)

# Notch angles, with quadrants ordered counter clockwise starting with North East
# Follows the quadrants of a circle, if you're familiar
# Angle is always taken with respect to the horizontal

# On OEM, the gate isn't perfectly symmetrical. 
# To get the bottom and top gates to cut a similar depth into the gate, the lower depth must be slightly more
oem_gate = True
oem_bottom_depth = 0.2                                
angs = [(15,75),(15,75),(15,75),(15,75)]
# Adjust the notch depth, can tune for single and double notches
notch_depth_double = 11.2
diagonal_depth_double = 11.8
notch_depth_single = 11
diagonal_depth_single = 11
# Change these parameters for different notch styles
convex = True
convexity = 0.035
convexity_weight = 0.8
rounded = True
round_radius = 0.25
flared = True
flare_ang = 50
sloped = True
gate_angle = 56
# If you want sloped notches, use this to adjust depth instead of the notch_depth. 
# Higher number = shallower notch
adjust_sloped_depth = 1.75

# Don't adjust these, unless you're using a different model than the provided ones
offset = 3
h_offset = 14.5
# Probably don't touch these
flare_length = 2
h = 3
r_sloped = h/math.tan(math.radians(gate_angle))

#Uncomment these settings for a SASI gate - 19mm
# angs = [(15,75),(15,75),(15,75),(15,75)]
# notch_depth_double = 9.7
# diagonal_depth_double = 9.6
# notch_depth_single = 11
# diagonal_depth_single = 11
# offset = 0
# h_offset = -4
# h=5
# sloped = False
# convex = True
# convexity = 0.05
# convexity_weight = 0.5
# rounded = True
# round_radius = 0.5
# flared = True
# flare_ang = 40

# threePointArc does not accept polar coordinates, so need to convert
def polarToCartesian(r,theta):
    print(theta)
    x = math.cos(math.radians(theta))*r
    y = math.sin(math.radians(theta))*r
    return(x,y)
# Moves the angle to the correct quadrant
def changeAngleQuadrant(angle,quadrant):
    if quadrant == 2:
        return 180-angle
    elif quadrant == 3:
        return 180 + angle
    elif quadrant == 4:
        return -angle
    else:
        return angle
# Cylidrical to Cartersian coordinates
# Used to generate the notch path for sloped notches
def cylindricalToCartesian(r,theta,h):
    x=r*math.cos(math.radians(theta))
    y=r*math.sin(math.radians(theta))
    z = h
    return (x,y,z)
# Creates notch from diagonal to desired angle
# Called twice per quadrant
def make_single_notch(notch_ang,diag_ang,notch_depth,diag_depth,flare_ang):        
    notch =(cq.Workplane("front")
             .polarLineTo(diag_depth, diag_ang-offset))
    if convex:
        notch = notch.threePointArc(polarToCartesian(notch_depth*(1-convexity),(notch_ang*convexity_weight)+(1-convexity_weight)*diag_ang-offset),polarToCartesian(notch_depth, notch_ang-offset))
    else:
        notch = notch.polarLineTo(notch_depth, notch_ang-offset)
    if flared:
        notch=notch.polarLine(-flare_length,flare_ang-offset)
    notch=notch.close()

    if sloped:
        notch=(notch.workplane(offset=h)
               .polarLineTo(diag_depth+r_sloped, diag_ang-offset))
        if convex:
            notch = notch.threePointArc(polarToCartesian((notch_depth+r_sloped)*(1-convexity),(notch_ang*convexity_weight)+(1-convexity_weight)*diag_ang-offset),polarToCartesian(notch_depth+r_sloped, notch_ang-offset))
        else:
            notch = notch.polarLineTo(notch_depth+r_sloped, notch_ang-offset)
        if flared:
            notch=notch.polarLine(-(flare_length+r_sloped),flare_ang-offset)
        notch=notch.close().loft(combine=True)
    else:
        notch=notch.extrude(h)
    return notch                              

def notch(a1,a2,quadrant):
    theta1 = changeAngleQuadrant(a1,quadrant)
    theta2 = changeAngleQuadrant(a2,quadrant)
    thetaM = changeAngleQuadrant(45,quadrant)
    thetaQ = changeAngleQuadrant(22.5,quadrant)
    flare_ang1 = changeAngleQuadrant(flare_ang,quadrant)
    flare_ang2 = changeAngleQuadrant(90-flare_ang,quadrant)
    # Checks if single or double notching, use appropriate depth
    # Extra step adjusts depth based on notch angle, so the depth into the gate should not be affected by angle
    depth_factor1 = math.cos(math.radians(5.5))/abs(math.cos(math.radians(theta1-thetaM+thetaQ)))
    depth_factor2 = math.cos(math.radians(5.5))/abs(math.cos(math.radians(theta2-thetaM-thetaQ)))
    if theta1%90 == 0 or theta2%90 ==0:
        notch_depth1 = notch_depth_single*depth_factor1
        notch_depth2 = notch_depth_single*depth_factor2
        diag_depth = diagonal_depth_single
    else:
        notch_depth1 = notch_depth_double*depth_factor1
        notch_depth2 = notch_depth_double*depth_factor2
        diag_depth = diagonal_depth_double
    if oem_gate and (quadrant > 2):
        notch_depth1 += oem_bottom_depth
        notch_depth2 += oem_bottom_depth
        diag_depth += oem_bottom_depth
    # when making sloped notches, the bottom depth must be brought in, or the notches will be too deep
    if sloped:
        r_adjust = adjust_sloped_depth*math.cos(math.radians(gate_angle))
        notch_depth1 = notch_depth1-r_adjust
        notch_depth2 = notch_depth2-r_adjust
        diag_depth = diag_depth-r_adjust

    notch1 = make_single_notch(theta1,thetaM,notch_depth1,diag_depth,flare_ang1)
    notch2 = make_single_notch(theta2,thetaM,notch_depth2,diag_depth,flare_ang2)

    # Join notches together if making two notches, discard if angle was 0 (if you don't want a notch in a given position)
    if theta1%90 == 0 and theta2%90 ==0:
        notch =None
    elif theta1%90 == 0:
        notch=notch2
    elif theta2%90 == 0:
        notch=notch1
    else:
        notch=notch1.union(notch2)
    
    if rounded and notch is not None:
        notch = notch.edges().fillet(round_radius)
    return notch.translate((0,0,h_offset))

# If you want to visualize the cutting body, you can uncomment this!
# Only does one quadrant, and you need to hard code the angles
# test=notch(17,73,1)
# show_object(
#     test,
#     # three-cad-viewer args
#     collapse="1",
#     reset_camera=True,
#     ortho=True
# )


# Work done here
for i, ang in enumerate(angs):
    try:
        result = result.cut(notch(ang[0],ang[1],i+1))
    except ValueError:
        pass


show_object(
    result,
    # three-cad-viewer args
    collapse="1",
    reset_camera=True,
    ortho=True
)

export_string=fname
export_string+=f"_oem_" if oem_gate else ""
export_string+=f"_notch_depth_{notch_depth_double}"
export_string+=f"_adjustment_{adjust_sloped_depth}_gate_angle_{gate_angle}" if sloped else ""
export_string+= f"_convex_{convexity}_{convexity_weight}" if convex else "_straight"
export_string+= f"_filleted_{round_radius}" if rounded else ""
export_string += f"_flare_angle_{flare_ang}" if flared else ""
export_string += "_angles"
for ang in angs:
    export_string+= f"_{ang[0]}_{ang[1]}"
export_string += "_cq"
exporters.export(result,f'gates/exports/{export_string}.step')
# If you prefer stl
#exporters.export(result,f'exports/{export_string}.stl')
