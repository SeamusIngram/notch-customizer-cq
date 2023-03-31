import cadquery as cq
from cadquery import exporters
import math
fname = "gate_0-6mm"
#fname = 'shell_front'
path = f'gates/{fname}.step'
result = cq.importers.importStep(path)

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
        
# Adjust the notch depth, can tune for single and double notches
notch_depth_double = 11
diagonal_depth_double = 11.6
notch_depth_single = 11
diagonal_depth_single = 11
# Change these parameters for different notch styles
convex=True
convexity = 0.035
convexity_weight = 0.5
rounded=True
round_radius = 0.25
flared = True
flare_ang = 50
sloped = True
gate_angle = 56
# If you want sloped notches, use this to adjust depth instead of the notch_depth. Higher number = shallower notch
adjust_depth = 1.5
# Notch angles, ordered counter clockwise starting with NorthWest
#Follows the quadrants of a circle, if you're familiar
angs = [(17,73),(17,73),(17,73),(17,73)];
# Don't Adjust These
flare_length = 2
h = 3
offset = 3
h_offset = 14.5
r_loft = h/math.tan(math.radians(gate_angle))

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
    # when notched at an angle with a loft, the angle at the top of the gate is actually too close to the diagonal 
    # A small correction is applied; The math used is probably overkill
    # Depth is also adjusted because if the start depth was the same as a vertical notch, it would be too deep 
    if sloped:
        r_adjust = adjust_depth*math.cos(math.radians(gate_angle))
        path_vector = cylindricalToCartesian(r_loft,changeAngleQuadrant(45-offset,quadrant),h)
        path = (cq.Edge.makeLine((0,0,0),path_vector))
        angle_adjust1 = math.degrees(math.atan2(math.cos(math.radians(theta1))*(path_vector[1]-path_vector[0]*math.tan(math.radians(theta1))),notch_depth1))
        angle_adjust2 = math.degrees(math.atan2(math.cos(math.radians(theta2))*(path_vector[0]-path_vector[1]*math.tan(math.radians(theta2))),notch_depth2))
        notch_depth1 = notch_depth1-r_adjust
        notch_depth2 = notch_depth2-r_adjust
        diag_depth = diag_depth-r_adjust
        theta1 = changeAngleQuadrant(a1-abs(angle_adjust1),quadrant)
        theta2 = changeAngleQuadrant(a2+abs(angle_adjust2),quadrant)

    # Creates notch from diagonal to desired angle
    # Done twice per quadrant
    notch1 =(cq.Workplane("front")
             .polarLineTo(diag_depth, thetaM-offset))
    if convex:
        notch1 = notch1.threePointArc(polarToCartesian(notch_depth2*(1-convexity),(theta2+thetaM)*convexity_weight-offset),polarToCartesian(notch_depth2, theta2-offset))
    else:
        notch1 = notch1.polarLineTo(notch_depth2, theta2-offset)
    if flared:
        notch1=notch1.polarLine(-flare_length,flare_ang1-offset)
    notch1=notch1.close()
    if sloped:
        notch1=notch1.sweep(path)
    else:
        notch1=notch1.extrude(h)
    
    notch2 =(cq.Workplane("front")
             .polarLineTo(diag_depth, thetaM-offset))
    if convex:
        notch2 = notch2.threePointArc(polarToCartesian(notch_depth1*(1-convexity),(theta1+thetaM)*convexity_weight-offset),polarToCartesian(notch_depth1, theta1-offset))
    else:
        notch2 = notch2.polarLineTo(notch_depth1, theta1-offset)
    if flared:
        notch2=notch2.polarLine(-flare_length,flare_ang2-offset)
    notch2=notch2.close()
    if sloped:
        notch2=notch2.sweep(path)
    else:
        notch2=notch2.extrude(h)

    # Join notches together if making two notches, discard if angle was 0 (if you don't want a notch in a given position)
    if theta1%90 == 0 and theta2%90 ==0:
        notch =None
    elif theta1%90 == 0:
        notch=notch1
    elif theta2%90 == 0:
        notch=notch2
    else:
        notch=notch1.union(notch2)
    
    if rounded and notch is not None:
        notch = notch.edges().fillet(round_radius)
    return notch.translate((0,0,h_offset))

# If you want to visualize the cutting body, you can uncomment this!
# Only does one quadrant, and you need to hard code the angles
#test=notch(17,73,1)

# Work done here
for i, ang in enumerate(angs):
    try:
        result = result.cut(notch(ang[0],ang[1],i+1))
    except ValueError:
        pass

export_string=fname
export_string+=f"_notch_depth_{notch_depth_double}"
export_string+=f"_adjustment_{adjust_depth}_gate_angle_{gate_angle}" if sloped else ""
export_string+= f"_convex_{convexity}_{convexity_weight}" if convex else "_straight"
export_string+= f"_filleted_{round_radius}" if rounded else ""
export_string += f"_flare_angle_{flare_ang}" if flared else ""
export_string += "_angles"
for ang in angs:
    export_string+= f"_{ang[0]}_{ang[1]}"
exporters.export(result,f'gates/exports/{export_string}.step')