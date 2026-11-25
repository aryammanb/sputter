param([string]$OutputDirectory = (Join-Path $PSScriptRoot 'magnetron-cad-r02'))
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
 static string Part(string name, double[,] profile, double[,] holes = null) {
  string path=Path.Combine(folder,name+".SLDPRT");
  if(File.Exists(path)) return path;
  var doc=(IModelDoc2)sw.NewDocument(Path.Combine(templates,"Part.PRTDOT"),0,0,0);
  if(doc==null) throw new Exception("Missing part template");
  try {
   var plane=(IFeature)doc.FirstFeature();
   while(plane!=null && plane.GetTypeName2()!="RefPlane") plane=(IFeature)plane.GetNextFeature();
   if(plane==null || !plane.Select2(false,0)) throw new Exception("Reference plane selection failed");
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
 static void Holes(IModelDoc2 doc,double[,] holes){
  doc.ClearSelection2(true);
  var plane=(IFeature)doc.FirstFeature();
  while(plane!=null && plane.Name!="Right Plane") plane=(IFeature)plane.GetNextFeature();
  if(plane==null || !plane.Select2(false,0)) throw new Exception("Right Plane unavailable");
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
  var cut=doc.FeatureManager.FeatureCut4(false,false,false,1,1,.4,.4,false,false,false,false,0,0,false,false,false,false,false,true,true,false,false,false,0,0,false,false);
  if(cut==null) throw new Exception("Hole cut failed in "+doc.GetTitle());
  cut.Name="Axial holes";
 }
 class Item {
  public string Path; public double X,Y,Z;
  public Item(string path,double x=0,double y=0,double z=0){Path=path; X=x; Y=y; Z=z;}
 }
 static Item At(string p,double x=0,double y=0,double z=0){return new Item(p,x,y,z);}
 static string Assembly(string name,params Item[] items){
  string path=Path.Combine(folder,name+".SLDASM");
  if(File.Exists(path)) return path;
  var doc=(IModelDoc2)sw.NewDocument(Path.Combine(templates,"Assembly.ASMDOT"),0,0,0);
  if(doc==null) throw new Exception("Assembly template unavailable");
  var assy=(IAssemblyDoc)doc;
  var math=(IMathUtility)sw.GetMathUtility();
  foreach(var i in items){
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
  foreach(string path in Directory.GetFiles(source,"*.SLDPRT")) { string dest=Path.Combine(vendor,"R02 "+Path.GetFileName(path)); if(!File.Exists(dest)) File.Copy(path,dest); }
  string[] originals=Directory.GetFiles(vendor,"*.SLDPRT");
  Array.Sort(originals,StringComparer.OrdinalIgnoreCase);

  var coolant=Pattern(2,14,2.6,Math.PI/8);
  var magnetHoles=Pattern(8,21,5.2);
  var headBolts=Pattern(3,29.4,1.65,Math.PI/2);
  var clampBolts=Pattern(3,29.4,1.65,-Math.PI/2);
  var plate=Part("101 NW100 mounting plate layout",Tube(13.7,25.7,65,11.1125),coolant);
  var stem=Part("102 Grounded stem weld tube",Tube(25.7,135.7,27,24));
  var fitting=Part("103 Coolant bulkhead reference",new double[,]{{-6,1.65},{13.7,1.65},{13.7,2.5},{1,2.5},{1,4.5},{-6,4.5}});
  var tube=Part("104 Coolant tube",Tube(13.7,158.7,2.25,1.65));
  var rod=Part("201 Copper power rod and socket",new double[,]{{50,3.25},{58,3.25},{58,0},{156.7,0},{156.7,3.35},{148.7,3.35},{148.7,3.2},{61,3.2},{61,5},{50,5}});
  var guide=Part("202 Ceramic rod guide",Tube(73,79,23.9,3.4),Pattern(2,14,4.5,Math.PI/8));
  var carrier=Part("203 Ceramic head carrier layout",Tube(135.7,143.7,27,11),coolant);
  var locator=Part("301 Nonmagnetic magnet locator 5 mm",Tube(143.7,148.7,30,9.2),Combine(magnetHoles,coolant));
  var center=Part("302 Center magnet annular layout",Tube(143.7,148.7,9,4.5));
  var magnet=Part("303 Outer magnet layout",Tube(143.7,148.7,5,0));
  var yoke=Part("304 Steel yoke",Tube(148.7,156.7,34.4,3.35),Combine(coolant,headBolts));
  var back=Part("305 Copper jacket backplate",Tube(156.7,159.7,34.4,0),Combine(coolant,headBolts));
  var inner=Part("306 Copper jacket inner wall",Tube(159.7,163.7,11,0));
  var outer=Part("307 Copper jacket outer wall",Tube(159.7,163.7,34.4,25),headBolts);
  var seat=Part("308 Copper target seat and jacket cover",Tube(163.7,168.7,34.4,0),Combine(headBolts,clampBolts));
  var target=Part("401 Aluminum target 2 inch",Tube(168.7,174.7,25.4,0));
  var ring=Part("402 Target clamp ring",new double[,]{{169.7,25.6},{174.7,25.6},{174.7,24},{176.7,24},{176.7,34.4},{169.7,34.4}},clampBolts);
  var clampScrew=Part("403 Target clamp screw envelope",new double[,]{{165,0},{179.4,0},{179.4,2.75},{176.7,2.75},{176.7,1.5},{165,1.5}});
  var headScrew=Part("309 Head attachment screw envelope",new double[,]{{146,0},{167.5,0},{167.5,1.5},{148.7,1.5},{148.7,2.75},{146,2.75}});
  var shield=Part("501 Grounded shield with inward lip",new double[,]{{135.7,36.4},{182.4,36.4},{182.4,23.4},{184.4,23.4},{184.4,39},{135.7,39}});
  var shoulder=Part("502 Grounded shield seat",Tube(133.7,135.7,39,27));
  var mount=Assembly("10 Mount and stem weldment",At(originals[3]),At(plate),At(stem),At(shoulder));
  var kf=Assembly("11 KF25 feedthrough hardware",At(originals[0]),At(originals[1]),At(originals[2]),At(originals[4]));
  var live=Assembly("20 Insulated power path",At(rod),At(guide),At(carrier));
  var plumbing=new System.Collections.Generic.List<Item>();
  for(int i=0;i<2;i++){ plumbing.Add(At(fitting,0,coolant[i,0],coolant[i,1])); plumbing.Add(At(tube,0,coolant[i,0],coolant[i,1])); }
  var cooling=Assembly("21 Coolant plumbing layout",plumbing.ToArray());
  var magItems=new System.Collections.Generic.List<Item>{At(locator),At(center),At(yoke)};
  for(int i=0;i<8;i++)magItems.Add(At(magnet,0,magnetHoles[i,0],magnetHoles[i,1]));
  var magnets=Assembly("30 Rear magnet pack",magItems.ToArray());
  var jacketItems=new System.Collections.Generic.List<Item>{At(back),At(inner),At(outer),At(seat)};
  for(int i=0;i<3;i++)jacketItems.Add(At(headScrew,0,headBolts[i,0],headBolts[i,1]));
  var jacket=Assembly("31 Copper cooling head layout",jacketItems.ToArray());
  var targetItems=new System.Collections.Generic.List<Item>{At(target),At(ring)};
  for(int i=0;i<3;i++)targetItems.Add(At(clampScrew,0,clampBolts[i,0],clampBolts[i,1]));
  var targetStack=Assembly("40 Target and clamp",targetItems.ToArray());
  Assembly("Magnetron gun R02",At(mount),At(kf),At(live),At(cooling),At(magnets),At(jacket),At(targetStack),At(shield));
 }
}
'@
[Magnetron]::Build($OutputDirectory,$templates,(Join-Path $PSScriptRoot 'kf25-cad-r01'))

