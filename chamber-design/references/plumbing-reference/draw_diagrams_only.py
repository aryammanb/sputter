from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, Circle

P=Path(__file__).resolve().parent
fig=plt.figure(figsize=(14,8),facecolor='white')
ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,14),ylim=(0,8));ax.axis('off')
blue='#246b96';orange='#bd6626';ink='#19384b';teal='#218375'
def txt(x,y,s,size=12,color=ink,weight='normal',ha='center'):
 ax.text(x,y,s,ha=ha,va='center',fontsize=size,color=color,weight=weight)
def block(x,y,w,h,name,color=blue):
 ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=.025,rounding_size=.1',fc='white',ec=color,lw=2,zorder=3))
 txt(x,y,name,13,weight='bold')
def pipe(points,color=blue):
 x,y=zip(*points);ax.plot(x,y,lw=2.8,color=color,zorder=1)
def arrow(a,b,color=blue):
 ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=16,lw=2,color=color,zorder=2))
def valve(x,y,name,color=blue,side=1):
 ax.add_patch(Polygon([(x-.15,y+.17),(x+.15,y+.17),(x,y),(x-.15,y-.17),(x+.15,y-.17),(x,y)],fc='white',ec=color,lw=1.8,zorder=4))
 txt(x+side*.28,y,name,11,color,ha='left' if side==1 else 'right')

txt(3.3,7.5,'THROUGH-TURBO CONNECTION',16,weight='bold')
txt(10.6,7.5,'SEPARATE ROUGHING / BACKING CONNECTIONS',15,weight='bold')
ax.plot([6.65,6.65],[.4,7.05],color='#dce4e9',lw=1)

x=3.3
block(x,6.45,3.6,.72,'VACUUM CHAMBER')
pipe([(x,6.09),(x,4.66)]);arrow((x,5.8),(x,5.05))
block(x,4.3,2.8,.72,'EXT70 TURBO')
pipe([(x,3.94),(x,2.31)]);arrow((x,3.6),(x,2.65))
txt(x+.25,3.18,'Backing line',11,blue,ha='left')
block(x,1.95,4.1,.72,'ROTARY VANE PUMP',teal)
pipe([(x,1.59),(x,.75)],teal);arrow((x,1.4),(x,.85),teal)
txt(x,.48,'EXHAUST',10,teal)

cx=10.6;tx=8.45;rx=12.65
block(cx,6.45,5.9,.72,'VACUUM CHAMBER')
pipe([(tx,6.09),(tx,4.66)]);valve(tx,5.45,'Chamber isolation')
arrow((tx,5.16),(tx,4.8))
block(tx,4.3,2.15,.72,'EXT70 TURBO')
pipe([(tx,3.94),(tx,2.85),(cx,2.85),(cx,2.31)])
valve(tx,3.4,'Backing valve');arrow((8.85,2.85),(10.15,2.85))
pipe([(rx,6.09),(rx,2.85),(cx,2.85)],orange)
valve(rx,4.7,'Roughing valve',orange,side=-1)
arrow((rx,5.85),(rx,5.1),orange);arrow((rx,4.2),(rx,3.15),orange)
arrow((12.15,2.85),(11.1,2.85),orange)
ax.add_patch(Circle((cx,2.85),.055,fc=blue,zorder=4))
block(cx,1.95,4.6,.72,'ONE ROTARY VANE PUMP',teal)
pipe([(cx,1.59),(cx,.75)],teal);arrow((cx,1.4),(cx,.85),teal)
txt(cx,.48,'EXHAUST',10,teal)

for extension in ['png','svg']:
 fig.savefig(P/f'Vacuum plumbing - flowcharts only.{extension}',dpi=200,facecolor='white')
print('Saved diagram-only PNG and SVG in chamber-design/references/plumbing-reference')
