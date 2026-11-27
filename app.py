import numpy as np
import plotly.graph_objects as go
def scene():
    f=go.Figure()
    f.update_layout(template="plotly_dark",height=490,margin=dict(l=0,r=0,t=10,b=0),scene=dict(aspectmode="data",xaxis_title="X",yaxis_title="Y",zaxis_title="Z"),uirevision="camera")
    return f
def tube(f,x,y,z,r=.12,color="#42c5e8"):
    x,y,z=map(np.asarray,(x,y,z))
    p=np.column_stack([x,y,z]); t=np.gradient(p,axis=0); t/=np.maximum(np.linalg.norm(t,axis=1)[:,None],1e-12)
    ref=np.tile([0.,0.,1.],(len(p),1)); ref[np.abs(t[:,2])>.9]=[1,0,0]
    n=np.cross(t,ref); n/=np.linalg.norm(n,axis=1)[:,None]; b=np.cross(t,n)
    a=np.linspace(0,2*np.pi,14)
    q=p[:,None,:]+r*(n[:,None,:]*np.cos(a)[None,:,None]+b[:,None,:]*np.sin(a)[None,:,None])
    f.add_trace(go.Surface(x=q[:,:,0],y=q[:,:,1],z=q[:,:,2],surfacecolor=np.zeros(q.shape[:2]),colorscale=[[0,color],[1,color]],showscale=False,hoverinfo="skip"))
def disk(f,x,y,z,r,color="#64748b",teeth=0,phase=0):
    a=np.linspace(0,2*np.pi, max(100,teeth*12)); rr=r*(1+.09*np.cos(teeth*(a-phase))) if teeth else np.full_like(a,r)
    f.add_trace(go.Mesh3d(x=np.r_[x,x+rr*np.cos(a)],y=np.r_[y,y+rr*np.sin(a)],z=np.full(len(a)+1,z),i=np.zeros(len(a)-1,dtype=int),j=np.arange(1,len(a)),k=np.arange(2,len(a)+1),color=color))
def curve(x,y,xlabel,ylabel):
    f=go.Figure(go.Scatter(x=x,y=y,mode="lines"));f.update_layout(template="plotly_dark",height=280,xaxis_title=xlabel,yaxis_title=ylabel,margin=dict(l=10,r=10,t=10,b=10));return f
def result(metrics,fig,chart,formula,note):
    return dict(metrics=metrics,fig=fig,chart=chart,formula=formula,note=note)


def design_spring(F,k):
    d=F/k; a=np.linspace(0,16*np.pi,500); f=scene()
    tube(f,np.cos(a),np.sin(a),np.linspace(0,max(.5,6-d/15),len(a)),.13)
    return result({"Deflection (mm)":d,"Energy (J)":F*d/2000},f,curve([0,F],[0,d],"Force (N)","Deflection (mm)"),r"\delta=F/k,\quad U=F^2/(2k)","Linear spring; geometry is illustrative, not a coil-bind calculation.")
def design_gears(z1,z2,rpm,torque,phase):
    r1=z1/20;r2=z2/20; f=scene()
    disk(f,0,0,0,r1,teeth=int(z1),phase=phase);disk(f,r1+r2,0,0,r2,"#e9a34c",int(z2),-phase*z1/z2)
    return result({"Ratio":z2/z1,"Output rpm":rpm*z1/z2,"Ideal output torque (Nm)":torque*z2/z1},f,curve([0,rpm],[0,rpm*z1/z2],"Input rpm","Output rpm"),r"i=Z_2/Z_1,\quad n_2=n_1/i","Ideal external gears; stylized teeth, no contact stress.")
def design_belt(d1,d2,rpm):
    r1=d1/100;r2=d2/100;c=6;f=scene();disk(f,0,0,0,r1);disk(f,c,0,0,r2)
    # external common tangents
    a=np.arccos((r1-r2)/c); angles=np.linspace(a,2*np.pi-a,100); angles2=np.linspace(-a,a,100)
    x=np.r_[r1*np.cos(angles),c+r2*np.cos(angles2),r1*np.cos(a)]
    y=np.r_[r1*np.sin(angles),r2*np.sin(angles2),r1*np.sin(a)]
    tube(f,x,y,np.zeros_like(x),.06,"#e9a34c")
    return result({"Output rpm":rpm*d1/d2,"Belt speed (m/s)":np.pi*d1/1000*rpm/60},f,curve([0,rpm],[0,rpm*d1/d2],"Input rpm","Output rpm"),r"n_2=n_1D_1/D_2","No slip; pulley geometry scaled for display.")


