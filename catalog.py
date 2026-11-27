from modules import design, fluid, thermal, heat, structures, robotics, manufacturing
# Each parameter: label, minimum, maximum, default, step
LABS = {
"Machine design": {
"Compression spring": (design.spring,[("Force (N)",0,500,100,10),("Stiffness (N/mm)",10,100,25,5)]),
"Gear pair": (design.gears,[("Driver teeth",12,60,20,1),("Driven teeth",12,80,40,1),("Input rpm",0,3000,1000,50),("Torque (Nm)",0,200,20,1),("Phase (rad)",0.,6.28,0.,.1)]),
"Belt drive": (design.belt,[("Driver diameter (mm)",50,200,100,5),("Driven diameter (mm)",50,200,150,5),("Input rpm",0,3000,1000,50)])},
"Fluid mechanics":{
"Venturi meter":(fluid.venturi,[("Inlet diameter (mm)",100,200,120,5),("Throat diameter (mm)",20,95,60,5),("Flow (L/s)",1,30,5,1)]),
"Pipe pressure loss":(fluid.pipe,[("Diameter (mm)",20,200,50,5),("Length (m)",1,100,10,1),("Flow (L/s)",.1,20.,2.,.1),("Viscosity (Pa s)",.0005,.1,.001,.0005)])},
"Thermodynamics":{
"Otto cycle":(thermal.otto,[("Compression ratio",5,12,8,1),("Inlet temperature (K)",280,350,300,5),("Peak temperature (K)",1500,2500,2000,50)]),
"Carnot refrigeration":(thermal.refrigeration,[("Cold temperature (°C)",-30,10,-5,1),("Hot temperature (°C)",20,60,35,1)])},
"Heat transfer":{
"Plane wall conduction":(heat.wall,[("Conductivity (W/m K)",.1,400.,15.,.1),("Thickness (mm)",10,200,50,5),("Area (m²)",.1,10.,1.,.1),("Hot temperature (°C)",50,300,100,5),("Cold temperature (°C)",0,40,20,5)]),
"Cylindrical fin":(heat.fin,[("Conductivity (W/m K)",10,400,200,10),("Convection (W/m² K)",5,100,20,5),("Diameter (mm)",5,50,10,1),("Length (mm)",20,300,100,10),("Base temperature (°C)",50,200,100,5),("Ambient (°C)",0,40,25,5)])},
"Strength of materials":{
"Cantilever beam":(structures.beam,[("Load (N)",0,1000,100,10),("Length (m)",.2,2.,1.,.1),("Width (mm)",20,100,40,5),("Depth (mm)",20,100,50,5),("Young modulus (GPa)",50,210,200,5)]),
"Shaft torsion":(structures.torsion,[("Torque (Nm)",0,500,100,10),("Length (m)",.2,2.,1.,.1),("Diameter (mm)",20,100,40,5),("Shear modulus (GPa)",20,100,80,5)])},
"Robotics and dynamics":{
"Two-link robot":(robotics.arm,[("Link 1 (m)",.2,2.,1.,.1),("Link 2 (m)",.2,2.,1.,.1),("Joint 1 (°)",-180,180,45,5),("Joint 2 (°)",-180,180,45,5)]),
"Simple pendulum":(robotics.pendulum,[("Length (m)",.2,3.,1.,.1),("Initial angle (°)",0,15,10,1)])},
"Manufacturing":{
"Lathe turning":(manufacturing.lathe,[("Diameter (mm)",20,150,50,5),("Speed (rpm)",100,3000,1000,50),("Feed (mm/rev)",.05,.5,.2,.05),("Depth (mm)",.1,3.,1.,.1)]),
"Slider crank":(manufacturing.crank,[("Crank radius (mm)",10,50,30,5),("Rod length (mm)",60,200,120,5),("Crank angle (°)",0,360,45,5)])}}

from modules import advanced as A
LABS["Machine design"].update({
"Helical spring designer":(A.spring_design,[("Load (N)",10,1000,200,10),("Wire diameter (mm)",2,8,5,1),("Mean coil diameter (mm)",35,80,40,5),("Active coils",4,16,8,1),("Shear modulus (GPa)",60,85,79,1),("Allowable shear (MPa)",200,900,500,25)]),
"Ball bearing life":(A.bearing,[("Dynamic rating (kN)",20,100,40,5),("Equivalent load (kN)",1,15,5,1),("Speed (rpm)",100,3000,1000,100)])})
LABS["Fluid mechanics"].update({
"Centrifugal pump":(A.pump,[("Flow (L/s)",1,100,20,1),("Head (m)",1,100,25,1),("Efficiency (%)",20,90,70,5),("Speed (rpm)",500,3000,1450,50)]),
"Hydraulic press":(A.hydraulic,[("Input force (N)",10,1000,100,10),("Small piston (mm)",10,50,20,5),("Large piston (mm)",60,150,100,5),("Input travel (mm)",10,100,50,5)])})
LABS["Thermodynamics"]["Diesel cycle"]=(A.diesel,[("Compression ratio",12,24,18,1),("Cutoff ratio",1.2,3.,2.,.1),("Inlet temperature (K)",280,350,300,5)])
LABS["Heat transfer"].update({
"Counterflow heat exchanger":(A.exchanger,[("Hot flow (kg/s)",.1,3.,1.,.1),("Cold flow (kg/s)",.1,3.,1.5,.1),("Hot inlet (°C)",50,100,80,5),("Cold inlet (°C)",5,40,20,5),("UA (W/K)",100,5000,1500,100)]),
"Transient slab conduction":(A.heat_transient,[("Diffusivity (mm²/s)",1,20,10,1),("Thickness (mm)",20,100,50,5),("Initial temperature (°C)",10,40,20,5),("Surface temperature (°C)",50,200,100,5),("Time (s)",1,60,10,1)])})
LABS["Strength of materials"].update({
"Pressure vessel":(A.pressure,[("Pressure (MPa)",.1,5.,1.,.1),("Diameter (mm)",500,1000,600,50),("Wall thickness (mm)",5,20,10,1),("Allowable stress (MPa)",80,250,150,10)]),
"Goodman fatigue":(A.fatigue,[("Alternating stress (MPa)",10,400,100,10),("Mean stress (MPa)",0,400,50,10),("Endurance limit (MPa)",100,400,200,10),("Ultimate strength (MPa)",400,1000,600,50)]),
"Euler buckling":(A.buckling,[("Length (m)",.5,3.,1.5,.1),("Diameter (mm)",10,50,20,5),("Young modulus (GPa)",50,210,200,5),("Effective length factor",.5,2.,1.,.1)]),
"Tensile test":(A.tensile,[("Young modulus (GPa)",50,210,200,5),("Area (mm²)",50,500,100,10),("Gauge length (mm)",50,200,100,10),("Force (N)",0,10000,1000,100)])})
LABS["Robotics and dynamics"]["Damped vibration"]=(A.vibration,[("Mass (kg)",1,10,2,1),("Stiffness (N/m)",100,1000,200,50),("Damping (Ns/m)",0,15,5,1),("Initial displacement (m)",.01,.5,.1,.01)])
LABS["Manufacturing"]["Welding heat field"]=(A.welding,[("Power (W)",500,3000,1500,100),("Efficiency (%)",30,90,70,5),("Conductivity (W/m K)",20,80,40,5),("Travel speed (mm/s)",1,15,5,1)])
