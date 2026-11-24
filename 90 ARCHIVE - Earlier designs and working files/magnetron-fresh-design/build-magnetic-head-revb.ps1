$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;using System.IO;using System.Collections.Generic;using System.Runtime.InteropServices;using SolidWorks.Interop.sldworks;
public class FreshMagneticHeadB {
 static ISldWorks sw;static IModelDoc2 d;static string folder;static List<string> log=new List<string>();
 static string Template(string n){return @"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2021\templates\"+n;}
 static double[,] Pattern(int n,double r,double a){var p=new double[n,2];for(int i=0;i<n;i++){double t=(a+i*360.0/n)*Math.PI/180;p[i,0]=r*Math.Cos(t);p[i,1]=r*Math.Sin(t);}return p;}
 static double[,] ports=Pattern(2,26,30); // replaced explicitly below: +/-30 deg, not opposite.
 static double[,] poles=Pattern(6,20,0), bolts=Pattern(6,37,0), retainers=Pattern(3,28,60);
 static void Save(string p){int e=0,w=0;if(!d.Extension.SaveAs(p,0,1,null,ref e,ref w)||e!=0)throw new Exception("Save "+p+" error="+e);Console.WriteLine(Path.GetFileName(p)+" warnings="+w);}
 static void Prop(string k,string v){d.Extension.CustomPropertyManager[""].Add3(k,30,v,2);}
 static IFeature Sketch(){d.ClearSelection2(true);if(!d.Extension.SelectByID2("Right Plane","PLANE",0,0,0,false,0,null,0))throw new Exception("Right Plane");d.SketchManager.InsertSketch(true);d.SketchManager.AddToDB=true;return (IFeature)d.SketchManager.ActiveSketch;}
 static double[] P(double y,double z){var m=(IMathUtility)sw.GetMathUtility();return (double[])((IMathPoint)((IMathPoint)m.CreatePoint(new double[]{0,y/1000,z/1000})).MultiplyTransform((MathTransform)d.SketchManager.ActiveSketch.ModelToSketchTransform)).ArrayData;}
 static void Circle(double y,double z,double r){var p=P(y,z);d.SketchManager.CreateCircleByRadius(p[0],p[1],0,r/1000);}
 static void Circles(double[,] p,double r){for(int i=0;i<p.GetLength(0);i++)Circle(p[i,0],p[i,1],r);}
 static void Line(double a,double b,double c,double e){var p=P(a,b);var q=P(c,e);d.SketchManager.CreateLine(p[0],p[1],0,q[0],q[1],0);}
 static void Finish(IFeature sk,string name){d.SketchManager.AddToDB=false;d.SketchManager.InsertSketch(true);sk.Name=name+" sketch";d.ClearSelection2(true);sk.Select2(false,0);}
 static void Cut(IFeature sk,string name,double from,double depth){Finish(sk,name);var f=d.FeatureManager.FeatureCut4(true,false,true,0,1,depth/1000,.2,false,false,false,false,0,0,false,false,false,false,false,true,true,false,false,false,3,from/1000,false,false);if(f==null)throw new Exception("Cut "+name);f.Name=name;}
 static void Boss(IFeature sk,string name,double from,double length){Finish(sk,name);var f=d.FeatureManager.FeatureExtrusion2(true,false,false,0,0,length/1000,length/1000,false,false,false,false,0,0,false,false,false,false,true,true,true,3,from/1000,false);if(f==null)throw new Exception("Boss "+name);f.Name=name;}
 static void Blank(double[,] profile){
  d=(IModelDoc2)sw.NewDocument(Template("Part.PRTDOT"),0,0,0);if(d==null)throw new Exception("New part");int e=0;sw.ActivateDoc3(d.GetTitle(),false,0,ref e);
  IFeature pl=(IFeature)d.FirstFeature();while(pl!=null&&pl.GetTypeName2()!="RefPlane")pl=(IFeature)pl.GetNextFeature();if(pl==null||(!pl.Select2(false,0)&&!d.Extension.SelectByID2(pl.Name,"PLANE",0,0,0,false,0,null,0)))throw new Exception("Revolve plane");
  var s=d.SketchManager;s.InsertSketch(true);s.AddToDB=true;var axis=s.CreateCenterLine(-.06,0,0,.03,0,0);
  for(int i=0;i<profile.GetLength(0);i++){int j=(i+1)%profile.GetLength(0);s.CreateLine(profile[i,0]/1000,profile[i,1]/1000,0,profile[j,0]/1000,profile[j,1]/1000,0);}
  var sk=(IFeature)s.ActiveSketch;s.AddToDB=false;s.InsertSketch(true);sk.Name="Axial blank profile";d.ClearSelection2(true);sk.Select2(false,0);var sel=(SelectData)((ISelectionMgr)d.SelectionManager).CreateSelectData();sel.Mark=16;axis.Select4(true,sel);
  var f=d.FeatureManager.FeatureRevolve2(true,true,false,false,false,false,0,0,2*Math.PI,0,false,false,0,0,0,0,0,true,true,true);if(f==null)throw new Exception("Revolve");f.Name="Native revolved blank";
 }
 static void Disk(double a,double b,double r,double inner=0){Blank(new double[,]{{a,inner},{b,inner},{b,r},{a,r}});}
 static string EndPart(string name,string material,double[] color){
  Prop("Status","REV B CONCEPT - NOT RELEASED FOR MANUFACTURE. No field, pressure, thermal or electrical rating. Coordinate-defined native sketches; production detailing incomplete.");
  Prop("Specified material",material);d.MaterialPropertyValues=new double[]{color[0],color[1],color[2],.25,.7,.25,.35,0,0};d.ForceRebuild3(false);
  var bs=(object[])((IPartDoc)d).GetBodies2(0,false);if(bs==null||bs.Length!=1)throw new Exception(name+" not one solid");var b=(Body2)bs[0];double volume=((double[])b.GetMassProperties(1))[3]*1e9;
  log.Add(name+" | volume_mm3="+volume.ToString("F9")+" | box_m="+String.Join(",",(double[])b.GetBodyBox()));
  string path=Path.Combine(folder,name+".SLDPRT");d.ShowNamedView2("*Isometric",7);d.ViewZoomtofit2();Save(path);Save(Path.Combine(folder,name+".step"));return path;
 }
 static void Shot(string filename,string view,int id,double ry=0,double rz=0){d.ClearSelection2(true);d.ShowNamedView2(view,id);if(ry!=0||rz!=0)((IModelView)d.ActiveView).RotateAboutCenter(ry,rz);d.ViewZoomtofit2();d.GraphicsRedraw2();Save(Path.Combine(folder,filename));}
 static void Open(string path,int type){int e=0,w=0;d=(IModelDoc2)sw.OpenDoc6(path,type,1,"",ref e,ref w);if(d==null||e!=0)throw new Exception("Open "+path);sw.ActivateDoc3(d.GetTitle(),false,0,ref e);}
 class Item {public string Path;public double X,Y,Z;public Item(string p,double x=0,double y=0,double z=0){Path=p;X=x;Y=y;Z=z;}}
 static string Assembly(string name,List<Item> items){
  d=(IModelDoc2)sw.NewDocument(Template("Assembly.ASMDOT"),0,0,0);if(d==null)throw new Exception("New assembly");int e=0;sw.ActivateDoc3(d.GetTitle(),false,0,ref e);var a=(IAssemblyDoc)d;
  var paths=new string[items.Count];var systems=new string[items.Count];var tx=new double[items.Count*16];
  for(int i=0;i<items.Count;i++){paths[i]=items[i].Path;systems[i]="";foreach(int k in new[]{0,4,8,12})tx[i*16+k]=1;tx[i*16+9]=items[i].X/1000;tx[i*16+10]=items[i].Y/1000;tx[i*16+11]=items[i].Z/1000;}
  var added=(object[])a.AddComponents3(paths,tx,systems);if(added==null||added.Length!=items.Count)throw new Exception("Insertion count");foreach(Component2 c in added){d.ClearSelection2(true);c.Select4(false,null,false);a.FixComponent();}d.ClearSelection2(true);d.ForceRebuild3(false);
  Prop("Status","Nominal magnetic-head concept; fixed CAD placement, not complete mechanical mates. No O-rings, actual fittings, bolts or complete vacuum housing included.");
  var mgr=a.InterferenceDetectionManager;mgr.TreatCoincidenceAsInterference=false;mgr.TreatSubAssembliesAsComponents=false;mgr.IgnoreHiddenBodies=false;var hits=mgr.GetInterferences() as object[];
  if(hits!=null&&hits.Length>0){foreach(Interference hit in hits){var ns=new List<string>();foreach(Component2 c in (object[])hit.Components)ns.Add(c.Name2);Console.WriteLine("INTERFERENCE "+String.Join(" / ",ns));}throw new Exception(name+" interferences="+hits.Length);}mgr.Done();
  log.Add(name+" | components="+items.Count+" | volumetric_interferences=0 (coincidences ignored)");
  string path=Path.Combine(folder,name+".SLDASM");Save(path);Save(Path.Combine(folder,name+".step"));return path;
 }
 public static void Run(string output){
  folder=output;Directory.CreateDirectory(folder);ports=new double[,]{{26*Math.Cos(Math.PI/6),13},{26*Math.Cos(Math.PI/6),-13}};
  try{sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");}catch(COMException){sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));}
  // Body: annular water pocket with six integral dry islands, connected divider and blind dry wells.
  Blank(new double[,]{{0,0},{7,0},{7,41},{0,41},{0,29},{4,29},{4,10},{0,10}});
  var sk=Sketch();Circles(poles,7.5);Boss(sk,"Six integral dry magnet-well islands",0,4);
  sk=Sketch();Line(9,-3,30,-3);Line(30,-3,30,3);Line(30,3,9,3);Line(9,3,9,-3);Boss(sk,"Integral 6mm-wide channel divider",0,4);
  sk=Sketch();Circle(0,0,6.15);Circles(poles,4.15);Cut(sk,"Seven dry blind magnet wells depth4p5",0,4.5);
  sk=Sketch();Circle(0,0,6.75);Circle(0,0,8.75);Cut(sk,"Center-well ID14x1p5 face gland",0,1.15);
  for(int i=0;i<6;i++){sk=Sketch();Circle(poles[i,0],poles[i,1],4.75);Circle(poles[i,0],poles[i,1],6.75);Cut(sk,"Outer dry-well face gland "+(i+1),0,1.15);}
  sk=Sketch();Circle(0,0,30.7);Circle(0,0,33.3);Cut(sk,"Perimeter ID62x2 face gland",0,1.5);
  sk=Sketch();Circles(bolts,1.25);Cut(sk,"Six rear M3 pilot pockets PCD74",0,4);
  sk=Sketch();Circles(Pattern(3,37,30),1.25);Cut(sk,"Three independent target-clamp pilots PCD74",4,3);
  Prop("Magnet wells","Six diameter8.3 and central diameter12.3 blind bores, X0..4.5. Magnet tips X3: 1.5mm axial air gap. Minimum copper to target face at X7 is2.5mm; total pole-to-seat separation4mm.");
  Prop("Water separation","Annular rear pocket R10..29 depth4 with integral R7.5 dry islands at six R20 poles. Each dry well requires its own face O-ring at cover. 6mm-wide divider at +Y. Eight primary O-rings total: six ID10x1.5, one ID14x1.5, one ID62x2.");
  Prop("Divider","Metal-land contact only in RevB; no short cord strip assumed sealed. Internal bypass must be measured and controlled after flatness/deflection review. This is separate from external containment seals.");
  string body=EndPart("F01-001 Copper cooling body RevB","C110 copper candidate",new double[]{.83,.47,.25});Shot("RevB body dry wells and water pocket.png","*Left",3,.28,-.4);
  // Cover: open dry bores align with seven body wells; relocated ports avoid magnets.
  Disk(-3,0,41);sk=Sketch();Circles(ports,7);Boss(sk,"Relocated integral port bosses between magnets",-11,8);
  sk=Sketch();Circle(0,0,6.3);Circles(poles,4.3);Cut(sk,"Seven dry magnet passages through cover",-3,3);
  sk=Sketch();Circles(bolts,1.7);Cut(sk,"Six cover clearance holes PCD74",-3,3);
  sk=Sketch();Circles(ports,4.4);Cut(sk,"G1-8 tapping pilot envelopes depth7",-11,7);
  sk=Sketch();Circles(ports,2);Cut(sk,"Water ports diameter4 into coolant plenum",-11,11);
  Prop("Ports","Axes R26 at +/-30 degrees (Y22.5166605 Z+/-13). OD14 bosses. Proposed face-sealed G1/8 fitting pilot diameter8.8 depth7 and diameter4 passage. Threads, actual fittings, seal seats and ratings require supplier detail.");
  Prop("Sealing","Flat face X0 closes eight body glands. Dry pass-throughs diameter8.6 and12.6. No divider-strip pocket. Old RevA two-ring cover is superseded.");
  string cover=EndPart("F01-002 Coolant cover RevB","C110 copper candidate",new double[]{.25,.65,.62});Shot("RevB cover seven dry passages.png","*Left",3,.3,-.4);
  // Magnets: actual provisional sizes, reused as instances.
  Disk(-17,3,4);Prop("Magnetization","Axial +X-facing pole N for all six outer rods; center opposite. GradeN45 is reference only; choose final grade/coating using thermal and demagnetization data. No constitutive data assigned.");
  string outer=EndPart("F01-003 Outer magnet D8x20 candidate","NdFeB grade/coating not selected",new double[]{.85,.25,.25});
  Disk(-17,-7,6);Prop("Magnetization","Both stacked discs axially aligned; target-facing stack pole S, opposite outer rods. Second instance translated+10mm. GradeN45 reference only; not procurement release.");
  string center=EndPart("F01-004 Center magnet D12x10 candidate","NdFeB grade/coating not selected",new double[]{.25,.43,.85});
  // Yoke supports magnetic return and fixes rear pole plane.
  Disk(-22,-17,41);sk=Sketch();Circles(ports,8.25);Cut(sk,"Two fitting-route clearance bores diameter16p5",-22,5);
  sk=Sketch();Circles(Pattern(3,37,0),1.7);Cut(sk,"Three long mounting screw clearances",-22,5);
  sk=Sketch();Circles(retainers,.8);Cut(sk,"Three M2 locator receiving pilots depth3",-20,3);
  Prop("Magnetic intent","Low-carbon AISI1018 steel candidate,5mm thick. Contacts rear pole faces at X-17. Two diameter16.5 utility clearances. Permeability and saturation not simulated; thickness is provisional.");
  string yoke=EndPart("F01-005 Steel return yoke RevB","AISI1018 low-carbon steel candidate",new double[]{.40,.46,.53});
  // Rear locator positively guides magnet bases, located by three M2 screws to the yoke.
  Disk(-17,-14,32);sk=Sketch();Circle(0,0,6.15);Circles(poles,4.15);Cut(sk,"Magnet-base locator bores",-17,3);
  sk=Sketch();Circles(ports,8.25);Cut(sk,"Open fitting-route reliefs",-17,3);
  sk=Sketch();Circles(retainers,1.2);Cut(sk,"Three M2 locator clearance holes",-17,3);
  Prop("Retention","Three M2x5 screw intent into yoke pilots. Heads proud on front side X-14. Magnet holes diameter8.3 and12.3. Pocket-to-port thin ligaments require manufacturing review. Locator is dry, nonsealing, and not the main electrical isolation.");
  string locator=EndPart("F01-006 Dry magnet locator RevB","PEEK candidate",new double[]{.82,.77,.59});
  Disk(-17,-3,3,1.7);Prop("Fastening","Three14mm-long spacers on R37 at0,120,240deg. M3x25 screw intent:5mm yoke+14mm spacer+3mm cover+3mm nominal body engagement. Threads/runout and preload must be finalized. Magnetic poles are not the clamp load path.");
  string spacer=EndPart("F01-007 Yoke spacer L14 RevB","316L stainless candidate",new double[]{.65,.69,.73});
  Disk(-41,-11,8);Prop("Reference envelope","REFERENCE ONLY: diameter16 x30mm fitting/tube route, no selected fitting and no physical port detail. Used solely for reserved-volume collision checks. Must replace with actual fitting including wrench and hose bend envelope.");
  string utility=EndPart("REF Fitting route D16x30","Nonphysical clearance reservation",new double[]{.4,.5,.7});
  var items=new List<Item>{new Item(body),new Item(cover),new Item(yoke),new Item(locator),new Item(center),new Item(center,10)};
  for(int i=0;i<6;i++)items.Add(new Item(outer,0,poles[i,0],poles[i,1]));
  var st=Pattern(3,37,0);for(int i=0;i<3;i++)items.Add(new Item(spacer,0,st[i,0],st[i,1]));
  string assembly=Assembly("F01 Magnetic cooling head RevB",items);Shot("RevB magnetic head assembled.png","*Left",3,.35,-.55);
  var packing=new List<Item>(items);for(int i=0;i<2;i++)packing.Add(new Item(utility,0,ports[i,0],ports[i,1]));
  Assembly("F01 RevB utility clearance check",packing);
  var exploded=new List<Item>{new Item(body,45),new Item(cover,25),new Item(yoke,-22),new Item(locator,-10),new Item(center),new Item(center,10)};
  for(int i=0;i<6;i++)exploded.Add(new Item(outer,0,poles[i,0],poles[i,1]));for(int i=0;i<3;i++)exploded.Add(new Item(spacer,0,st[i,0],st[i,1]));
  Assembly("F01 RevB exploded inspection",exploded);Shot("RevB magnetic head exploded.png","*Left",3,.35,-.95);
  Open(assembly,2);Shot("RevB magnetic head assembled.png","*Left",3,.35,-.55);
  File.WriteAllLines(Path.Combine(folder,"RevB native geometry checks.txt"),log);
  Console.WriteLine("PASS: magnetic head15 physical candidate instances; utility check17 instances; zero nominal volumetric interferences. No pressure or field qualification.");
 }
}
'@
[FreshMagneticHeadB]::Run((Join-Path $PSScriptRoot 'RevB'))