def fluid_venturi(D,d,Q):
    Q=Q/1000; A=np.pi*(D/1000)**2/4; B=np.pi*(d/1000)**2/4; v=Q/A; w=Q/B
    x=np.linspace(0,8,150); r=(D-(D-d)*np.exp(-((x-4)/1.3)**2))/100
    a=np.linspace(0,2*np.pi,40); X,T=np.meshgrid(x,a); R=np.tile(r,(len(a),1)); f=scene()
    f.add_trace(go.Surface(x=X,y=R*np.cos(T),z=R*np.sin(T),opacity=.55,showscale=False))
    return result({"Inlet velocity (m/s)":v,"Throat velocity (m/s)":w,"Pressure drop (Pa)":500*(w*w-v*v)},f,curve(x,Q/(np.pi*(r/20)**2),"Position (scaled)","Velocity (m/s)"),r"Q=Av,\quad \Delta p=\rho(v_2^2-v_1^2)/2","Ideal horizontal water flow, density 1000 kg/m³; no losses.")
def fluid_pipe(D,L,Q,mu):
    D=D/1000;Q=Q/1000;v=4*Q/(np.pi*D**2);Re=1000*v*D/mu; friction=64/Re if Re<2300 else .3164/Re**.25; dp=friction*L/D*500*v*v
    f=scene();x=np.linspace(0,8,100);a=np.linspace(0,2*np.pi,40);X,T=np.meshgrid(x,a);f.add_trace(go.Surface(x=X,y=np.cos(T),z=np.sin(T),opacity=.5,showscale=False))
    return result({"Velocity (m/s)":v,"Reynolds number":Re,"Pressure loss (Pa)":dp},f,curve([0,L],[dp,0],"Distance (m)","Gauge pressure relative to outlet (Pa)"),r"\Delta p=f(L/D)\rho v^2/2","Smooth pipe; Blasius approximation above Re 2300, transitional estimates uncertain.")


def thermal_otto(r,T1,T3):
    g=1.4; T2=T1*r**(g-1); T4=T3/r**(g-1);v=np.linspace(1/r,1,100);p1=101325
    p2=p1*r**g;p3=p2*T3/T2;p4=p3/r**g
    f=scene();a=np.linspace(0,2*np.pi,40);z=np.linspace(0,5,20);A,Z=np.meshgrid(a,z);f.add_trace(go.Surface(x=np.cos(A),y=np.sin(A),z=Z,opacity=.35,showscale=False));disk(f,0,0,5/r,.95)
    V=np.r_[v[::-1],1/r,v,1];P=np.r_[p1/v[::-1]**g,p3,p3*((1/r)/v)**g,p1]
    return result({"Ideal efficiency (%)":100*(1-r**(1-g)),"Compression temperature (K)":T2,"Exhaust temperature (K)":T4},f,curve(V,P/1000,"Relative volume","Pressure (kPa)"),r"\eta=1-r^{1-\gamma}","Air-standard Otto cycle, constant specific heats; piston schematic.")
def thermal_refrigeration(Te,Tc):
    a=Te+273.15;b=Tc+273.15;f=scene()
    x=np.array([0,4,4,0,0]);y=np.array([0,0,3,3,0]);tube(f,x,y,np.zeros(5),.12)
    return result({"Carnot COP":a/(b-a)},f,curve(np.linspace(Tc,Tc+30,100),a/(np.linspace(Tc,Tc+30,100)-Te),"Condenser temperature (°C)","Ideal COP"),r"COP_R=T_L/(T_H-T_L)","Reversible upper bound, not actual refrigerant cycle; schematic loop.")


def heat_wall(k,L,A,hot,cold):
    L=L/1000;q=k*A*(hot-cold)/L;x=np.linspace(0,L,80);T=hot+(cold-hot)*x/L;X,Y=np.meshgrid(x,np.linspace(0,L,20));f=scene()
    f.add_trace(go.Surface(x=X,y=Y,z=np.zeros_like(X),surfacecolor=np.tile(T,(20,1)),colorscale="Turbo",colorbar=dict(title="°C")))
    return result({"Heat rate (W)":q,"Heat flux (W/m²)":q/A},f,curve(x,T,"Thickness (m)","Temperature (°C)"),r"\dot Q=kA(T_h-T_c)/L","Steady one-dimensional conduction, constant conductivity.")
def heat_fin(k,h,D,L,base,ambient):
    D=D/1000;L=L/1000;A=np.pi*D**2/4;P=np.pi*D;m=np.sqrt(h*P/(k*A));x=np.linspace(0,L,100);T=ambient+(base-ambient)*np.cosh(m*(L-x))/np.cosh(m*L);q=np.sqrt(h*P*k*A)*(base-ambient)*np.tanh(m*L)
    f=scene();X,Aa=np.meshgrid(x,np.linspace(0,2*np.pi,30));f.add_trace(go.Surface(x=X,y=D/2*np.cos(Aa),z=D/2*np.sin(Aa),surfacecolor=np.tile(T,(30,1)),colorscale="Turbo"))
    return result({"Heat rate (W)":q,"Tip temperature (°C)":T[-1]},f,curve(x,T,"Length (m)","Temperature (°C)"),r"m=\sqrt{hP/(kA)},\quad q=\sqrt{hPkA}\theta_b\tanh(mL)","Straight cylindrical fin with insulated tip.")


