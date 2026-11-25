param([string]$OutputDirectory = (Join-Path $PSScriptRoot 'magnetron-cad-r09'))
$ErrorActionPreference = 'Stop'
$swDirectory = 'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS'
$templates = 'C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2021\templates'
$dll = Join-Path $swDirectory 'SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;
using System.IO;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public static class SealClosure {
 static ISldWorks sw;
 static string templates;
 static string folder;
 static void Save(IModelDoc2 doc, string path) {
  int errors=0,warnings=0;
  if (!doc.Extension.SaveAs(path,0,1,null,ref errors,ref warnings) || errors!=0)
   throw new Exception("Save failed: "+path+" ("+errors+")");
  Console.WriteLine(Path.GetFileName(path)+" warnings="+warnings);
 }
 static string Part(string name, double[,] profile, double[,] holes = null, Action<IModelDoc2> detail = null) {
  string previous=Path.Combine(folder,name+".SLDPRT");
  string path=Path.Combine(folder,"R09 "+name+".SLDPRT");
  if(!File.Exists(path) && File.Exists(previous)) File.Copy(previous,path);
  if(File.Exists(path)) return path;
  var doc=(IModelDoc2)sw.NewDocument(Path.Combine(templates,"Part.PRTDOT"),0,0,0);
  if(doc==null) throw new Exception("Missing part template");
  try {
   var plane=(IFeature)doc.FirstFeature();
   while(plane!=null && plane.GetTypeName2()!="RefPlane") plane=(IFeature)plane.GetNextFeature();
   if(plane==null || (!plane.Select2(false,0) && !doc.Extension.SelectByID2(plane.Name,"PLANE",0,0,0,false,0,null,0))) throw new Exception("Reference plane selection failed for "+name+" / "+doc.GetTitle());
   var sketch=doc.SketchManager;
   sketch.InsertSketch(true);
   sketch.AddToDB=true;
   var axis=sketch.CreateCenterLine(-.110,0,0,.075,0,0);
   for(int i=0;i<profile.GetLength(0);i++){
    int j=(i+1)%profile.GetLength(0);
    sketch.CreateLine(profile[i,0]/1000,profile[i,1]/1000,0,profile[j,0]/1000,profile[j,1]/1000,0);
   }
   sketch.AddToDB=false;
   var profileFeature=(IFeature)sketch.ActiveSketch;
   sketch.InsertSketch(true);
   profileFeature.Name="Axial profile (mm)";
   doc.ClearSelection2(true);
   profileFeature.Select2(false,0);
   var selection=(SelectData)((ISelectionMgr)doc.SelectionManager).CreateSelectData();
   selection.Mark=16;
   axis.Select4(true,selection);
   var revolved=doc.FeatureManager.FeatureRevolve2(true,true,false,false,false,false,0,0,2*Math.PI,0,false,false,0,0,0,0,0,true,true,true);
   if(revolved==null) throw new Exception("Revolve failed: "+name);
   revolved.Name="Full revolution";
   doc.ClearSelection2(true);
   if(holes!=null) Holes(doc, holes);
   if(detail!=null) detail(doc);
   var props=doc.Extension.CustomPropertyManager[""];
   props.Add3("Release status",30,"DESIGN REVIEW ONLY - not released for manufacture",2);
   if(name.StartsWith("101")||name.StartsWith("204")||name.StartsWith("304")||name.StartsWith("308")||name.StartsWith("502")||name.StartsWith("601"))
    props.Add3("Thread intent",30,"M3 x 0.5 tapped holes represented by 2.5 mm pilot bores; screw overlaps are thread envelopes. See R09 review for locations and engagement. No modeled helical thread.",2);
   doc.ViewZoomtofit2();
   Save(doc,path);
   return path;
  } finally { sw.CloseDoc(doc.GetTitle()); }
 }
 static double[,] Tube(double a,double b,double r,double inner) {
  return new double[,]{{a,inner},{b,inner},{b,r},{a,r}};
 }
 static double[,] Pattern(int count,double radius,double hole,double phase=0) {
  var result=new double[count,3];
  for(int i=0;i<count;i++){
   double a=phase+i*2*Math.PI/count;
   result[i,0]=radius*Math.Cos(a); result[i,1]=radius*Math.Sin(a); result[i,2]=hole;
  }
  return result;
 }
 static double[,] Combine(params double[][,] sets){
  int count=0; foreach(var set in sets) count+=set.GetLength(0);
  var result=new double[count,3]; int row=0;
  foreach(var set in sets) for(int i=0;i<set.GetLength(0);i++,row++)
   for(int j=0;j<3;j++) result[row,j]=set[i,j];
  return result;
 }
 static void Holes(IModelDoc2 doc,double[,] holes,double from=0,double to=0){
  doc.ClearSelection2(true);
  var plane=(IFeature)doc.FirstFeature();
  while(plane!=null && plane.Name!="Right Plane") plane=(IFeature)plane.GetNextFeature();
  if(plane==null || (!plane.Select2(false,0) && !doc.Extension.SelectByID2("Right Plane","PLANE",0,0,0,false,0,null,0))) throw new Exception("Right Plane unavailable");
  var sk=doc.SketchManager; sk.InsertSketch(true); sk.AddToDB=true;
  var transform=(IMathTransform)sk.ActiveSketch.ModelToSketchTransform;
  var math=(IMathUtility)sw.GetMathUtility();
  for(int i=0;i<holes.GetLength(0);i++){
   var point=(IMathPoint)math.CreatePoint(new double[]{0,holes[i,0]/1000,holes[i,1]/1000});
   var p=(double[])((IMathPoint)point.MultiplyTransform((MathTransform)transform)).ArrayData;
   sk.CreateCircleByRadius(p[0],p[1],0,holes[i,2]/1000);
  }
  sk.AddToDB=false;
  var feature=(IFeature)sk.ActiveSketch; sk.InsertSketch(true);
  doc.ClearSelection2(true); feature.Select2(false,0);
  var cut=doc.FeatureManager.FeatureCut4(to!=0,false,true,to!=0?0:1,1,to!=0?(to-from)/1000:.4,.4,false,false,false,false,0,0,false,false,false,false,false,true,true,false,false,false,to!=0?3:0,from/1000,false,false);
  if(cut==null) throw new Exception("Hole cut failed in "+doc.GetTitle());
  cut.Name="Axial holes";
 }
 static void VentSlot(IModelDoc2 doc){
  doc.ClearSelection2(true);
  if(!doc.Extension.SelectByID2("Right Plane","PLANE",0,0,0,false,0,null,0))throw new Exception("Slot plane missing");
  var sk=doc.SketchManager;sk.InsertSketch(true);sk.AddToDB=true;
  var tx=(IMathTransform)sk.ActiveSketch.ModelToSketchTransform;var math=(IMathUtility)sw.GetMathUtility();
  var yz=new double[,]{{26.2,-.5},{35,-.5},{35,.5},{26.2,.5}};var points=new double[4][];
  for(int i=0;i<4;i++)points[i]=(double[])((IMathPoint)((IMathPoint)math.CreatePoint(new double[]{0,yz[i,0]/1000,yz[i,1]/1000})).MultiplyTransform((MathTransform)tx)).ArrayData;
  for(int i=0;i<4;i++){int j=(i+1)%4;sk.CreateLine(points[i][0],points[i][1],0,points[j][0],points[j][1],0);}
  sk.AddToDB=false;var f=(IFeature)sk.ActiveSketch;sk.InsertSketch(true);doc.ClearSelection2(true);f.Select2(false,0);
  var cut=doc.FeatureManager.FeatureCut4(true,false,true,0,1,.0005,.4,false,false,false,false,0,0,false,false,false,false,false,true,true,false,false,false,3,.1592,false,false);
  if(cut==null)throw new Exception("Vent slot failed");cut.Name="Dry interface vent - NOT a coolant passage";
 }
 static void Prop(IModelDoc2 d,string n,string v){d.Extension.CustomPropertyManager[""].Add3(n,30,v,2);}
 static IModelDoc2 Open(string p,int type){int e=0,w=0;var d=(IModelDoc2)sw.OpenDoc6(p,type,1,"",ref e,ref w);if(d==null||e!=0)throw new Exception("Open failed "+p);sw.ActivateDoc3(d.GetTitle(),false,0,ref e);return d;}
 static double Strip(double r){double z=.5;return z*Math.Sqrt(r*r-z*z)+r*r*Math.Asin(z/r);}
 public static void Run(string output,string templateDirectory){
  try{sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");}catch(COMException){sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));}
  folder=output;templates=templateDirectory;
  var ports=Combine(Pattern(1,13,2.30,Math.PI/8-.24),Pattern(1,13,2.30,Math.PI/8+.24));
  var holes=Combine(ports,Pattern(3,29.4,1.65,Math.PI/2));
  string name="305 Brazing-land rear closure";
  string path=Part(name,new double[,]{{156.7,0},{159.65,0},{159.65,26.2},{159.2,26.2},{159.2,27.2},{159.7,27.2},{159.7,34.4},{156.7,34.4}},holes,VentSlot);
  var doc=Open(path,1);var p=(IPartDoc)doc;
  p.SetMaterialPropertyName2(doc.ConfigurationManager.ActiveConfiguration.Name,@"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\lang\english\sldmaterials\solidworks materials.sldmat","Copper");
  var solids=(object[])p.GetBodies2(0,false);if(solids.Length!=1)throw new Exception("Rear closure must be one body");
  double volume=((double[])((Body2)solids[0]).GetMassProperties(1))[3]*1e9;
  double expected=Math.PI*(34.4*34.4*3-26.2*26.2*.05-(27.2*27.2-26.2*26.2)*.5-3*1.65*1.65*3-2*2.3*2.3*2.95)-.5*(Strip(34.4)-Strip(27.2));
  if(Math.Abs(volume-expected)>.005)throw new Exception("Closure volume mismatch "+volume+" expected "+expected);
  Prop(doc,"Joint design status","Proposed permanent vacuum-compatible brazed closure. Geometry is not a leak-tightness certification; filler, process, tolerances, pressure/temperature envelope and leak acceptance remain to be qualified.");
  Prop(doc,"Joint J1 face allowance","0.050 mm nominal ROOM-TEMPERATURE face gap: closure face X159.650 to body lands X159.700, inside radius26.2. Final clearance must be set for selected filler/process at brazing temperature.");
  Prop(doc,"Joint J1 required bonded lands","Continuous outer seal land radius25.0..26.2 (1.2 mm wide), central land radius0..10.4, and full divider. Keep outer dry mounting rim and vent groove unbrazed. Actual land width/strength requires process qualification.");
  Prop(doc,"Dry separation groove","Radius26.2..27.2, 1.0 mm radial width, 0.5 mm deep; floor X159.2. One 1.0 mm-wide radial vent to OD at +Y, Z=0. Open to chamber vacuum; NOT a secondary containment system.");
  Prop(doc,"Tube joints J2 J3","Two diameter4.60 through bores accept existing diameter4.50 tubes; nominal radial gap0.050 mm, insertion overlap2.950 mm. Continuous circumferential braze required at each tube. Tube sizes and joining clearances provisional.");
  Prop(doc,"Dry mounting holes","Three diameter3.30 through holes on diameter58.8 circle. Hole nearest edge radius27.75; dry groove outer radius27.2; nominal ligament0.55 mm. Screws do not create the coolant seal.");
  Prop(doc,"Fabrication sequence","Fixture for uniform gap; prevent filler entering ports, channel, groove and screw holes. Join and inspect copper jacket before magnets/ceramics. Check divider bypass separately from external leakage. Qualified hydraulic and helium test procedures required.");
  Save(doc,path);doc.ShowNamedView2("*Right",4);((IModelView)doc.ActiveView).RotateAboutCenter(.30,-.40);doc.ViewZoomtofit2();doc.GraphicsRedraw2();Save(doc,Path.Combine(folder,"305 proposed seal face.png"));
  var body=Open(Path.Combine(folder,"R09 308 Integral copper target seat and channel.SLDPRT"),1);
  Prop(body,"Rear closure interface revision","2026-11-15: mates with 305 Brazing-land rear closure. Proposed 0.050 mm face-braze allowance over central land, divider and continuous outer land radius25..26.2. Groove outside primary seal vents to vacuum. Not qualified until fabricated and tested.");
  int e=0,w=0;if(!body.Save3(1,ref e,ref w)||e!=0)throw new Exception("Body metadata save failed");
  string subpath=Path.Combine(folder,"R09 31 Copper cooling head layout.SLDASM"),toppath=Path.Combine(folder,"Magnetron gun R09.SLDASM");
  string history=Path.Combine(folder,"Review history");Directory.CreateDirectory(history);
  foreach(string f in new[]{subpath,toppath}){string backup=Path.Combine(history,"Before closure seal lands - "+Path.GetFileName(f));if(!File.Exists(backup))File.Copy(f,backup);}
  var sub=Open(subpath,2);var a=(IAssemblyDoc)sub;a.ResolveAllLightWeightComponents(false);
  foreach(Component2 c in (object[])a.GetComponents(true))if(c.GetPathName().EndsWith("R09 305 Copper jacket backplate.SLDPRT")){
   sub.ClearSelection2(true);c.Select4(false,null,false);if(!a.ReplaceComponents(path,"",false,false))throw new Exception("Closure replacement failed");break;
  }
  foreach(Component2 c in (object[])a.GetComponents(true)){sub.ClearSelection2(true);c.Select4(false,null,false);a.FixComponent();}
  sub.ClearSelection2(true);sub.ForceRebuild3(false);Prop(sub,"Coolant boundary status","305 closure now contains proposed face-braze allowance, dry vented groove and tube socket clearances. Pre-braze CAD includes intentional open gaps; no filler solids modeled. Not leak-tight as an unjoined assembly.");Save(sub,subpath);
  var top=Open(toppath,2);top.ForceRebuild3(false);Save(top,toppath);
  doc=Open(path,1);doc.ShowNamedView2("*Right",4);((IModelView)doc.ActiveView).RotateAboutCenter(.30,-.40);doc.ViewZoomtofit2();doc.GraphicsRedraw2();
  Console.WriteLine("PASS: new closure one body, volume="+volume.ToString("F6")+" mm3, expected="+expected.ToString("F6")+" mm3. Assembly updated. Proposed joints remain unqualified.");
 }

}
'@
[SealClosure]::Run($OutputDirectory,$templates)
