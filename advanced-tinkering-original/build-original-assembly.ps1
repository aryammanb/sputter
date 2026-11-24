param([switch]$RepairHV)
$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -Path 'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.swconst.dll'
Add-Type -ReferencedAssemblies $dll,'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.swconst.dll','System.Web.Extensions' -TypeDefinition @'
using System;using System.IO;using System.Text;using System.Linq;using System.Collections.Generic;using System.Web.Script.Serialization;using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;using SolidWorks.Interop.swconst;
public class ATReconstruction {
 public class Point {public double X,Z;}
 public class Plan {public Point[] Magnets,TargetScrews,BackplateScrews,SpacerScrews,BaseScrews,ClampHalfScrews;public double TubeDisplayLength;public string[] KnownUncertainties;}
 public class Item {public string Name,Path,Class,Receiver;public double[] Transform;public Item(string n,string p,string cls,string recv="",double x=0,double y=0,double z=0,double[] tx=null){Name=n;Path=p;Class=cls;Receiver=recv;Transform=tx??Tx(x,y,z);}}
 static ISldWorks sw;static IModelDoc2 d;static string root,gen;static Plan plan;static JavaScriptSerializer js=new JavaScriptSerializer();static List<object> partLog=new List<object>();static List<object> itemLog=new List<object>();
 static string Template(string f){return @"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2021\templates\"+f;}
 static double[] Tx(double x=0,double y=0,double z=0){return new double[]{1,0,0,0,1,0,0,0,1,x/1000,y/1000,z/1000,1,0,0,0};}
 static double[] Down(double x,double y,double z){return new double[]{1,0,0,0,-1,0,0,0,-1,x/1000,y/1000,z/1000,1,0,0,0};}
 static double[] Radial(double theta,double y){double a=theta*Math.PI/180,c=Math.Cos(a),s=Math.Sin(a);return new double[]{-s,0,c,-c,0,-s,0,-1,0,.0508*c,y/1000,.0508*s,1,0,0,0};}
 static void Prop(string k,string v){d.Extension.CustomPropertyManager[""].Add3(k,30,v,2);}
 static void Save(string path){int e=0,w=0;if(!d.Extension.SaveAs(path,0,1,null,ref e,ref w)||e!=0)throw new Exception("Save failed "+path+" error="+e);}
 static void Open(string path,int type=1){int e=0,w=0;d=(IModelDoc2)sw.OpenDoc6(path,type,1,"",ref e,ref w);if(d==null||e!=0)throw new Exception("Open "+path+" error="+e);sw.ActivateDoc3(d.GetTitle(),false,0,ref e);}
 static IFeature StartFront(){
  d=(IModelDoc2)sw.NewDocument(Template("Part.PRTDOT"),0,0,0);if(d==null)throw new Exception("New part");int e=0;sw.ActivateDoc3(d.GetTitle(),false,0,ref e);
  if(!d.Extension.SelectByID2("Front Plane","PLANE",0,0,0,false,0,null,0))throw new Exception("Front plane");d.SketchManager.InsertSketch(true);d.SketchManager.AddToDB=true;return (IFeature)d.SketchManager.ActiveSketch;
 }
 static void RevolveEnd(IFeature sk,SketchSegment axis,double angle=2*Math.PI){
  d.SketchManager.AddToDB=false;d.SketchManager.InsertSketch(true);sk.Name="Reconstructed nominal axial profile";d.ClearSelection2(true);sk.Select2(false,0);
  var sel=(SelectData)((ISelectionMgr)d.SelectionManager).CreateSelectData();sel.Mark=16;axis.Select4(true,sel);
  var f=d.FeatureManager.FeatureRevolve2(true,true,false,false,false,false,0,0,angle,0,false,false,0,0,0,0,0,true,true,true);if(f==null)throw new Exception("Revolve failed");f.Name="Native revolved geometry";
 }
 static void Profile(double[,] pts){var sk=StartFront();var s=d.SketchManager;var axis=s.CreateCenterLine(0,-.5,0,0,.05,0);
  for(int i=0;i<pts.GetLength(0);i++){int j=(i+1)%pts.GetLength(0);s.CreateLine(pts[i,1]/1000,pts[i,0]/1000,0,pts[j,1]/1000,pts[j,0]/1000,0);}RevolveEnd(sk,axis);}
 static void Tube(double a,double b,double r,double inner=0){Profile(new double[,]{{a,inner},{b,inner},{b,r},{a,r}});}
 static void Ring(double major,double radial,double axial,double angle=2*Math.PI){var sk=StartFront();var s=d.SketchManager;var axis=s.CreateCenterLine(0,-.5,0,0,.05,0);
  if(Math.Abs(radial-axial)<1e-8)s.CreateCircleByRadius(major/1000,0,0,radial/1000);else s.CreateEllipse(major/1000,0,0,(major+radial)/1000,0,0,major/1000,axial/1000,0);RevolveEnd(sk,axis,angle);}
 static double[] SP(double x,double y,double z){var math=(IMathUtility)sw.GetMathUtility();return (double[])((IMathPoint)((IMathPoint)math.CreatePoint(new double[]{x/1000,y/1000,z/1000})).MultiplyTransform((MathTransform)d.SketchManager.ActiveSketch.ModelToSketchTransform)).ArrayData;}
 static void WorldLine(double[] a,double[] b){var p=SP(a[0],a[1],a[2]);var q=SP(b[0],b[1],b[2]);d.SketchManager.CreateLine(p[0],p[1],0,q[0],q[1],0);}
 static void WorldArc(double[] a,double[] b,double[] mid){var p=SP(a[0],a[1],a[2]);var q=SP(b[0],b[1],b[2]);var t=SP(mid[0],mid[1],mid[2]);if(d.SketchManager.Create3PointArc(p[0],p[1],0,q[0],q[1],0,t[0],t[1],0)==null)throw new Exception("Path arc");}
 static string EndPart(string name,string cls,string material,double[] color,string detail){
  Prop("Reconstruction evidence",cls);Prop("Specified material",material);Prop("Details and limits",detail);Prop("Purpose","Study reconstruction of Advanced Tinkering source design; not a new design or manufacturing release.");
  d.MaterialPropertyValues=new double[]{color[0],color[1],color[2],.3,.8,.2,.25,0,0};d.ForceRebuild3(false);
  var bs=(object[])((IPartDoc)d).GetBodies2(0,false);if(bs==null||bs.Length!=1)throw new Exception(name+" must be one solid");var b=(Body2)bs[0];double volume=((double[])b.GetMassProperties(1))[3]*1e9;if(volume<=0)throw new Exception("Empty solid "+name);
  string path=Path.Combine(gen,name+".SLDPRT");d.ShowNamedView2("*Isometric",7);d.ViewZoomtofit2();Save(path);partLog.Add(new {name=name,path=path,evidence=cls,material=material,volume_mm3=volume,box_m=(double[])b.GetBodyBox(),detail=detail});Console.WriteLine("Created "+name);sw.CloseDoc(d.GetTitle());return path;
 }
 static string Screw(string name,double diameter,double length){
  double sr=diameter/2,hr=diameter==3?2.75:diameter==4?3.5:4.25,h=diameter;
  Profile(new double[,]{{-h,0},{-h,hr-.2},{-h+.2,hr},{0,hr},{0,sr},{length-.2,sr},{length,sr-.2},{length,0}});
  // Socket geometry is shown; thread helices are represented by nominal major-diameter cylinders.
  d.ClearSelection2(true);if(!d.Extension.SelectByID2("Top Plane","PLANE",0,0,0,false,0,null,0))throw new Exception("Socket plane");var s=d.SketchManager;s.InsertSketch(true);s.AddToDB=true;
  double across=diameter==3?2.5:diameter==4?3:4,r=across/Math.Sqrt(3);var vertices=new double[6][];
  for(int i=0;i<6;i++){double a=i*Math.PI/3;vertices[i]=new double[]{r*Math.Cos(a),0,r*Math.Sin(a)};}
  for(int i=0;i<6;i++)WorldLine(vertices[i],vertices[(i+1)%6]);var sk=(IFeature)s.ActiveSketch;s.AddToDB=false;s.InsertSketch(true);d.ClearSelection2(true);sk.Select2(false,0);
  var cut=d.FeatureManager.FeatureCut4(true,false,true,0,1,h*.5/1000,.1,false,false,false,false,0,0,false,false,false,false,false,true,true,false,false,false,3,-h/1000,false,false);
  if(cut==null)throw new Exception("Socket cut failed "+name);cut.Name="Simplified nominal hex socket";
  return EndPart(name,"Geometry-derived standard hardware; length inferred from stack","Stainless steel; strength class not specified",new double[]{.63,.67,.72},"Nominal M"+diameter+" x "+length+" socket-head screw. Helical threads omitted; nominal shaft overlaps receiving thread minor diameters intentionally. Head/socket detailing is a study representation, not a toolbox certified part.");
 }
 static string Hose(string name,bool axisZ,double q0,double qend,double sign,double worldStart,double bendStart,double bendEnd,double outer,double inner,double[] color){
  d=(IModelDoc2)sw.NewDocument(Template("Part.PRTDOT"),0,0,0);if(d==null)throw new Exception("Hose part");int e=0;sw.ActivateDoc3(d.GetTitle(),false,0,ref e);
  string plane=axisZ?"Right Plane":"Front Plane";if(!d.Extension.SelectByID2(plane,"PLANE",0,0,0,false,0,null,0))throw new Exception("Hose plane");var s=d.SketchManager;s.InsertSketch(true);s.AddToDB=true;
  Func<double,double,double[]> pt=(q,y)=>axisZ?new double[]{0,y-worldStart,q*sign}:new double[]{q*sign,y-worldStart,0};
  double dx=q0-qend,dy=bendStart-bendEnd,R=(dx*dx+dy*dy)/(4*dx),theta=2*Math.Atan(dx/dy);double qm=(q0+qend)/2,ym=(bendStart+bendEnd)/2;
  if(name.Contains("HV copper")){
   // Bare-wire tail exits radially under the screw head, then passes through its annular clearance.
   WorldLine(pt(q0-1.5,worldStart),pt(q0-.3,worldStart));
   WorldArc(pt(q0-.3,worldStart),pt(q0,worldStart-.3),pt(q0-.3+.3/Math.Sqrt(2),worldStart-.3+.3/Math.Sqrt(2)));
   WorldLine(pt(q0,worldStart-.3),pt(q0,bendStart));
  }else WorldLine(pt(q0,worldStart),pt(q0,bendStart));
  WorldArc(pt(q0,bendStart),pt(qm,ym),pt(q0-R+R*Math.Cos(theta/2),bendStart-R*Math.Sin(theta/2)));
  WorldArc(pt(qm,ym),pt(qend,bendEnd),pt(qend+R-R*Math.Cos(theta/2),bendEnd+R*Math.Sin(theta/2)));
  WorldLine(pt(qend,bendEnd),pt(qend,-300));var path=(IFeature)s.ActiveSketch;s.AddToDB=false;s.InsertSketch(true);path.Name="Illustrative smooth utility route";
  d.ClearSelection2(true);if(!d.Extension.SelectByID2("Top Plane","PLANE",0,0,0,false,0,null,0))throw new Exception("Hose profile plane");s.InsertSketch(true);s.AddToDB=true;var c=SP(axisZ?0:q0*sign,0,axisZ?q0*sign:0);
  s.CreateCircleByRadius(c[0],c[1],0,outer/1000);if(inner>0)s.CreateCircleByRadius(c[0],c[1],0,inner/1000);var profile=(IFeature)s.ActiveSketch;s.AddToDB=false;s.InsertSketch(true);profile.Name="Utility circular cross section";
  d.ClearSelection2(true);if(inner>0){profile.Select2(false,1);path.Select2(true,4);}else path.Select2(false,4);
  var f=d.FeatureManager.InsertProtrusionSwept4(false,false,0,false,true,0,0,false,0,0,0,0,true,true,true,0,true,inner<=0,inner<=0?2*outer/1000:0,0);
  if(f==null)throw new Exception("Utility sweep failed "+name);f.Name="Native hollow utility sweep";
  Prop("Reference placement Y mm",worldStart.ToString(System.Globalization.CultureInfo.InvariantCulture));
  return EndPart(name,"Illustrative flexible utility; not measured original routing",axisZ?"Cable material representation":"Polymer coolant hose representation",color,"Smooth S-bend with OD"+(2*outer)+" ID"+(2*inner)+"mm. Interface/routing fit illustration only. Exact hose/cable dimensions, lengths, materials and fitting identity were not supplied.");
 }
 static string CleanClamp(){
  Open(Path.Combine(root,"parts","Flanschklemme.SLDPRT"));var bs=(object[])((IPartDoc)d).GetBodies2(0,false);Body2 largest=null;double max=0;foreach(Body2 b in bs){double v=((double[])b.GetMassProperties(1))[3];if(v>max){max=v;largest=b;}}
  var copy=(Body2)largest.Copy();d=(IModelDoc2)sw.NewDocument(Template("Part.PRTDOT"),0,0,0);if(d==null)throw new Exception("Clamp new part");var f=(Feature)((IPartDoc)d).CreateFeatureFromBody3(copy,false,0);if(f==null)throw new Exception("Clamp body copy");f.Name="Exact source clamp-half solid";
  return EndPart("AT original flange clamp half","Exact largest STEP solid; microscopic fragment excluded","316L stainless steel supplied specification",new double[]{.64,.67,.72},"Source Flanschklemme.step contains one complete clamp half and an extra fragment of1.45e-9 mm3. This part copies the full solid unchanged. Second instance rotates180degrees about original Y axis; source files retained unchanged.");
 }
 static string Assembly(string name,List<Item> items,bool main=false){
  d=(IModelDoc2)sw.NewDocument(Template("Assembly.ASMDOT"),0,0,0);if(d==null)throw new Exception("Assembly template");int e=0;sw.ActivateDoc3(d.GetTitle(),false,0,ref e);var a=(IAssemblyDoc)d;
  var paths=items.Select(i=>i.Path).ToArray();var systems=items.Select(i=>"").ToArray();var tx=new double[16*items.Count];for(int i=0;i<items.Count;i++)Array.Copy(items[i].Transform,0,tx,16*i,16);
  var added=(object[])a.AddComponents3(paths,tx,systems);if(added==null||added.Length!=items.Count)throw new Exception("Insertion count "+name);
  for(int i=0;i<items.Count;i++){var c=(Component2)added[i];d.ClearSelection2(true);c.Select4(false,null,false);c.Name2=items[i].Name;a.FixComponent();itemLog.Add(new {assembly=name,name=c.Name2,path=c.GetPathName(),evidence=items[i].Class,receiver=items[i].Receiver,transform=items[i].Transform});}
  d.ClearSelection2(true);d.ForceRebuild3(false);Prop("Reconstruction source","Advanced Tinkering, Breaking Down My Magnetron Design, https://www.youtube.com/watch?v=MslftqA7LYw and ten user-supplied STEP files.");
  Prop("Placement method","Supplied common assembly coordinates retained; added parts placed from source surfaces and hole axes. Fixed rigid placements, no free degrees of freedom; not a mechanically mated motion model.");
  Prop("Evidence limits","Original STEP geometry and magnet/O-ring nominal sizes are source-backed. Missing standard hardware, sleeves and utilities are identified in reconstruction manifest. Tube length200mm is illustrative pending source information.");
  d.ShowNamedView2("*Isometric",7);d.ViewZoomtofit2();string path=Path.Combine(root,name+".SLDASM");Save(path);if(main)Save(Path.Combine(root,name+".step"));Console.WriteLine("Assembly "+name+" components="+items.Count);return path;
 }
 public static void Run(string folder){
  root=folder;gen=Path.Combine(root,"reconstructed parts");Directory.CreateDirectory(gen);plan=js.Deserialize<Plan>(File.ReadAllText(Path.Combine(root,"construction-plan.json")));js.MaxJsonLength=10000000;
  try{sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");}catch(COMException){sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));}
  Func<string,string> original=n=>Path.Combine(root,"parts",n+".SLDPRT");
  string clamp=CleanClamp();
  Tube(0,20,4);string rod=EndPart("AT outer magnet D8x20 N45","User-supplied nominal size and grade; centers from source holes","NdFeB N45",new double[]{.73,.25,.25},"12 axial rods, Y-22.5..-2.5; target-facing pole S per video11:05. Source holes D9 on PCD50. No magnetic FEA implied.");
  Tube(0,10,6);string disc=EndPart("AT center magnet D12x10 N45","User-supplied nominal size and grade","NdFeB N45",new double[]{.25,.43,.78},"2 axial discs stacked in same magnetization direction. Target-facing stack pole N per video11:05. Y-22.5..-12.5 and-12.5..-2.5.");
  Tube(0,2,25.4);string target=EndPart("AT titanium target D50p8x2 fitted","Video material and nominal diameter;2mm thickness inferred from clamp contact plane","Titanium",new double[]{.52,.55,.6},"Study target fills Y0..2, matching source target seat Y0 and clamp lip Y2. Actual supplied target STEP absent; thickness inference recorded.");
  var sealSpecs=new[]{new double[]{14.5,8.675,-9.725},new double[]{35,18.425,-9.725},new double[]{76,39.425,-12.725},new double[]{62,32.425,0}};
  var installed=new Dictionary<double,string>();
  foreach(var q in sealSpecs){double freeR=q[0]/2+1,major=q[1],hy=.725,rx=freeR/(major*hy);
   Ring(major,rx,hy);Prop("Free-state nominal ring","ID"+q[0]+" x2mm");Prop("Installed envelope","Volume-preserving elliptical cross section,1.45mm axial height. An illustrative occupied-volume envelope, not a predicted elastomer deformation shape.");
   installed[q[0]]=EndPart("AT O-ring ID"+q[0].ToString(System.Globalization.CultureInfo.InvariantCulture).Replace('.','p')+"x2 installed","Nominal size from user; installed envelope fitted to measured source gland","FKM per user specification",new double[]{.12,.13,.14},"Free nominal torus volume retained. Installed radius chosen inside measured gland. Cross section is visual fit only, no seal performance claim.");
   Ring(freeR,1,1);EndPart("AT O-ring ID"+q[0].ToString(System.Globalization.CultureInfo.InvariantCulture).Replace('.','p')+"x2 free","Exact user-supplied nominal free dimensions","FKM per user specification",new double[]{.12,.13,.14},"Uncompressed circular cross-section ring; supplied as a separate free-state part and not inserted into closed assembly.");
  }
  Profile(new double[,]{{-1.5,1.65},{22,1.65},{22,2.8},{0,2.8},{0,3.9},{-1.5,3.9}});string sleeve=EndPart("AT PTFE screw shoulder sleeve fitted","Reconstructed compatible profile from source bore/counterbore and video; no original sleeve drawing","PTFE",new double[]{.9,.9,.86},"Shank OD5.6 ID3.3 x22mm; flange OD7.8 x1.5mm. Shoulder at Y-68, noseY-46, flange backY-69.5. Fits source D5.8 bore,D8 counterbore. Exact original flange thickness and sleeve profile unverified.");
  var screws=new Dictionary<string,string>();foreach(var q in new[]{new double[]{3,6},new double[]{3,8},new double[]{3,16},new double[]{3,35},new double[]{4,8},new double[]{4,10},new double[]{5,20}}){string key="M"+q[0]+"x"+q[1];screws[key]=Screw("AT "+key+" socket-head study",q[0],q[1]);}
  Ring(2.3,.18,.18,5*Math.PI/3);string hook=EndPart("AT bare HV wire hook representative","Video hook connection; exact wire diameter/shape not specified","Copper conductor representation",new double[]{.8,.48,.25},"300degree wire eye around M4 terminal screw. MajorR2.3 and wireD0.36, placedY-22.68 Z13.55. Thin wire is a collision-free illustration, not a conductor specification.");
  Profile(new double[,]{{-13,2.1},{7,2.1},{7,3.7},{0,3.7},{0,6.5},{-11,6.5},{-11,4},{-13,4}});string fitting=EndPart("REF coolant push-in fitting body","Video appearance and source clearance fitted; exact fitting not identified","Reference metal fitting body",new double[]{.3,.32,.35},"Local shoulderY0 at BackplateY-22.5; rear body13mm; nominal inserted stem7mm. No specific thread standard claimed. Passes source yokeD14 clearance. Fits are representative, not a purchased-part model.");
  Tube(-13,-11,5.25,4);string collet=EndPart("REF coolant fitting blue release collar","Illustrative matching visible fitting appearance","Reference polymer collar",new double[]{.13,.4,.75},"Reference-only blue collar; exact manufacturer part dimensions absent.");
  double yFlange=-78,yEnd=yFlange-plan.TubeDisplayLength;
  Profile(new double[,]{{yFlange,8.6},{yFlange-2.5,8.6},{yFlange-2.5,8},{yEnd,8},{yEnd,10},{yFlange-4.339745962,10},{yFlange-3,15},{yFlange,15}});
  string tube=EndPart("REF KF16 flanged tube L200","Standard-form KF16 interface with source-fitted placement; tube length is illustrative","Stainless steel reference",new double[]{.58,.63,.68},"D30 flange,5mm nominal flange envelope,15degree rear taper,D20x2 tube; mating faceY-78,basefaceY-74,4mm seal gap.200mm displayed length is not verified original length. Replace with source purchased component when known.");
  Profile(new double[,]{{-80,8},{-72,8},{-72,8.5},{-74,8.5},{-74,9},{-78,9},{-78,8.5},{-80,8.5}});string cr=EndPart("REF KF16 centering ring fitted","Representative standard-form component; exact supplier model absent","Stainless steel reference",new double[]{.6,.63,.68},"D17 pilots and D16 bore; overall8mm height,4mm center shoulder. Fits source D17.2 receiver. Installed component shape is representative, not manufacturer-certified.");
  Ring(12,6.25*11.5/(12*2),2);string kfseal=EndPart("REF KF16 O-ring installed envelope","Representative18x5 metric KF16 ring; exact installed seal identity unconfirmed","FKM reference",new double[]{.12,.13,.14},"Volume-preserving illustrative ellipse of free ID18x5 ring,4mm installed height. Not one of the five author-specified2mm face seals. Supplier ISO-KF variant remains to verify.");
  string hoseR=Hose("REF blue coolant hose right",false,13.55,3,1,-29.5,-43,-63,2,1.25,new double[]{.13,.38,.75});
  string hoseL=Hose("REF blue coolant hose left",false,13.55,3,-1,-29.5,-43,-63,2,1.25,new double[]{.13,.38,.75});
  string lead=Hose("REF HV copper conductor route",true,17.35,4.5,1,-22.68,-40,-64,.18,0,new double[]{.8,.48,.25});
  string jacket=Hose("REF white HV cable insulation",true,17.35,4.5,1,-34,-40,-64,1.75,.18,new double[]{.9,.9,.86});
  // Build subassemblies. Every original component retains its original source coordinates.
  var cathode=new List<Item>{new Item("S_Kuehlkoerper",original("Kuehlkoerper"),"Exact original STEP"),new Item("S_Backplate",original("Backplate"),"Exact original STEP"),new Item("S_MagnetYoke",original("Magnet Joke"),"Exact original STEP"),new Item("M_CenterDiscRear",disc,"Specified magnet","",0,-22.5,0),new Item("M_CenterDiscFront",disc,"Specified magnet","",0,-12.5,0),new Item("O_WaterInner",installed[14.5],"Specified ring; installed envelope","",0,-9.725,0),new Item("O_WaterOuter",installed[35],"Specified ring; installed envelope","",0,-9.725,0),new Item("B_Yoke_M4x10",screws["M4x10"],"Geometry-derived screw","S_Backplate",0,-26.5,-13.55),new Item("B_HVTerminal_M4x8",screws["M4x8"],"Geometry-derived screw","S_Backplate",0,-22.86,13.55),new Item("R_HVHook",hook,"Video representative","",0,-22.68,13.55)};
  for(int i=0;i<12;i++){var p=plan.Magnets[i];cathode.Add(new Item("M_OuterRod_"+(i+1),rod,"Specified magnet","",p.X,-22.5,p.Z));p=plan.BackplateScrews[i];cathode.Add(new Item("B_Backplate_M3x16_"+(i+1),screws["M3x16"],"Geometry-derived screw","S_Kuehlkoerper",p.X,-18.5,p.Z));}
  foreach(double x in new[]{-13.55,13.55}){string n=x<0?"Left":"Right";cathode.Add(new Item("R_FittingBody_"+n,fitting,"Reference fitting","",x,-22.5,0));cathode.Add(new Item("R_BlueCollet_"+n,collet,"Reference fitting","",x,-22.5,0));}
  string g1=Assembly("01 Original cathode cooling and magnets",cathode);
  var spacerItems=new List<Item>{new Item("S_Abstandshalter",original("Abstandshalter"),"Exact original STEP"),new Item("O_SpacerToCopper",installed[76],"Specified ring; installed envelope","",0,-12.725,0)};
  for(int i=0;i<12;i++){var p=plan.SpacerScrews[i];spacerItems.Add(new Item("B_Head_M3x35_"+(i+1),screws["M3x35"],"Geometry-derived screw","S_Kuehlkoerper",p.X,-41,p.Z));}string g2=Assembly("02 Original spacer and copper attachment",spacerItems);
  var baseItems=new List<Item>{new Item("S_Isolator",original("Isolator"),"Exact original STEP"),new Item("S_Boden",original("Boden"),"Exact original STEP"),new Item("O_SpacerToPTFE",installed[62],"Specified ring; installed envelope","",0,-40.275,0),new Item("O_PTFEToBase",installed[62],"Specified ring; installed envelope","",0,-46.725,0)};
  for(int i=0;i<12;i++){var p=plan.BaseScrews[i];baseItems.Add(new Item("I_ShoulderSleeve_"+(i+1),sleeve,"Geometry-fitted reconstructed PTFE sleeve","",p.X,-68,p.Z));baseItems.Add(new Item("B_Base_M3x35_"+(i+1),screws["M3x35"],"Geometry-derived screw","S_Abstandshalter",p.X,-69.5,p.Z));}string g3=Assembly("03 Original PTFE isolation and base",baseItems);
  var targetItems=new List<Item>{new Item("S_TargetKlemme",original("Target Klemme"),"Exact original STEP"),new Item("R_TitaniumTarget",target,"Fitted target thickness")};for(int i=0;i<12;i++){var p=plan.TargetScrews[i];targetItems.Add(new Item("B_Target_M3x8_"+(i+1),screws["M3x8"],"Geometry-derived screw","S_Kuehlkoerper",tx:Down(p.X,1,p.Z)));}string g4=Assembly("04 Original target clamp and fitted target",targetItems);
  var shieldItems=new List<Item>{new Item("S_GroundshieldTube",original("Groundshield Rohr"),"Exact original STEP"),new Item("S_DarkSpaceShield",original("Dunkelraumabschirmung"),"Exact original STEP")};for(int i=0;i<6;i++)shieldItems.Add(new Item("B_ShieldTop_M3x6_"+(i+1),screws["M3x6"],"Geometry-derived screw","S_DarkSpaceShield",tx:Radial(30+i*60,9)));for(int i=0;i<3;i++)shieldItems.Add(new Item("B_ShieldBase_M4x8_"+(i+1),screws["M4x8"],"Geometry-derived screw","S_Boden",tx:Radial(90+i*120,-60.262)));string g5=Assembly("05 Original grounded shield",shieldItems);
  double[] flip=new double[]{-1,0,0,0,1,0,0,0,-1,0,0,0,1,0,0,0};
  var mountItems=new List<Item>{new Item("S_ClampHalfA",clamp,"Exact source main solid"),new Item("S_ClampHalfB",clamp,"Second source half by180deg symmetry",tx:flip),new Item("R_KF16Tube",tube,"Reference purchased tube"),new Item("R_KF16CenteringRing",cr,"Reference centering ring"),new Item("R_KF16Seal",kfseal,"Reference seal installed envelope","",0,-76,0)};
  for(int i=0;i<3;i++){var p=plan.ClampHalfScrews[i];mountItems.Add(new Item("B_KFClamp_M5x20_A"+(i+1),screws["M5x20"],"Geometry-derived screw","S_Boden",p.X,-88.3165,p.Z));mountItems.Add(new Item("B_KFClamp_M5x20_B"+(i+1),screws["M5x20"],"Geometry-derived screw","S_Boden",-p.X,-88.3165,-p.Z));}string g6=Assembly("06 Original clamp and reference KF16 tube",mountItems);
  var utilities=new List<Item>{new Item("R_RightCoolantHose",hoseR,"Illustrative flexible routing","",0,-29.5,0),new Item("R_LeftCoolantHose",hoseL,"Illustrative flexible routing","",0,-29.5,0),new Item("R_HVLead",lead,"Illustrative bare conductor","",0,-22.68,0),new Item("R_HVJacket",jacket,"Illustrative insulation route","",0,-34,0)};string g7=Assembly("07 Reference atmospheric utility routes",utilities);
  var groups=new List<Item>{new Item("G1_Cathode",g1,"Original geometry plus reconstructed components"),new Item("G2_Spacer",g2,"Original geometry plus reconstructed components"),new Item("G3_BaseIsolation",g3,"Original geometry plus reconstructed components"),new Item("G4_Target",g4,"Original geometry plus reconstructed components"),new Item("G5_GroundShield",g5,"Original geometry plus reconstructed components"),new Item("G6_KFMount",g6,"Original geometry plus reference components"),new Item("G7_UtilityRoutes",g7,"Reference utilities")};
  Assembly("Advanced Tinkering magnetron - full reconstruction",groups,true);
  File.WriteAllText(Path.Combine(root,"generated-parts.json"),js.Serialize(partLog),Encoding.UTF8);File.WriteAllText(Path.Combine(root,"assembly-manifest.json"),js.Serialize(itemLog),Encoding.UTF8);
  Console.WriteLine("COMPLETE: assembly built; run independent source and interference audit before delivery.");
 }
 public static void RepairHVOnly(string folder){
  root=folder;gen=Path.Combine(root,"reconstructed parts");try{sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");}catch(COMException){sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));}
  Ring(2.3,.18,.18,5*Math.PI/3);string newHook=EndPart("AT bare HV wire hook fitted","Video hook connection; exact wire diameter/shape not specified","Copper conductor representation",new double[]{.8,.48,.25},"300degree eye majorR2.3,wireD0.36,worldY-22.68,Z13.55. Wire size is a fit illustration, not an electrical specification.");
  string newLead=Hose("REF HV copper conductor fitted route",true,17.35,4.5,1,-22.68,-40,-64,.18,0,new double[]{.8,.48,.25});
  string newJacket=Hose("REF white HV cable fitted insulation",true,17.35,4.5,1,-34,-40,-64,1.75,.18,new double[]{.9,.9,.86});
  foreach(string group in new[]{"01 Original cathode cooling and magnets","07 Reference atmospheric utility routes"}){
   Open(Path.Combine(root,group+".SLDASM"),2);var a=(IAssemblyDoc)d;
   foreach(Component2 c in (object[])a.GetComponents(true)){
    string file=Path.GetFileName(c.GetPathName()),replacement=null;
    if(file=="AT bare HV wire hook representative.SLDPRT")replacement=newHook;
    if(file=="REF HV copper conductor route.SLDPRT")replacement=newLead;
    if(file=="REF white HV cable insulation.SLDPRT")replacement=newJacket;
    if(replacement!=null){d.ClearSelection2(true);c.Select4(false,null,false);if(!a.ReplaceComponents(replacement,"",false,false))throw new Exception("HV replacement "+file);}
   }
   foreach(Component2 c in (object[])a.GetComponents(true)){
    string file=Path.GetFileName(c.GetPathName());double? y=null;
    if(group.StartsWith("01")&&file=="AT M4x8 socket-head study.SLDPRT")y=-22.86;
    if(file=="AT bare HV wire hook fitted.SLDPRT"||file=="REF HV copper conductor fitted route.SLDPRT")y=-22.68;
    if(y.HasValue){d.ClearSelection2(true);c.Select4(false,null,false);a.UnfixComponent();var tx=(double[])c.Transform2.ArrayData;tx[10]=y.Value/1000;var math=(IMathUtility)sw.GetMathUtility();c.Transform2=(MathTransform)math.CreateTransform(tx);a.FixComponent();}
   }
   d.ClearSelection2(true);d.ForceRebuild3(false);int e=0,w=0;if(!d.Save3(1,ref e,ref w)||e!=0)throw new Exception("Group resave "+group);
  }
  Open(Path.Combine(root,"Advanced Tinkering magnetron - full reconstruction.SLDASM"),2);((IAssemblyDoc)d).ResolveAllLightWeightComponents(false);d.ForceRebuild3(false);int ee=0,ww=0;if(!d.Save3(1,ref ee,ref ww)||ee!=0)throw new Exception("Root resave");Save(Path.Combine(root,"Advanced Tinkering magnetron - full reconstruction.step"));
  File.WriteAllText(Path.Combine(root,"hv-repaired-parts.json"),js.Serialize(partLog),Encoding.UTF8);Console.WriteLine("HV representation updated and root rebuilt.");
 }
}
'@
if($RepairHV){[ATReconstruction]::RepairHVOnly($PSScriptRoot)}else{[ATReconstruction]::Run($PSScriptRoot)}