def structures_beam(F,L,b,h,E):
    b/=1000;h/=1000;E*=1e9;I=b*h**3/12;x=np.linspace(0,L,100);y=F*x*x*(3*L-x)/(6*E*I);f=scene();tube(f,x,np.zeros_like(x),-y*20,max(.005,b/2))
    return result({"Tip deflection (mm)":y[-1]*1000,"Root stress (MPa)":F*L*h/(2*I)/1e6},f,curve(x,y*1000,"Position (m)","Deflection (mm)"),r"\delta=FL^3/(3EI),\quad \sigma=Mc/I","Cantilever end load, small deflection; display deformation magnified 20×.")
def structures_torsion(T,L,D,G):
    D/=1000;G*=1e9;J=np.pi*D**4/32;theta=T*L/(G*J);x=np.linspace(0,L,100);f=scene();tube(f,x,np.zeros_like(x),np.zeros_like(x),D/2)
    a=theta*x/L;tube(f,x,D/2*np.cos(a),D/2*np.sin(a),D/35,"#f5a34b")
    return result({"Twist (degrees)":np.degrees(theta),"Shear stress (MPa)":T*D/(2*J)/1e6},f,curve(x,np.degrees(a),"Length (m)","Twist (degrees)"),r"\theta=TL/(GJ),\quad \tau=Tr/J","Solid circular shaft, linear elasticity.")


def robotics_arm(L1,L2,a,b):
    a,b=np.radians([a,b]);x1=L1*np.cos(a);y1=L1*np.sin(a);x2=x1+L2*np.cos(a+b);y2=y1+L2*np.sin(a+b);f=scene()
    for p,q in [([0,0,0],[x1,y1,0]),([x1,y1,0],[x2,y2,0])]:
        v=np.linspace(p,q,30).T;tube(f,*v,.07)
    f.add_trace(go.Scatter3d(x=[0,x1,x2],y=[0,y1,y2],z=[0,0,0],mode="markers",marker=dict(size=7,color="#f5a34b")))
    t=np.linspace(0,2*np.pi,200)
    return result({"End X (m)":x2,"End Y (m)":y2,"Reach (m)":np.hypot(x2,y2)},f,curve((L1+L2)*np.cos(t),(L1+L2)*np.sin(t),"X (m)","Outer workspace Y (m)"),r"x=L_1\cos a+L_2\cos(a+b)","Planar two-link arm; unrestricted joints, no collision model.")
def robotics_pendulum(L,angle):
    t=np.linspace(0,10,300);a=np.radians(angle);w=np.sqrt(9.81/L);th=a*np.cos(w*t);f=scene();tube(f,np.linspace(0,L*np.sin(a),30),np.zeros(30),np.linspace(0,-L*np.cos(a),30),.035);f.add_trace(go.Scatter3d(x=[L*np.sin(a)],y=[0],z=[-L*np.cos(a)],mode="markers",marker=dict(size=15)))
    frames=[]
    for j,ang in enumerate(th[::5]):
        xx=L*np.sin(ang);zz=-L*np.cos(ang)
        frames.append(go.Frame(name=str(j),data=[go.Scatter3d(x=[0,xx],y=[0,0],z=[0,zz],mode="lines",line=dict(width=8)),go.Scatter3d(x=[xx],y=[0],z=[zz],mode="markers",marker=dict(size=15))]))
    f.data=[];f.add_traces(frames[0].data);f.frames=frames
    f.update_layout(scene=dict(xaxis=dict(range=[-L,L]),yaxis=dict(range=[-L,L]),zaxis=dict(range=[-L*1.1,.1])),updatemenus=[dict(type="buttons",buttons=[dict(label="Play",method="animate",args=[None,{"frame":{"duration":167,"redraw":True},"fromcurrent":True}]),dict(label="Pause",method="animate",args=[[None],{"mode":"immediate","frame":{"duration":0}}])])])
    return result({"Period (s)":2*np.pi/w},f,curve(t,np.degrees(th),"Time (s)","Angle (degrees)"),r"T=2\pi\sqrt{L/g}","Small-angle, undamped pendulum.")


def manufacturing_lathe(D,rpm,feed,depth):
    v=np.pi*D*rpm/1000;f=scene();x=np.linspace(0,5,100);a=np.linspace(0,2*np.pi,40);X,A=np.meshgrid(x,a);r=D/100;f.add_trace(go.Surface(x=X,y=r*np.cos(A),z=r*np.sin(A),showscale=False));tube(f,[2,2,2],[r,r+.4,r+.8],[0,.2,.4],.08,"#e9a34c")
    return result({"Cutting speed (m/min)":v,"Feed rate (mm/min)":feed*rpm,"Approx. MRR (mm³/min)":1000*v*feed*depth},f,curve([0,rpm],[0,v],"rpm","Cutting speed (m/min)"),r"V=\pi DN/1000,\quad MRR\approx1000Vfd","Turning approximation for shallow cuts.")
