# notch-customizer-py
Cadquery/Build123d version of parametric notching script for Gamecube Controllers. Should support any GCC shell design ideas!
Based on my notch-customizer made with OpenSCAD, and has many of the same capabilities. I'm more comfortable with python, so I'll probably be updating this version only going forward.

## y tho?
Custom GCC motherboards like the Phob and Goomwave support notch calibration, and so it is easier to produce notched Gamecube Controllers. Notches for these controllers do not have to be made specifically for one controller, and do not need to be as precise. Therefore, you can notch a shell ahead of time, and then calibrate when the controller is assemled. Lots of cool custom controller projects are using 3D printing to experiment with new shell shapes, built-in notches, or easily swappable gates. I came up with this script to try and make it so that anybody could easily customize and hopefully get a shell or gate 3d printed with the notches they wanted. Do I think that computer generated, 3D fabricated notches will replace talented modders and OEM shells? No, the feel of well made notches will certainly be better, but I do think if 3D printed gates can be shown to be consistent and relatively durable, it will allow many more people to have access to low cost options.

# Dependencies
[CadQuery](https://github.com/CadQuery/cadquery) and [Build123d](https://github.com/gumyr/build123d) are python modules that allow you to design parametric 3D models programmatically. There are several advantages over OpenSCAD for my workflow.
- Import and export of .step files. This is probably the biggest draw, as being able to work with a step file makes manual adjustments after running the script much easier
- Faster rendering of geometry
- Automatic export and file naming with built-in functions
- More powerful native geometry options. For example: curves, fillets, and lofts. All of which are used in this script
- Access to standard python operations and syntax. This is a personal reason, but I find OpenSCAD finnicky in some areas, and am quite comfortable with python

From the Build123d github, it describes itself as an evolution of Cadquery, with a less restrictive API that enables the full python toolbox. As such, Build123d statements will be more familiar to those used to python syntax, and I find it more intuitive to create geometry with. Since the functions will be slightly different, the notches created by the two scripts will be slightly different for the same paramenters. Currently, both versions of the notch customizer have feature parity, but going forward changes will likely be made to the Build123d script first. Certain features may not ever be ported to the CadQuery version. Any feature discrepancies will be noted.

The [OCP CAD Viewer for VS Code](https://github.com/bernhard-42/vscode-ocp-cad-viewer) is an extension that allows you to develop and view your geometry directly in VS Code. It is easy to install, and will set up all the additional components for both CadQuery or Build123d. Just follow the instructions in its readme. This is my current preferred way to work with this project. If you wish to use a different environment (There are suggestions in the Build123d [documentation](https://build123d.readthedocs.io/en/latest/external.html)) you might have to adjust the script, as the functions that display the models use the ocp-vscode library.

# Parameters
## Angles
The headline feature is that you can specify the angle of each notch. The notch is created by cutting material from the diagonal of the gate all the way to the desired angle. There is currently no way to have notches that appear as a 'tooth' in the gate (like the infamous [Multishine Notches](https://multishine.tech/collections/wp-content/uploads/2022/01/full-notches-smash-ultimate-gamecube.png)). This means you cannot have more that one notch in each octant of the gate. The angle of a given notch can only be 1-44 or 46-89 degrees, depending on the notch. The angles are stored in the **angs** list, where each index contains a pair of angles. The first value accepts angles 1-44 and the second 46-89. The notches are ordered starting from the North East quadrant of the gate, and move around the quadrant counter clockwise. Note the angle is always taken from the horizontal, so an angle of 17 degrees in the South West quadrant would create a shallow angle, which you might use for perfect wavedashes.

![Various Angles](/img/angles.png)

If you do not want a notch at a specific (For example, you want wavedash notches only), you can enter 0 for that angle. If you have one notch in a quadrant, the script will use different depth values, in case you have different preferences for quadrants with one (referred to as a single) or two (double) notches.
 
## Depth
 You may adjust the depth of your notches with the **notch_depth** and **diagonal_depth**, which control how far into the gate it gets cuts at those two points. As mentioned above, you can choose different depths for single notches and double notches. This is mostly because I found that I might prefer the diagonal of the gate to be intact with a single notch, but did not mind cutting deeper into the diagonal with two notches.

![Various Depths](/img/depths.png)

## Fillets
You may wish to get rid of the sharp corners. Since the stick itself is circular, it won't actually rest all the way in a sharp corner. Set **rounded** to True to and adjust **round_radius** to your liking. Default is 0.25.

![Filleted Edges](/img/rounds.png)

## Convexity
A convex notch will make it so that your stick wants to move into the notch, allowing you to quickly and consistently hit the notch angle. A straight notch will make it so that the intermediate angles between the notch and diagonal are equally easy to pinpoint. Credit to [Kadano's](http://kadano.net/SSBM/GCC/) detailed notching explanations, which helped inform the customization options. To enable convex notches, set **convex** to True (False for straight notches). Increasing the *convexity* will make the curve more pronounced, but too large a value will result in strange geometries. Values between 0.001 and 0.05 are recommended. **convexity_weighting** will move the peak of the notch curve. The value **must be between 0 and 1**. 0.5 will put the peak of the curve at the midpoint of the notch and the diagonal, a value less than 0.5 will put it closer to the diagonal, and greater will move it towards the notch.

![Various Curves](/img/curves.png)

## Flared Edges
The script by default cuts the notches in a straight line from the centre of the gate, but this can result in  notches that 'hook' inwards, which can lead to the stick not comfortably fitting in the notch, or getting stuck. You might wish to "flare" the notch so it's easier to roll in and out. Set **flared** to True to enable, and then specify the **flare_ang**. The angle of the flare is taken from the notch with respect to the horizontal/vertical, so I recommend a value near 45 degrees.

![Flared Notches](/img/flares.png)

## Sloped Notches
Many modders make notches with "sloped" edges, often to match the profile of the unmodified gate. This means that the angled surface will be in contact with the stick when it moves along the gate. Some people prefer a "straight" notch, which means only the edge. This is discussed in Goomy's *How to notch a GameCube controller* video [here](https://youtu.be/IPyPO3TByUU?t=313). 

![Cross section of sloped styles](/img/slopes.png)

If you wish to have a sloped edge, set **sloped** to True. The default **gate_angle** is 56 degrees, which closely matches the original gate angle. You may change this if you want another gate angle. If you want notches that go straight up and down, set **sloped** False. Do not change the gate angle to 90 degrees, the features might not be the same as if you just set **sloped** to False.

If you find that the notches are not the right depth when you enable sloped notches, you should change the value of **adjust_sloped_depth**, not the notch or diagonal depth. This way, you can adjust the sloped notches independently of the vertical ones. A higher value will make your notches more shallow. 


## OEM Gates
These files were designed with the OEM Shell files designed and shared by [GearHawkStudio](https://twitter.com/GearhawkStudio). The Gamecube gate is not perfectly symmetric, and so small adjustments can be made to each quadrant to make the notches more consistent. When using a gate with the OEM style, set the **oem_gate** variable to True. This will make the bottom notches extend slightly further, which results in a more consistent notch depth around the shell. I have noticed this is only really beneficial when a sloped notch is selected. You can tune the additional depth using the **oem_bottom_depth** parameter, though this shouldn't be necessary if your geometry is based on the same shell. 

Also note that this expects the gate to be aligned around the origin in a specific way. If you are having trouble getting your OEM gate aligned, and the notches don't appear to be consistent, please let me know so I can share how to set up your gate in 3D space for the best result.

# Adding your own Designs
I have included several gates based on the Gearhawk Shell, including removable options from the [Removable-Gate-GCC](https://github.com/sean44104/Removable-Gate-GCC) project by Olympia. If you have your own gates that you wish to notch, the script should work, so long as your gate is centred at (0,0). Keep in mind that the spacing and depth of the notches are for a GCC gate based on the Gearhawk files, so if your design is significantly different it may require many parameter adjustments. You may need to adjust the positioning of the cutting bodies as well. The GCC gate is tilted by design approximately 3 degrees, so if your gate has a different offset rotation, then this has to be changed or the notches will not be in the correct locations. Change the variable **offset** in the script to the appropriate angle. Additionally, the geometry cutting the notches are positioned at a specific height. This is important when making sloped notches in particular. If the vertical positioning of your model is different to what's expected, no notches will be made. Change the **h_offset** value until the notches appear.

CadQuery only can import step files (no stl). Place your file in the gates folder, and set the string **fname** to "your_file_name" (do not include the file extension).

# Running the Script
Download the repository, and open the folder in VS Code. Follow the [ocp-vscode](https://github.com/bernhard-42/vscode-ocp-cad-viewer) quickstart instructions to install all dependencies. Open the notch-customizer.py file you wish to use. You can select either the build123d or CadQuery version. Then click the run button in VS Code. You should see the notched gate appear in the viewer, and an export will be made. Alternatively can run the script from the command line so long as you have installed the appropriate modules. You will not have a GUI, but it should still export the file, which you can view in some other 3D modelling software. Make sure the shell you wish to import and your export folder exist in the appropriate locations in your file structure.

# Exporting 
You may export as either a step or stl file. By default, only step files are created, but you may uncomment the last line of the script, and it well also export an stl.

The files are exported to the gates/exports directory. You will need to create this file before you run the script the first time. The file will be named automatically with the relevant parameter values

the format is:
\
original file name,
\
_oem, if **oem_gate** was True
\
_notch_depth_x, where x is **notch_depth_double**
\
_adjustment_x_gate_angle_y, where x is **adjust_slope_depth** and y is **gate_angle** if **sloped** was True
\
_convex_x_y, where x is **convexity** and y is **convexity_weight** if **convex** was True, or
\
_straight if **convex** was False
\
_filleted_x, where x is **round_radius** if **rounded** was True
\
_flare_angle_x, where x is **flare_ang** if **flared** was True
\
_angles, followed by all the angles separated by underscores in the same order as the **angs** list
\
_cq or _b3d, depending on which modelling tool was used

The resulting name is quite long, but I wanted it to record all major parameters. That way someone could be given the settings used and replicate it exactly if they wished.

# To be tested!
Though I have printed some early prototypes, those were with an FDM printer, which has issues recreating the fine details. I do plan on using a 3d printing service to test different materials and fabrication technologies, but that hasn't happened yet. If you try it yourself, let me know how well it works!
