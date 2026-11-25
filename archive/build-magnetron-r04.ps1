param([string]$OutputDirectory = (Join-Path $PSScriptRoot 'magnetron-cad-r04'))
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
public static class Magnetron {
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
  string path=Path.Combine(folder,"R04 "+name+".SLDPRT");
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
 static void Channel(IModelDoc2 doc){
  doc.ClearSelection2(true);
  var plane=(IFeature)doc.FirstFeature();
  while(plane!=null && plane.Name!="Right Plane") plane=(IFeature)plane.GetNextFeature();
  if(plane==null || (!plane.Select2(false,0) && !doc.Extension.SelectByID2("Right Plane","PLANE",0,0,0,false,0,null,0))) throw new Exception("Right Plane unavailable");
  var sk=doc.SketchManager; sk.InsertSketch(true); sk.AddToDB=true;
  var tr=sk.ActiveSketch.ModelToSketchTransform;
  var mu=(IMathUtility)sw.GetMathUtility();
  Func<double,double,double[]> point=(r,theta)=>(double[])((IMathPoint)((IMathPoint)mu.CreatePoint(new double[]{0,r*Math.Cos(theta)/1000,r*Math.Sin(theta)/1000})).MultiplyTransform(tr)).ArrayData;
  const double start=Math.PI/8+.06;
  const double end=Math.PI/8+2*Math.PI-.06;
  var origin=point(0,0);
  var u=point(25,start); var v=point(25,end);
  var a=point(11,start); var b=point(11,end);
  var quarter=point(25,start+.1);
  short sense=(short)(u[0]*quarter[1]-u[1]*quarter[0]>0?1:-1);
  sk.CreateArc(origin[0],origin[1],0,u[0],u[1],0,v[0],v[1],0,sense);
  sk.CreateArc(origin[0],origin[1],0,a[0],a[1],0,b[0],b[1],0,sense);
  sk.CreateLine(u[0],u[1],0,a[0],a[1],0);
  sk.CreateLine(v[0],v[1],0,b[0],b[1],0);
  sk.AddToDB=false;
  var f=(IFeature)sk.ActiveSketch; sk.InsertSketch(true);
  doc.ClearSelection2(true); f.Select2(false,0);
  var cut=doc.FeatureManager.FeatureCut4(false,false,false,1,1,.4,.4,false,false,false,false,0,0,false,false,false,false,false,true,true,false,false,false,0,0,false,false);
  if(cut==null) throw new Exception("Coolant channel cut failed");
  cut.Name="C-shaped coolant passage and integral divider";
 }
 class Item {
  public string Path; public double X,Y,Z;
  public Item(string path,double x=0,double y=0,double z=0){Path=path; X=x; Y=y; Z=z;}
 }
 static Item At(string p,double x=0,double y=0,double z=0){return new Item(p,x,y,z);}
 static string Assembly(string name,params Item[] items){
  string path=Path.Combine(folder,(name.StartsWith("Magnetron")?name:"R04 "+name)+".SLDASM");
  if(File.Exists(path)) return path;
  var doc=(IModelDoc2)sw.NewDocument(Path.Combine(templates,"Assembly.ASMDOT"),0,0,0);
  if(doc==null) throw new Exception("Assembly template unavailable");
  var assy=(IAssemblyDoc)doc;
  var math=(IMathUtility)sw.GetMathUtility();
  if(name.StartsWith("Magnetron")){
   var paths=Array.ConvertAll(items, i=>i.Path);
   var systems=new string[items.Length];
   var transforms=new double[items.Length*16];
   for(int j=0;j<items.Length;j++){ systems[j]=""; foreach(int k in new[]{0,4,8,12}) transforms[16*j+k]=1; }
   var added=assy.AddComponents3(paths,transforms,systems) as object[];
   if(added==null || added.Length!=items.Length) throw new Exception("Batch insert incomplete");
  } else foreach(var i in items){
   int e=0,w=0;
   int type=Path.GetExtension(i.Path).Equals(".SLDASM",StringComparison.OrdinalIgnoreCase)?2:1;
   var componentDoc=(IModelDoc2)sw.OpenDoc6(i.Path,type,1,"",ref e,ref w);
   if(componentDoc==null) throw new Exception("Open failed "+i.Path+" "+e);
   sw.ActivateDoc3(doc.GetTitle(),false,0,ref e);
   var component=assy.AddComponent5(i.Path,0,"",false,"",0,0,0);
   if(component==null) throw new Exception("Insert failed "+i.Path);
   component.Transform2=(MathTransform)math.CreateTransform(new double[]{1,0,0,0,1,0,0,0,1,i.X/1000,i.Y/1000,i.Z/1000,1,0,0,0});
   doc.ClearSelection2(true);
   if(component.Select4(false,null,false)) assy.FixComponent();
   var actual=(double[])component.Transform2.ArrayData;
   if(Math.Abs(actual[9]-i.X/1000)+Math.Abs(actual[10]-i.Y/1000)+Math.Abs(actual[11]-i.Z/1000)>1e-7) throw new Exception("Placement failed "+i.Path);
  }
  doc.ForceRebuild3(false); doc.ShowNamedView2("*Isometric",7); doc.ViewZoomtofit2();
  Save(doc,path);
  Console.WriteLine(name+" top-level components="+assy.GetComponentCount(true));
  if(!name.StartsWith("Magnetron")) sw.CloseDoc(doc.GetTitle());
  return path;
 }
 public static void Build(string output,string templateDirectory,string source){
  try { sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application"); }
  catch(COMException) { sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application")); }
  templates=templateDirectory; folder=output; Directory.CreateDirectory(folder);
  string vendor=Path.Combine(folder,"Purchased component envelopes"); Directory.CreateDirectory(vendor);
  foreach(string path in Directory.GetFiles(source,"*.SLDPRT")) { string dest=Path.Combine(vendor,"R04 "+Path.GetFileName(path)); if(!File.Exists(dest)) File.Copy(path,dest); }
  string[] originals=Directory.GetFiles(vendor,"*.SLDPRT");
  Array.Sort(originals,StringComparer.OrdinalIgnoreCase);

  var coolant=Combine(Pattern(1,13,2.4,Math.PI/8-.24),Pattern(1,13,2.4,Math.PI/8+.24));
  var magnetHoles=Pattern(8,21,5.2);
  var headBolts=Pattern(3,29.4,1.65,Math.PI/2);
  var clampBolts=Pattern(3,29.4,1.65,-Math.PI/2);
  var externalPorts=Pattern(2,34,2.4);
  var plate=Part("101 R04 NW100 plate",Tube(13.7,25.7,65,11.1125),externalPorts);
  var stem=Part("102 Grounded stem weld tube",Tube(25.7,135.7,27,24));
  var fitting=Part("103 R04 Coolant bulkhead",new double[,]{{-6,1.65},{13.7,1.65},{13.7,2.35},{1,2.35},{1,4.5},{-6,4.5}});
  var tube=Part("104 Cathode coolant tube",Tube(118.7,159.7,2.25,1.65));
  var dielectric=Part("105 Dielectric coolant line envelope",Tube(49.7,118.7,2.25,1.65));
  var rod=Part("201 Copper power rod and socket",new double[,]{{50,3.25},{58,3.25},{58,0},{156.7,0},{156.7,3.35},{148.7,3.35},{148.7,3.2},{61,3.2},{61,5},{50,5}});
  var guide=Part("202 R04 Ceramic rod guide",Tube(73,79,23.9,3.4),coolant);
  var carrier=Part("203 R04 Ceramic head carrier",Tube(135.7,143.7,27,9.5),coolant);
  var locator=Part("301 Nonmagnetic magnet locator 5 mm",Tube(143.7,148.7,30,9.2),Combine(magnetHoles,coolant,Pattern(3,29.4,2.85,Math.PI/2)));
  var center=Part("302 Center magnet annular layout",Tube(143.7,148.7,9,4.5));
  var magnet=Part("303 Outer magnet layout",Tube(143.7,148.7,5,0));
  var yoke=Part("304 Steel yoke",Tube(148.7,156.7,34.4,3.35),Combine(coolant,headBolts));
  var back=Part("305 Copper jacket backplate",Tube(156.7,159.7,34.4,0),Combine(coolant,headBolts));
  var channel=Part("306 Copper C-channel core",Tube(159.7,163.7,34.4,0),headBolts,Channel);
  var seat=Part("308 Copper target seat and jacket cover",Tube(163.7,168.7,34.4,0),headBolts, doc=>Holes(doc,clampBolts,165.2,168.7));
  var target=Part("401 Aluminum target 2 inch",Tube(168.7,174.7,25.4,0));
  var ring=Part("402 Target clamp ring",new double[,]{{169.7,25.6},{174.7,25.6},{174.7,24},{176.7,24},{176.7,34.4},{169.7,34.4}},clampBolts,doc=>Holes(doc,Pattern(3,29.4,3,-Math.PI/2),174.0,176.7));
  var clampScrew=Part("403 Target clamp screw envelope",new double[,]{{165.5,0},{176.7,0},{176.7,2.75},{174,2.75},{174,1.5},{165.5,1.5}});
  var headScrew=Part("309 Head attachment screw envelope",new double[,]{{146,0},{167.5,0},{167.5,1.5},{148.7,1.5},{148.7,2.75},{146,2.75}});
  var shieldBolts=Pattern(3,40,1.65);
  var shield=Part("501 Grounded shield with inward lip",new double[,]{{135.7,36.4},{179.7,36.4},{179.7,23.4},{181.7,23.4},{181.7,39},{139.7,39},{139.7,43},{135.7,43}},shieldBolts);
  var shoulder=Part("502 Grounded shield seat",Tube(131.7,135.7,43,27),shieldBolts);
  var shieldScrew=Part("503 Shield screw envelope",new double[,]{{132,0},{142.4,0},{142.4,2.75},{139.7,2.75},{139.7,1.5},{132,1.5}});
  var mount=Assembly("10 Mount and stem weldment",At(originals[3]),At(plate),At(stem),At(shoulder));
  var kf=Assembly("11 KF25 feedthrough hardware",At(originals[0]),At(originals[1]),At(originals[2]),At(originals[4]));
  var live=Assembly("20 Insulated power path",At(rod),At(guide),At(carrier));
  var plumbing=new System.Collections.Generic.List<Item>();
  for(int i=0;i<2;i++){ plumbing.Add(At(fitting,0,externalPorts[i,0],externalPorts[i,1])); plumbing.Add(At(tube,0,coolant[i,0],coolant[i,1])); plumbing.Add(At(dielectric,0,coolant[i,0],coolant[i,1])); }
  var cooling=Assembly("21 Coolant plumbing layout",plumbing.ToArray());
  var magItems=new System.Collections.Generic.List<Item>{At(locator),At(center),At(yoke)};
  for(int i=0;i<8;i++)magItems.Add(At(magnet,0,magnetHoles[i,0],magnetHoles[i,1]));
  var magnets=Assembly("30 Rear magnet pack",magItems.ToArray());
  var jacketItems=new System.Collections.Generic.List<Item>{At(back),At(channel),At(seat)};
  for(int i=0;i<3;i++)jacketItems.Add(At(headScrew,0,headBolts[i,0],headBolts[i,1]));
  var jacket=Assembly("31 Copper cooling head layout",jacketItems.ToArray());
  var targetItems=new System.Collections.Generic.List<Item>{At(target),At(ring)};
  for(int i=0;i<3;i++)targetItems.Add(At(clampScrew,0,clampBolts[i,0],clampBolts[i,1]));
  var targetStack=Assembly("40 Target and clamp",targetItems.ToArray());
  var shItems=new System.Collections.Generic.List<Item>{At(shield)};
  for(int i=0;i<3;i++) shItems.Add(At(shieldScrew,0,shieldBolts[i,0],shieldBolts[i,1]));
  var shieldGroup=Assembly("50 Removable grounded shield",shItems.ToArray());
  Assembly("Magnetron gun R04",At(mount),At(kf),At(live),At(cooling),At(magnets),At(jacket),At(targetStack),At(shieldGroup));
 }
}
'@
[Magnetron]::Build($OutputDirectory,$templates,(Join-Path $PSScriptRoot 'kf25-cad-r01'))