def manufacturing_crank(r,l,angle):
    a=np.radians(angle);x=r*np.cos(a)+np.sqrt(l*l-r*r*np.sin(a)**2);f=scene();p=np.array([r*np.cos(a),r*np.sin(a),0]);q=np.array([x,0,0])
    for u,v in [(np.zeros(3),p),(p,q)]:tube(f,*np.linspace(u,v,30).T,max(1,r/12))
    t=np.linspace(0,2*np.pi,360);s=r*np.cos(t)+np.sqrt(l*l-r*r*np.sin(t)**2)
    return result({"Slider position (mm)":x,"Stroke (mm)":2*r},f,curve(np.degrees(t),s,"Crank angle (°)","Slider position (mm)"),r"x=r\cos\theta+\sqrt{l^2-r^2\sin^2\theta}","Rigid slider-crank, kinematics only.")



def advanced_spring_design(F,d,D,n,G,S):
    C=D/d; K=(4*C-1)/(4*C-4)+.615/C
    k=G*1000*d**4/(8*D**3*n); delta=F/k; tau=K*8*F*D/(np.pi*d**3)
    solid=(n+2)*d; free=solid+1.15*delta; a=np.linspace(0,2*np.pi*(n+2),700)
    f=scene();tube(f,D/2*np.cos(a),D/2*np.sin(a),np.linspace(d/2,free-delta-d/2,len(a)),d/2)
    return result({"Spring rate (N/mm)":k,"Deflection (mm)":delta,"Wahl stress (MPa)":tau,"Stress safety ratio":S/max(tau,1e-12),"Spring index":C,"Solid length (mm)":solid,"Suggested free length (mm)":free},f,curve([0,delta],[0,F],"Deflection (mm)","Load (N)"),r"k=Gd^4/(8D^3n),\quad \tau=K_w8FD/(\pi d^3)","Round-wire compression spring, squared/ground ends assumed; free length includes 15% deflection allowance. Check fatigue, buckling, material and coil clearance separately.")
def advanced_pressure(p,D,t,S):
    hoop=p*D/(2*t); axial=hoop/2; f=scene();a,z=np.meshgrid(np.linspace(0,2*np.pi,60),np.linspace(0,D*2,30))
    f.add_trace(go.Surface(x=D/2*np.cos(a),y=D/2*np.sin(a),z=z,surfacecolor=np.full_like(z,hoop),colorscale="Turbo",opacity=.8))
    return result({"Hoop stress (MPa)":hoop,"Axial stress (MPa)":axial,"Allowable/stress":S/hoop},f,curve([0,p],[0,hoop],"Pressure (MPa)","Hoop stress (MPa)"),r"\sigma_h=pD/(2t),\quad \sigma_l=pD/(4t)","Thin closed cylinder; D/t should exceed 20. Not a pressure vessel code design.")
def advanced_fatigue(sa,sm,Se,Sut):
    n=1/(sa/Se+sm/Sut);f=scene();x=np.linspace(0,Sut,60);y=Se*(1-x/Sut)
    f.add_trace(go.Scatter3d(x=x,y=y,z=np.zeros_like(x),mode="lines",name="Goodman limit"));f.add_trace(go.Scatter3d(x=[sm],y=[sa],z=[0],mode="markers",marker=dict(size=8)))
    return result({"Goodman safety factor":n},f,curve(x,y,"Mean stress (MPa)","Alternating stress (MPa)"),r"1/n=\sigma_a/S_e+\sigma_m/S_{ut}","Modified Goodman criterion; tensile mean stress, corrected endurance limit supplied by user.")
def advanced_bearing(C,P,rpm):
    life=(C/P)**3;f=scene();a=np.linspace(0,2*np.pi,150)
    for r in [2,3]:tube(f,r*np.cos(a),r*np.sin(a),np.zeros_like(a),.13)
    for t in np.linspace(0,2*np.pi,10,endpoint=False):f.add_trace(go.Scatter3d(x=[2.5*np.cos(t)],y=[2.5*np.sin(t)],z=[0],mode="markers",marker=dict(size=12)))
    return result({"L10 (million rev)":life,"L10 (hours)":life*1e6/(60*rpm)},f,curve(np.linspace(P,C,100),(C/np.linspace(P,C,100))**3,"Load (kN)","L10 (million rev)"),r"L_{10}=(C/P)^3","Ball bearing basic rating life, constant equivalent load; 90% reliability.")
