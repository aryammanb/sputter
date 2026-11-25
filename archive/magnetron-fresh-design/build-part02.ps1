$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;
using System.IO;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public class FreshCover02 {
 static ISldWorks sw;static IModelDoc2 d;
 static double[,] ports={{18*Math.Cos(Math.PI/6),9},{18*Math.Cos(Math.PI/6),-9}};
 static void Save(string p){int e=0,w=0;if(!d.Extension.SaveAs(p,0,1,null,ref e,ref w)||e!=0)throw new Exception("Save "+p+" error="+e);Console.WriteLine(Path.GetFileName(p)+" warnings="+w);}
 static void Prop(string k,string v){d.Extension.CustomPropertyManager[""].Add3(k,30,v,2);}
 static IFeature Sketch(){d.ClearSelection2(true);if(!d.Extension.SelectByID2("Right Plane","PLANE",0,0,0,false,0,null,0))throw new Exception("Sketch plane");d.SketchManager.InsertSketch(true);d.SketchManager.AddToDB=true;return (IFeature)d.SketchManager.ActiveSketch;}
 static double[] P(double y,double z){var m=(IMathUtility)sw.GetMathUtility();return (double[])((IMathPoint)((IMathPoint)m.CreatePoint(new double[]{0,y/1000,z/1000})).MultiplyTransform((MathTransform)d.SketchManager.ActiveSketch.ModelToSketchTransform)).ArrayData;}
 static void Circle(double y,double z,double r){var p=P(y,z);d.SketchManager.CreateCircleByRadius(p[0],p[1],0,r/1000);}
 static void Line(double y1,double z1,double y2,double z2){var p=P(y1,z1);var q=P(y2,z2);d.SketchManager.CreateLine(p[0],p[1],0,q[0],q[1],0);}
 static void Arc(double y1,double z1,double y2,double z2,double ym,double zm){var p=P(y1,z1);var q=P(y2,z2);var t=P(ym,zm);d.SketchManager.Create3PointArc(p[0],p[1],0,q[0],q[1],0,t[0],t[1],0);}
 static void Finish(IFeature sk,string name){d.SketchManager.AddToDB=false;d.SketchManager.InsertSketch(true);sk.Name=name+" sketch";d.ClearSelection2(true);sk.Select2(false,0);}
 static void Cut(IFeature sk,string name,double from,double depth){Finish(sk,name);var f=d.FeatureManager.FeatureCut4(true,false,true,0,1,depth/1000,.4,false,false,false,false,0,0,false,false,false,false,false,true,true,false,false,false,3,from/1000,false,false);if(f==null)throw new Exception("Cut "+name);f.Name=name;}
 static void Shot(string file,string view,int id,bool tilt){d.ClearSelection2(true);d.ShowNamedView2(view,id);if(tilt)((IModelView)d.ActiveView).RotateAboutCenter(.32,-.4);d.ViewZoomtofit2();d.GraphicsRedraw2();Save(file);}
 public static void Run(string folder){
  try{sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");}catch(COMException){sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));}
  d=(IModelDoc2)sw.NewDocument(@"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2021\templates\Part.PRTDOT",0,0,0);if(d==null)throw new Exception("Template");int ae=0;sw.ActivateDoc3(d.GetTitle(),false,0,ref ae);
  IFeature plane=(IFeature)d.FirstFeature();while(plane!=null&&plane.GetTypeName2()!="RefPlane")plane=(IFeature)plane.GetNextFeature();if(plane==null||(!plane.Select2(false,0)&&!d.Extension.SelectByID2(plane.Name,"PLANE",0,0,0,false,0,null,0)))throw new Exception("Revolve plane");
  var s=d.SketchManager;s.InsertSketch(true);s.AddToDB=true;var axis=s.CreateCenterLine(-.03,0,0,.02,0,0);
  double[,] profile={{-3,0},{0,0},{0,35},{-3,35}};
  for(int i=0;i<4;i++){int j=(i+1)%4;s.CreateLine(profile[i,0]/1000,profile[i,1]/1000,0,profile[j,0]/1000,profile[j,1]/1000,0);}
  var sk=(IFeature)s.ActiveSketch;s.AddToDB=false;s.InsertSketch(true);sk.Name="Cover disk OD70 thickness3";d.ClearSelection2(true);sk.Select2(false,0);var sel=(SelectData)((ISelectionMgr)d.SelectionManager).CreateSelectData();sel.Mark=16;axis.Select4(true,sel);
  var rev=d.FeatureManager.FeatureRevolve2(true,true,false,false,false,false,0,0,2*Math.PI,0,false,false,0,0,0,0,0,true,true,true);if(rev==null)throw new Exception("Disk revolve");rev.Name="One-piece copper cover blank";
  sk=Sketch();for(int i=0;i<2;i++)Circle(ports[i,0],ports[i,1],7);Finish(sk,"Two integral OD14 port bosses");
  var boss=d.FeatureManager.FeatureExtrusion2(true,false,false,0,0,.008,.008,false,false,false,false,0,0,false,false,false,false,true,true,true,3,-.011,false);if(boss==null)throw new Exception("Port boss extrusion");boss.Name="Integral port bosses rear8mm";
  sk=Sketch();for(int i=0;i<6;i++){double a=i*Math.PI/3;Circle(32*Math.Cos(a),32*Math.Sin(a),1.7);}Cut(sk,"Six M3 clearance holes diameter3p4 PCD64",-3,3);
  sk=Sketch();for(int i=0;i<2;i++)Circle(ports[i,0],ports[i,1],4.4);Cut(sk,"Two G1-8 tapping pilot envelopes diameter8p8 depth7",-11,7);
  sk=Sketch();for(int i=0;i<2;i++)Circle(ports[i,0],ports[i,1],2);Cut(sk,"Two water passages diameter4",-11,11);
  sk=Sketch();Line(11.3,-1.3,24.7,-1.3);Arc(24.7,-1.3,24.7,1.3,26,0);Line(24.7,1.3,11.3,1.3);Arc(11.3,1.3,11.3,-1.3,10,0);Cut(sk,"Internal bypass-strip groove length16 width2p6 depth1p5",-1.5,1.5);
  ((IPartDoc)d).SetMaterialPropertyName2(d.ConfigurationManager.ActiveConfiguration.Name,@"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\lang\english\sldmaterials\solidworks materials.sldmat","Copper");
  Prop("Part number","F01-002 revision A");Prop("Specified material","C110 copper candidate; machine cover and two port bosses from ONE blank. Generic Copper CAD material is a proxy.");
  Prop("Release status","CONCEPT CAD - NOT RELEASED FOR MANUFACTURE. Pressure, cover deflection, seal loading, threads, fluid and magnetic performance unverified.");
  Prop("Coordinates","X0 mates to F01-001 rear face. Disk X-3..0. Port bosses X-11..-3. Target side is +X.");
  Prop("Ports","Two axes Y=15.5884573 Z=+/-9 mm. Proposed G1/8-28 parallel female thread with face-sealed male fitting. CAD represents diameter8.8 x7 mm tapping pilots and diameter4 through passages; no thread helix or approved port standard is modeled. Final tap depth, lead-in, thread gauge and seal seat follow selected fitting drawing.");
  Prop("Fitting seal faces","Two OD14 boss end faces at X-11; flat sealing face for supplier-approved elastomer ring/bonded seal. No tapered pipe fitting. Verify actual seal diameter and port detail before machining. Fitting not selected or included.");
  Prop("Main sealing","Flat cover face X0 closes the two existing circular glands in F01-001 without changing their 1.5 mm assembled depth. Maintain continuous flat lands opposite R6.7-9.3 and R26.7-29.3. Primary O-rings and fasteners not included in CAD.");
  Prop("Divider treatment","Capsule groove Y10..26 Z+/-1.3 X-1.5..0 accepts candidate 2mm FKM cord strip with controlled ends. Approximate local nominal squeeze25 percent. Internal bypass reducer only, NOT a primary containment seal. End lands remain0.7mm from main gland boundaries; residual bypass must be measured. Strip not included.");
  Prop("Mechanical interfaces","Six diameter3.4 clearance holes on PCD64 at0+60n degrees. Rear screw heads external; M3 copper receiving threads in Part01 require preload and engagement design. No countersinks, thread runout, edge breaks, fillets or drill tips modeled.");
  Prop("Magnet space","Flat rear disk at X-3. Two OD14 bosses occupy radius11..25 near +/-30 degrees and project8mm. Magnet arrangement must reserve these volumes; no magnet fit verified.");
  Prop("Model method","Native revolve, merged boss extrusion and sketch cuts, regenerated by build-part02.ps1. Coordinate-defined sketches, not fully constrained production sketches.");
  d.ForceRebuild3(false);var bodies=(object[])((IPartDoc)d).GetBodies2(0,false);if(bodies==null||bodies.Length!=1)throw new Exception("Cover must be one solid");var body=(Body2)bodies[0];double vol=((double[])body.GetMassProperties(1))[3]*1e9;
  double slotArea=13.4*2.6+Math.PI*1.3*1.3;
  double expected=Math.PI*35*35*3+2*Math.PI*7*7*8-6*Math.PI*1.7*1.7*3-2*Math.PI*(4.4*4.4*7+2*2*4)-slotArea*1.5;
  if(Math.Abs(vol-expected)>.01)throw new Exception("Volume actual "+vol+" expected "+expected);
  string coverPath=Path.Combine(folder,"F01-002 Coolant cover RevA.SLDPRT");Save(coverPath);Save(Path.Combine(folder,"F01-002 Coolant cover RevA.step"));
  Shot(Path.Combine(folder,"F01-002 rear ports.png"),"*Left",3,true);Shot(Path.Combine(folder,"F01-002 sealing face.png"),"*Right",4,true);
  string report="Single solid: PASS\r\nAnalytic volume: PASS\r\nVolume mm3: "+vol.ToString("F6")+"\r\nExpected mm3: "+expected.ToString("F6")+"\r\nBounding box m: "+String.Join(", ",(double[])body.GetBodyBox())+"\r\nCover hole centers match Part01 PCD64: PASS by identical coordinate definitions\r\nPort axes match C-channel cap centers: PASS by identical coordinate definitions\r\nMinimum bridge-to-slot side ligament mm:0.7\r\nSlot end to circular gland boundary mm:0.7\r\nBoss outside separation mm:4\r\nHole edge to outer gland radius mm:1.0\r\nThese are nominal geometry checks; no pressure, leak, bypass, thermal or electrical qualification.\r\n";
  File.WriteAllText(Path.Combine(folder,"F01-002 geometry checks.txt"),report);Console.WriteLine(report);
  var cover=d;
  string bodyPath=Path.Combine(folder,"F01-001 Copper cooling body RevA.SLDPRT");int e=0,w=0;var original=(IModelDoc2)sw.OpenDoc6(bodyPath,1,1,"",ref e,ref w);if(original==null||e!=0)throw new Exception("Open mating body");
  d=(IModelDoc2)sw.NewDocument(@"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2021\templates\Assembly.ASMDOT",0,0,0);if(d==null)throw new Exception("Assembly template");sw.ActivateDoc3(d.GetTitle(),false,0,ref e);var assy=(IAssemblyDoc)d;
  var paths=new string[]{bodyPath,coverPath};var systems=new string[]{"",""};var transforms=new double[32];for(int j=0;j<2;j++)foreach(int k in new[]{0,4,8,12})transforms[16*j+k]=1;
  var added=(object[])assy.AddComponents3(paths,transforms,systems);if(added==null||added.Length!=2)throw new Exception("Assembly insertion");
  foreach(Component2 c in added){d.ClearSelection2(true);c.Select4(false,null,false);assy.FixComponent();}
  d.ClearSelection2(true);d.ForceRebuild3(false);
  Prop("Status","Two-part nominal cooling subassembly only. No O-rings, internal strip, fittings or fasteners included; unqualified for manufacture or operation.");
  Prop("Placement","Both native part origins aligned; shared mating plane X0. Fixed nominal placement, not mechanical assembly mates. Part01 remains unchanged.");
  Save(Path.Combine(folder,"F01 Cooling body and cover RevA.SLDASM"));Save(Path.Combine(folder,"F01 Cooling body and cover RevA.step"));
  Shot(Path.Combine(folder,"F01 cooling pair assembled.png"),"*Left",3,true);
  // Save a second native assembly showing the mating faces separated by 16 mm.
  var comp=(Component2)added[1];d.ClearSelection2(true);comp.Select4(false,null,false);assy.UnfixComponent();
  var tx=(double[])comp.Transform2.ArrayData;tx[9]=-.016;var math=(IMathUtility)sw.GetMathUtility();comp.Transform2=(MathTransform)math.CreateTransform(tx);d.ClearSelection2(true);d.ForceRebuild3(false);
  Save(Path.Combine(folder,"F01 Cooling pair exploded inspection.SLDASM"));Shot(Path.Combine(folder,"F01 cooling pair exploded.png"),"*Left",3,true);
 }
}
'@
[FreshCover02]::Run($PSScriptRoot)
