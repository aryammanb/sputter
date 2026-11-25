from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Polygon
from matplotlib import font_manager

P=Path(__file__).resolve().parent
plt.rcParams['font.family']='DejaVu Sans'
fig=plt.figure(figsize=(18,12),facecolor='#f2f5f8')
ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,18),ylim=(0,12));ax.axis('off')
ink='#183247';muted='#526879';blue='#2078ae';orange='#c46c26';teal='#187c70'

def text(x,y,s,size=12,color=ink,weight='normal',ha='center',va='center'):
 ax.text(x,y,s,fontsize=size,color=color,weight=weight,ha=ha,va=va,linespacing=1.45)
def panel(x,title,subtitle):
 ax.add_patch(FancyBboxPatch((x,.65),8.35,9.7,boxstyle='round,pad=.03,rounding_size=.18',facecolor='white',edgecolor='#d6e0e7',lw=1.2))
 text(x+.35,9.93,title,18,weight='bold',ha='left')
 text(x+.35,9.45,subtitle,11,color=muted,ha='left')
def block(cx,cy,w,h,title,sub='',color=blue):
 ax.add_patch(FancyBboxPatch((cx-w/2,cy-h/2),w,h,boxstyle='round,pad=.025,rounding_size=.13',facecolor='#f1f7fb' if color==blue else '#edf7f4',edgecolor=color,lw=1.7,zorder=3))
 text(cx,cy+(.13 if sub else 0),title,14,weight='bold')
 if sub:text(cx,cy-.23,sub,10,color=muted)
def pipe(points,color=blue,lw=3):
 xs,ys=zip(*points);ax.plot(xs,ys,color=color,lw=lw,solid_capstyle='round',zorder=1)
def arrow(a,b,color=blue):
 ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=17,color=color,lw=2,zorder=2))
def valve(cx,cy,tag,color=blue):
 # Vertical isolation-valve symbol, with crossing triangles.
 ax.add_patch(Polygon([(cx-.16,cy+.18),(cx+.16,cy+.18),(cx,cy),(cx-.16,cy-.18),(cx+.16,cy-.18),(cx,cy)],closed=True,facecolor='white',edgecolor=color,lw=1.8,zorder=4))
 text(cx+.3,cy,tag,12,color=color,weight='bold',ha='left')
def dot(x,y):ax.add_patch(Circle((x,y),.065,fc=blue,ec='white',lw=.8,zorder=4))

text(.55,11.3,'SPUTTER CHAMBER | TWO SINGLE-PUMP PLUMBING OPTIONS',24,weight='bold',ha='left')
text(.55,10.78,'Gas-flow schematics for the EXT70 system. Both layouts use one rotary vane pump.',13,color=muted,ha='left')
panel(.55,'A  |  Pump through the turbo','One serial pumping path; simplest plumbing')
panel(9.1,'B  |  Separate roughing and backing branches','One shared pump; independently valved flow paths')

# Option A: all gas passes through turbo to rotary-pump inlet.
x=3.45
block(x,8.45,3.9,.85,'VACUUM CHAMBER','12 L nominal chamber')
block(x,6.4,2.65,.85,'EXT70 TURBO','High-vacuum inlet above')
block(x,3.95,3.9,.9,'ROTARY VANE PUMP','Suction / inlet at top',teal)
pipe([(x,8.0),(x,6.85)]);arrow((x,7.8),(x,7.1))
pipe([(x,5.95),(x,4.4)]);arrow((x,5.75),(x,4.65))
text(x+.3,5.2,'Backing / foreline',12,color=blue,ha='left')
pipe([(x,3.5),(x,2.92)],muted,2);arrow((x,3.35),(x,2.93),muted)
text(x,2.7,'Exhaust → suitable discharge / treatment',10,color=muted)
text(1.0,2.15,'INITIAL PUMP-DOWN',11,weight='bold',ha='left')
text(1.0,1.72,'Rotary pump evacuates the chamber through the turbo.\nStart the turbo according to its controller/manual.',11,color=muted,ha='left')
text(1.0,1.08,'HIGH VACUUM: same path; both pumps operate.',11,color=ink,ha='left')

# Option B: chamber branch and turbo outlet branch join at pump suction.
cx=13.25;tx=11.25;rx=15.5
block(cx,8.45,5.9,.85,'VACUUM CHAMBER','Two chamber connections')
pipe([(tx,8.0),(tx,6.85)]);valve(tx,7.43,'H');arrow((tx,7.18),(tx,6.93))
block(tx,6.4,2.25,.85,'EXT70 TURBO')
pipe([(tx,5.95),(tx,4.95),(cx,4.95),(cx,4.4)])
valve(tx,5.48,'B');arrow((tx,5.93),(tx,5.73));arrow((11.7,4.95),(12.8,4.95))
pipe([(rx,8.0),(rx,4.95),(cx,4.95)],orange)
valve(rx,6.4,'R',orange);arrow((rx,7.6),(rx,6.8),orange);arrow((rx,5.95),(rx,5.13),orange);arrow((15.1,4.95),(13.7,4.95),orange)
dot(cx,4.95)
text(12.0,5.6,'Backing branch',10,color=blue,ha='left')
text(rx+.33,7.35,'Direct\nroughing',11,color=orange,ha='left')
block(cx,3.95,4.1,.9,'ONE ROTARY VANE PUMP','Both branches join at suction / inlet',teal)
pipe([(cx,3.5),(cx,3.05)],muted,2);arrow((cx,3.4),(cx,3.05),muted)
text(cx,2.83,'Exhaust → suitable discharge / treatment',10,color=muted)

text(9.55,2.3,'H  Chamber–turbo isolation     B  Backing isolation\nR  Direct roughing isolation',10.5,weight='bold',ha='left')
text(9.55,1.65,'HIGH VACUUM: H + B open; R closed.\nROUGHING: H closed; R open; B follows the validated sequence.',10.5,color=muted,ha='left')
text(9.55,1.02,'Keeping the turbo spinning needs foreline-pressure monitoring\nand a verified switching / holding arrangement.',10.5,color='#9b5420',ha='left')

text(.6,.28,'Arrows show gas flow toward pump suction. Cooling, venting, gauges, anti-suckback protection and interlocks are omitted for clarity.  |  24 November 2026',9,color=muted,ha='left')
fig.savefig(P/'Vacuum plumbing - two single-pump options.png',dpi=200,facecolor=fig.get_facecolor())
fig.savefig(P/'Vacuum plumbing - two single-pump options.svg',facecolor=fig.get_facecolor())
print('Saved PNG and editable SVG plumbing graphic')