def advanced_pump(Q,H,eta,rpm):
    q=Q/1000;power=1000*9.81*q*H;f=scene();disk(f,0,0,0,2)
    for a in np.linspace(0,2*np.pi,7,endpoint=False):
        t=np.linspace(.3,1.9,40);tube(f,t*np.cos(a+t*.5),t*np.sin(a+t*.5),np.ones_like(t)*.2,.1)
    return result({"Hydraulic power (W)":power,"Shaft power (W)":power/(eta/100),"Shaft torque (Nm)":power/(eta/100)/(rpm*2*np.pi/60)},f,curve([0,Q],[0,power],"Flow (L/s)","Hydraulic power (W)"),r"P_h=\rho gQH,\quad P_s=P_h/\eta","Specified operating point, not a predicted pump characteristic or CFD.")
def advanced_hydraulic(F,d1,d2,s):
    ratio=(d2/d1)**2;f=scene()
    for x,d,h in [(0,d1,s),(4,d2,s/ratio)]:
        a,z=np.meshgrid(np.linspace(0,2*np.pi,40),np.linspace(0,3,20));f.add_trace(go.Surface(x=x+d/100*np.cos(a),y=d/100*np.sin(a),z=z,opacity=.4,showscale=False));disk(f,x,0,1+h/100,d/100)
    return result({"Output force (N)":F*ratio,"Output travel (mm)":s/ratio,"Pressure (MPa)":F/(np.pi*d1*d1/4)},f,curve([0,F],[0,F*ratio],"Input force (N)","Output force (N)"),r"F_2/F_1=A_2/A_1","Ideal incompressible hydraulic press; no losses.")
def advanced_exchanger(mh,mc,Th,Tc,UA):
    Ch=mh*4180;Cc=mc*4180;mn=min(Ch,Cc);cr=mn/max(Ch,Cc);ntu=UA/mn
    e=ntu/(1+ntu) if abs(cr-1)<1e-9 else (1-np.exp(-ntu*(1-cr)))/(1-cr*np.exp(-ntu*(1-cr)))
    q=e*mn*(Th-Tc);ho=Th-q/Ch;co=Tc+q/Cc;f=scene();x=np.linspace(0,5,80)
    for y,col in [(0,"#f97316"),(1,"#38bdf8")]:tube(f,x,np.full_like(x,y),np.zeros_like(x),.22,col)
    return result({"Heat duty (W)":q,"Effectiveness":e,"Hot outlet (°C)":ho,"Cold outlet (°C)":co},f,curve([0,1],[Th,ho],"Hot flow direction","Hot temperature (°C)"),r"Q=\epsilon C_{\min}(T_{h,i}-T_{c,i})","Counterflow water-water exchanger, constant cp and UA.")
def advanced_buckling(L,D,E,K):
    I=np.pi*(D/1000)**4/64;P=np.pi**2*E*1e9*I/(K*L)**2;f=scene();x=np.linspace(0,L,100);tube(f,x,.03*L*np.sin(np.pi*x/L),np.zeros_like(x),D/2000)
    return result({"Euler critical load (N)":P,"Slenderness KL/r":K*L/(D/4000)},f,curve(x,.03*L*np.sin(np.pi*x/L),"Length (m)","Illustrative mode (m)"),r"P_{cr}=\pi^2EI/(KL)^2","Elastic slender column; mode is illustrative, not actual post-buckling displacement.")
def advanced_tensile(E,A,L,F):
    stress=F/A;strain=stress/(E*1000);f=scene();x=np.linspace(0,L*(1+strain),100);tube(f,x,np.zeros_like(x),np.zeros_like(x),np.sqrt(A/np.pi))
    return result({"Stress (MPa)":stress,"Strain":strain,"Extension (mm)":L*strain},f,curve([0,strain],[0,stress],"Strain","Stress (MPa)"),r"\sigma=F/A,\quad \epsilon=\sigma/E","Linear elastic uniaxial model; yield and necking not modeled.")
def advanced_vibration(m,k,c,x0):
    w=np.sqrt(k/m);z=c/(2*np.sqrt(k*m));t=np.linspace(0,10,500);wd=w*np.sqrt(1-z*z);x=x0*np.exp(-z*w*t)*(np.cos(wd*t)+z*w/wd*np.sin(wd*t));f=scene();a=np.linspace(0,12*np.pi,400);tube(f,np.cos(a),np.sin(a),np.linspace(0,4+x0,len(a)),.1);disk(f,0,0,4+x0,1.3)
    return result({"Natural frequency (Hz)":w/(2*np.pi),"Damping ratio":z},f,curve(t,x,"Time (s)","Displacement (m)"),r"\omega_n=\sqrt{k/m},\quad \zeta=c/(2\sqrt{km})","Underdamped free vibration, zero initial velocity.")
def advanced_diesel(r,rc,T):
    g=1.4;eff=1-(rc**g-1)/(g*(rc-1)*r**(g-1));f=scene();a,z=np.meshgrid(np.linspace(0,2*np.pi,40),np.linspace(0,4,20));f.add_trace(go.Surface(x=np.cos(a),y=np.sin(a),z=z,opacity=.4,showscale=False));disk(f,0,0,4/r,1)
    rr=np.linspace(rc+.1,25,100);ee=1-(rc**g-1)/(g*(rc-1)*rr**(g-1))
    return result({"Ideal efficiency (%)":100*eff,"Compression temperature (K)":T*r**(g-1)},f,curve(rr,100*ee,"Compression ratio","Efficiency (%)"),r"\eta=1-\frac{r_c^\gamma-1}{\gamma(r_c-1)r^{\gamma-1}}","Air-standard Diesel cycle.")
