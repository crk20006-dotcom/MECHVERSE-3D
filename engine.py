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
