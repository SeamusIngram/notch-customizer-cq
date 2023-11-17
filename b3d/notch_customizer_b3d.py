from build123d import *
import math
from ocp_vscode import show, show_object, reset_show, set_port, set_defaults, get_defaults, Collapse
set_port(3939)

reset_show() # use for reapeated shift-enter execution to clean object buffer
set_defaults(axes=True, black_edges=True, transparent=False, collapse=Collapse.LEAVES, grid=(True, True, True))

#fname = "gate_0-6mm"
fname = "gateplate-stock"
#fname = 'shell_front'
path = f'gates/{fname}.step'
gate = import_step(path)

# Notch angles, with quadrants ordered counter clockwise starting with North East
# Follows the quadrants of a circle, if you're familiar
# Angle is always taken with respect to the horizontal

# On OEM, the gate isn't perfectly symmetrical. 
# To get the bottom and top gates to cut a similar depth into the gate, the lower depth must be slightly more
oem_gate = True
oem_bottom_depth = 0.4                         
angs = [(15,75),(15,75),(15,75),(15,75)]
# Adjust the notch depth, can tune for single and double notches
notch_depth_double = 10.7
diagonal_depth_double = 11.5
notch_depth_single = 10.7
diagonal_depth_single = 11.15
# Change these parameters for different notch styles
convex = True
convexity = 0.03
convexity_weight = 0.8
rounded = True
round_radius = 0.25
flared = True
flare_ang = 30
sloped = True
gate_angle = 56
# If you want sloped notches, use this to adjust depth instead of the notch_depth. 
# Higher number = shallower notch
adjust_sloped_depth = 1.75

# Don't adjust these, unless you're using a different model than the provided ones
offset = 3
h_offset = Location((0,0,14),(0,0,0))
# Probably don't touch these
flare_length = 2
h = 3
r_sloped = h/math.tan(math.radians(gate_angle))
# threePointArc does not accept polar coordinates, so need to convert

def polarToCartesian(r,theta):
    print(theta)
    x = math.cos(math.radians(theta))*r
    y = math.sin(math.radians(theta))*r
    return(x,y)

def changeAngleQuadrant(angle,quadrant):
    if quadrant == 2:
        return 180-angle
    elif quadrant == 3:
        return 180 + angle
    elif quadrant == 4:
        return -angle
    else:
        return angle
    
def notch_sketch(a1,a2,a_diag,af1,af2,d1,d2,d_diag):
  with BuildLine() as points:
    notch_point1 = polarToCartesian(d1,a1)
    notch_point2 = polarToCartesian(d2,a2)
    diag_point = polarToCartesian(d_diag,a_diag)
    if (a1+offset)%90 == 0:
      Line((0,0),diag_point)
    else:
      if flared:
        f1 = PolarLine(notch_point1,-flare_length,af1)
        Line((0,0),f1@1)
      else:
        Line((0,0),notch_point1)
      if convex:
        midpoint_r1 = d1*(1-convexity)
        midpoint_theta1 = (a1*convexity_weight)+(1-convexity_weight)*a_diag
        curve_midpoint1 = polarToCartesian(midpoint_r1,midpoint_theta1)
        ThreePointArc(notch_point1,curve_midpoint1,diag_point)
      else:
        Line(notch_point1,diag_point)

    if (a2+offset)%90 == 0:
      Line((0,0),diag_point)
    else:
      if convex:
        midpoint_r2 = d2*(1-convexity)
        midpoint_theta2 = (a2*convexity_weight)+(1-convexity_weight)*a_diag
        curve_midpoint2 = polarToCartesian(midpoint_r2,midpoint_theta2)
        ThreePointArc(notch_point2,curve_midpoint2,diag_point)
      else:
        Line(diag_point,notch_point2)
      if flared:
        f2 = PolarLine(notch_point2,-flare_length,af2)
        Line(f2@1,(0,0))
      else:
        Line(notch_point2,(0,0))
    return points

               
def make_notch(a1,a2,quadrant):
  theta1 = changeAngleQuadrant(a1,quadrant) - offset
  thetaM = changeAngleQuadrant(45,quadrant) - offset
  thetaQ = changeAngleQuadrant(22.5,quadrant)
  theta2 = changeAngleQuadrant(a2,quadrant) - offset
  flare_ang1 = changeAngleQuadrant(flare_ang,quadrant) - offset
  flare_ang2 = changeAngleQuadrant(90-flare_ang,quadrant) - offset
  # Checks if single or double notching, use appropriate depth
  # Extra step adjusts depth based on notch angle, so the depth into the gate should not be affected by angle
  depth_factor1 = math.cos(math.radians(5.5))/abs(math.cos(math.radians(theta1-thetaM+thetaQ)))
  depth_factor2 = math.cos(math.radians(5.5))/abs(math.cos(math.radians(theta2-thetaM-thetaQ)))
  if a1%90 == 0 or a2%90 ==0:
      notch_depth1 = notch_depth_single*depth_factor1
      notch_depth2 = notch_depth_single*depth_factor2
      diag_depth = diagonal_depth_single
  else:
      notch_depth1 = notch_depth_double*depth_factor1
      notch_depth2 = notch_depth_double*depth_factor2
      diag_depth = diagonal_depth_double
  if oem_gate and (quadrant > 2) and sloped:
      notch_depth1 += oem_bottom_depth/4
      notch_depth2 += oem_bottom_depth/4
      diag_depth += oem_bottom_depth
  if sloped:
    r_adjust = adjust_sloped_depth*math.cos(math.radians(gate_angle))
    notch_depth1 -= r_adjust
    notch_depth2 -= r_adjust
    diag_depth -= r_adjust
  
  with BuildPart() as notch:
    with BuildSketch() as bottom:
      points = notch_sketch(theta1,theta2,thetaM,flare_ang1,flare_ang2,
                            notch_depth1,notch_depth2,diag_depth)
      make_face(points.line)
    if sloped:
      with BuildSketch(Plane.XY.offset(h)) as top:
        points = notch_sketch(theta1,theta2,thetaM,flare_ang1,flare_ang2,
                              notch_depth1+r_sloped,notch_depth2+r_sloped,diag_depth+r_sloped)
        make_face(points.line)
      loft(sections=[bottom.sketch,top.sketch])
    else:
      extrude(amount=h)
    if rounded:
      fillet(notch.edges(),radius=round_radius)
  notch.part.move(h_offset)
  # Uncomment if you want to see the cutting body
  # show_object(notch.part)
  return notch

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
export_string += "_b3d"

for i, ang in enumerate(angs):
  try:
    tool = make_notch(ang[0],ang[1],i+1)
    gate = gate.cut(tool.part)
  except:
    pass
   
  #  show_object(tool)
show_object(gate)
gate.export_step(f'gates/exports/{export_string}.step')
# Uncomment for STL
# gate.export_stl(f'gates/exports/{export_string}.stl')