def advanced_welding(P,eta,k,v):
    # Regularized Rosenthal moving point source, illustrative surface field
    x=np.linspace(-.04,.04,90);y=np.linspace(-.03,.03,70);X,Y=np.meshgrid(x,y);R=np.sqrt(X*X+Y*Y+.002**2);alpha=1.2e-5;T=25+eta/100*P/(2*np.pi*k*R)*np.exp(-v/1000*(X+R)/(2*alpha));f=scene();f.add_trace(go.Surface(x=X*1000,y=Y*1000,z=np.zeros_like(X),surfacecolor=T,colorscale="Turbo",colorbar=dict(title="°C")))
    return result({"Peak grid temperature (°C)":T.max(),"Net power (W)":P*eta/100},f,curve(x*1000,T[len(y)//2],"Distance (mm)","Temperature (°C)"),r"T-T_0=\frac{\eta P}{2\pi kR}e^{-v(x+R)/(2\alpha)}","Regularized Rosenthal approximation; constant properties, no phase change; not validated weld pool prediction.")
def advanced_heat_transient(alpha,L,T0,Ts,time):
    L=L/1000;x=np.linspace(0,L,81);dx=x[1]-x[0];a=alpha*1e-6;steps=max(1,int(np.ceil(time*a/(.45*dx*dx))));dt=time/steps;T=np.full(81,float(T0));T[[0,-1]]=Ts;lam=a*dt/dx**2
    for _ in range(steps):T[1:-1]+=lam*(T[:-2]-2*T[1:-1]+T[2:])
    X,Y=np.meshgrid(x*1000,np.linspace(0,20,20));f=scene();f.add_trace(go.Surface(x=X,y=Y,z=np.zeros_like(X),surfacecolor=np.tile(T,(20,1)),colorscale="Turbo"))
    return result({"Center temperature (°C)":T[40],"Time steps":steps,"Fourier step number":lam},f,curve(x*1000,T,"Position (mm)","Temperature (°C)"),r"T_i^{n+1}=T_i^n+Fo(T_{i-1}^n-2T_i^n+T_{i+1}^n)","Explicit finite difference 1D slab, both surfaces fixed, constant diffusivity.")


# Each parameter: label, minimum, maximum, default, step
LABS = {
"Machine design": {
"Compression spring": (design_spring,[("Force (N)",0,500,100,10),("Stiffness (N/mm)",10,100,25,5)]),
"Gear pair": (design_gears,[("Driver teeth",12,60,20,1),("Driven teeth",12,80,40,1),("Input rpm",0,3000,1000,50),("Torque (Nm)",0,200,20,1),("Phase (rad)",0.,6.28,0.,.1)]),
"Belt drive": (design_belt,[("Driver diameter (mm)",50,200,100,5),("Driven diameter (mm)",50,200,150,5),("Input rpm",0,3000,1000,50)])},
"Fluid mechanics":{
"Venturi meter":(fluid_venturi,[("Inlet diameter (mm)",100,200,120,5),("Throat diameter (mm)",20,95,60,5),("Flow (L/s)",1,30,5,1)]),
"Pipe pressure loss":(fluid_pipe,[("Diameter (mm)",20,200,50,5),("Length (m)",1,100,10,1),("Flow (L/s)",.1,20.,2.,.1),("Viscosity (Pa s)",.0005,.1,.001,.0005)])},
"Thermodynamics":{
"Otto cycle":(thermal_otto,[("Compression ratio",5,12,8,1),("Inlet temperature (K)",280,350,300,5),("Peak temperature (K)",1500,2500,2000,50)]),
"Carnot refrigeration":(thermal_refrigeration,[("Cold temperature (°C)",-30,10,-5,1),("Hot temperature (°C)",20,60,35,1)])},
"Heat transfer":{
"Plane wall conduction":(heat_wall,[("Conductivity (W/m K)",.1,400.,15.,.1),("Thickness (mm)",10,200,50,5),("Area (m²)",.1,10.,1.,.1),("Hot temperature (°C)",50,300,100,5),("Cold temperature (°C)",0,40,20,5)]),
"Cylindrical fin":(heat_fin,[("Conductivity (W/m K)",10,400,200,10),("Convection (W/m² K)",5,100,20,5),("Diameter (mm)",5,50,10,1),("Length (mm)",20,300,100,10),("Base temperature (°C)",50,200,100,5),("Ambient (°C)",0,40,25,5)])},
"Strength of materials":{
"Cantilever beam":(structures_beam,[("Load (N)",0,1000,100,10),("Length (m)",.2,2.,1.,.1),("Width (mm)",20,100,40,5),("Depth (mm)",20,100,50,5),("Young modulus (GPa)",50,210,200,5)]),
"Shaft torsion":(structures_torsion,[("Torque (Nm)",0,500,100,10),("Length (m)",.2,2.,1.,.1),("Diameter (mm)",20,100,40,5),("Shear modulus (GPa)",20,100,80,5)])},
"Robotics and dynamics":{
"Two-link robot":(robotics_arm,[("Link 1 (m)",.2,2.,1.,.1),("Link 2 (m)",.2,2.,1.,.1),("Joint 1 (°)",-180,180,45,5),("Joint 2 (°)",-180,180,45,5)]),
"Simple pendulum":(robotics_pendulum,[("Length (m)",.2,3.,1.,.1),("Initial angle (°)",0,15,10,1)])},
"Manufacturing":{
"Lathe turning":(manufacturing_lathe,[("Diameter (mm)",20,150,50,5),("Speed (rpm)",100,3000,1000,50),("Feed (mm/rev)",.05,.5,.2,.05),("Depth (mm)",.1,3.,1.,.1)]),
"Slider crank":(manufacturing_crank,[("Crank radius (mm)",10,50,30,5),("Rod length (mm)",60,200,120,5),("Crank angle (°)",0,360,45,5)])}}

LABS["Machine design"].update({
"Helical spring designer":(advanced_spring_design,[("Load (N)",10,1000,200,10),("Wire diameter (mm)",2,8,5,1),("Mean coil diameter (mm)",35,80,40,5),("Active coils",4,16,8,1),("Shear modulus (GPa)",60,85,79,1),("Allowable shear (MPa)",200,900,500,25)]),
"Ball bearing life":(advanced_bearing,[("Dynamic rating (kN)",20,100,40,5),("Equivalent load (kN)",1,15,5,1),("Speed (rpm)",100,3000,1000,100)])})
LABS["Fluid mechanics"].update({
"Centrifugal pump":(advanced_pump,[("Flow (L/s)",1,100,20,1),("Head (m)",1,100,25,1),("Efficiency (%)",20,90,70,5),("Speed (rpm)",500,3000,1450,50)]),
"Hydraulic press":(advanced_hydraulic,[("Input force (N)",10,1000,100,10),("Small piston (mm)",10,50,20,5),("Large piston (mm)",60,150,100,5),("Input travel (mm)",10,100,50,5)])})
LABS["Thermodynamics"]["Diesel cycle"]=(advanced_diesel,[("Compression ratio",12,24,18,1),("Cutoff ratio",1.2,3.,2.,.1),("Inlet temperature (K)",280,350,300,5)])
LABS["Heat transfer"].update({
"Counterflow heat exchanger":(advanced_exchanger,[("Hot flow (kg/s)",.1,3.,1.,.1),("Cold flow (kg/s)",.1,3.,1.5,.1),("Hot inlet (°C)",50,100,80,5),("Cold inlet (°C)",5,40,20,5),("UA (W/K)",100,5000,1500,100)]),
"Transient slab conduction":(advanced_heat_transient,[("Diffusivity (mm²/s)",1,20,10,1),("Thickness (mm)",20,100,50,5),("Initial temperature (°C)",10,40,20,5),("Surface temperature (°C)",50,200,100,5),("Time (s)",1,60,10,1)])})
LABS["Strength of materials"].update({
"Pressure vessel":(advanced_pressure,[("Pressure (MPa)",.1,5.,1.,.1),("Diameter (mm)",500,1000,600,50),("Wall thickness (mm)",5,20,10,1),("Allowable stress (MPa)",80,250,150,10)]),
"Goodman fatigue":(advanced_fatigue,[("Alternating stress (MPa)",10,400,100,10),("Mean stress (MPa)",0,400,50,10),("Endurance limit (MPa)",100,400,200,10),("Ultimate strength (MPa)",400,1000,600,50)]),
"Euler buckling":(advanced_buckling,[("Length (m)",.5,3.,1.5,.1),("Diameter (mm)",10,50,20,5),("Young modulus (GPa)",50,210,200,5),("Effective length factor",.5,2.,1.,.1)]),
"Tensile test":(advanced_tensile,[("Young modulus (GPa)",50,210,200,5),("Area (mm²)",50,500,100,10),("Gauge length (mm)",50,200,100,10),("Force (N)",0,10000,1000,100)])})
LABS["Robotics and dynamics"]["Damped vibration"]=(advanced_vibration,[("Mass (kg)",1,10,2,1),("Stiffness (N/m)",100,1000,200,50),("Damping (Ns/m)",0,15,5,1),("Initial displacement (m)",.01,.5,.1,.01)])
LABS["Manufacturing"]["Welding heat field"]=(advanced_welding,[("Power (W)",500,3000,1500,100),("Efficiency (%)",30,90,70,5),("Conductivity (W/m K)",20,80,40,5),("Travel speed (mm/s)",1,15,5,1)])


def answer(key,model,messages,context):
    from openai import OpenAI
    client=OpenAI(base_url="https://integrate.api.nvidia.com/v1",api_key=key,timeout=60)
    system="""You are MECHVERSE, a mechanical engineering tutor. Explain step by step with units, assumptions, equations and checks. Use the supplied experiment context, distinguish schematic visualization from validated physics, and do not invent measurements. Teach in the student's requested language. Never claim a design is certified safe."""
    response=client.chat.completions.create(model=model,messages=[{"role":"system","content":system+"\nCurrent experiment: "+context}]+messages[-12:],temperature=.3,max_tokens=1800)
    return response.choices[0].message.content or "No text returned."


def main():
    import json, os
    import streamlit as st
    st.set_page_config(page_title="MECHVERSE AI",page_icon="⚙️",layout="wide")
    st.title("MECHVERSE AI")
    st.caption("Interactive mechanical engineering laboratory · 7 departments · 28 experiments")
    with st.sidebar:
        st.header("Laboratory")
        department=st.selectbox("Department",list(LABS))
        name=st.selectbox("Experiment",list(LABS[department]))
        solver,params=LABS[department][name]
        st.subheader("Experiment controls")
        values=[st.slider(label,lo,hi,default,step,key=name+label) for label,lo,hi,default,step in params]
        def reset():
            for label,lo,hi,default,step in params: st.session_state[name+label]=default
        st.button("Reset controls",on_click=reset)
    r=solver(*values)
    context=json.dumps({"experiment":name,"inputs":dict(zip([p[0] for p in params],values)),"results":{k:float(v) for k,v in r["metrics"].items()},"assumptions":r["note"]})
    lab,tutor,guide=st.tabs(["3D laboratory","AI tutor","Tutorial & export"])
    with lab:
        st.subheader(name)
        cols=st.columns(3)
        for i,(k,v) in enumerate(r["metrics"].items()): cols[i%3].metric(k,f"{v:,.4g}")
        st.plotly_chart(r["fig"],use_container_width=True,key=name+"3d")
        st.caption("Drag to orbit · scroll/pinch to zoom · use chart toolbar to reset camera")
        st.plotly_chart(r["chart"],use_container_width=True,key=name+"graph")
        st.latex(r["formula"]);st.info(r["note"])
        if name=="Helical spring designer":
            if r["metrics"]["Stress safety ratio"]<1: st.error("Calculated shear stress exceeds the selected allowable stress.")
            if not 4<=r["metrics"]["Spring index"]<=12: st.warning("Spring index outside the common preliminary design range of 4–12.")
        if name=="Pressure vessel" and values[1]/values[2]<=20: st.warning("Thin-wall assumption is not satisfied.")
    with tutor:
        st.subheader("NVIDIA AI Tutor")
        try: key=st.secrets.get("NVIDIA_API_KEY",""); model=st.secrets.get("NVIDIA_MODEL","meta/llama-3.3-70b-instruct")
        except Exception: key="";model="meta/llama-3.3-70b-instruct"
        key=key or os.getenv("NVIDIA_API_KEY","")
        if not key: st.warning("Administrator: configure NVIDIA_API_KEY in Streamlit secrets. Simulations work without it.")
        history=st.session_state.setdefault("history_"+name,[])
        if st.button("Clear conversation"): history.clear()
        for msg in history:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        question=st.chat_input("Ask about this experiment",disabled=not bool(key))
        if question:
            history.append({"role":"user","content":question})
            with st.chat_message("user"): st.markdown(question)
            with st.chat_message("assistant"):
                try:
                    with st.spinner("Tutor is thinking..."): reply=answer(key,model,history,context)
                    st.markdown(reply);history.append({"role":"assistant","content":reply})
                except Exception: st.error("NVIDIA request failed. Check model access, API key, quota and connectivity.")
    with guide:
        st.subheader("Guided experiment")
        st.markdown("**Aim:** Investigate "+name.lower()+" and the relationship between its inputs and outputs.")
        st.markdown("1. Record the initial parameters and calculated results.\n2. Rotate the 3D model and inspect its geometry.\n3. Change one input while holding the others constant.\n4. Compare the graph and numerical results with the governing equation.\n5. Ask the AI tutor to explain the trend and discuss assumptions.")
        st.latex(r["formula"]);st.write(r["note"])
        st.subheader("Observation journal")
        observation=st.text_area("Record your observations",key="obs_"+name)
        report="# "+name+"\n\n## Inputs and results\n"+context+"\n\n## Observations\n"+observation
        st.download_button("Download lab journal",report,file_name="lab_journal.md")
        st.download_button("Download interactive 3D model",r["fig"].to_html(include_plotlyjs=True),file_name="model.html",mime="text/html")
        st.download_button("Download experiment data",context,file_name="experiment.json",mime="application/json")


if __name__ == "__main__":
    main()
