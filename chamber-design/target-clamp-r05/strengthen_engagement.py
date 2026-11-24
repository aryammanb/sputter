from pathlib import Path
p=Path('chamber-design/target-clamp-r05/build_clamp_revision.py');s=p.read_text();anchor="  native_gun.append(q|{'shape':native})"
replacement="""  if q['role']=='gun_targetbolts':
   axis=next(f._geomAdaptor().Cylinder().Axis().Location() for f in native.Faces() if f.geomType()=='CYLINDER' and abs(f._geomAdaptor().Cylinder().Radius()-1.5)<.02)
   xx,zz=axis.X(),axis.Z();trim=cq.Solid.makeBox(8,.6,8,V(xx-4,-7.2,zz-4))
   shaft=cq.Solid.makeCylinder(1.5,2.3,V(xx,-8.8,zz),V(0,1,0));tip=cq.Solid.makeCone(1.3,1.5,.2,V(xx,-9,zz),V(0,1,0))
   native=native.cut(trim).fuse(shaft,tip).clean();assert native.isValid() and len(native.Solids())==1
   q['name']+=' R05 M3x10';q['note']='R05 nominal M3x10 replaces M3x8, same head seatY1; tipY-9. Verify full useful M3x0.5 thread toY-9 and pilot bottomY-10.'
  native_gun.append(q|{'shape':native})"""
s=s.replace(anchor,replacement).replace("checks['pilot_bottom_margin_mm']=lo-(-10)","checks['pilot_bottom_margin_mm']=bb(screw)[1]-(-10);checks['screw_physical_tip_y_mm']=bb(screw)[1];checks['screw_underhead_y_mm']=1;checks['previous_straight_pilot_engagement_mm']=3.55")
s=s.replace("'screw_PCD':80", "'screw_spec':'M3 x10 (12 pieces)','screw_PCD':80")
p.write_text(s)
