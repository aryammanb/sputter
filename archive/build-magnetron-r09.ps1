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
 class Item {
  public string Path; public double X,Y,Z;
  public Item(string path,double x=0,double y=0,double z=0){Path=path; X=x; Y=y; Z=z;}
 }
 static Item At(string p,double x=0,double y=0,double z=0){return new Item(p,x,y,z);}
 static string ImportSolid(string name,string step){
  string path=Path.Combine(folder,"R09 "+name+".SLDPRT");
  if(File.Exists(path))return path;
  int errors=0;
  var doc=(IModelDoc2)sw.LoadFile4(Path.Combine(folder,step),"r",null,ref errors);
  if(doc==null||errors!=0)throw new Exception("STEP import failed: "+step+" "+errors);
  try{ Save(doc,path); } finally { sw.CloseDoc(doc.GetTitle()); }
  return path;
 }
 static string Assembly(string name,params Item[] items){
  string path=Path.Combine(folder,(name.StartsWith("Magnetron")?name:"R09 "+name)+".SLDASM");
  if(File.Exists(path)) return path;
  var doc=(IModelDoc2)sw.NewDocument(Path.Combine(templates,"Assembly.ASMDOT"),0,0,0);
  if(doc==null) throw new Exception("Assembly template unavailable");
  var assy=(IAssemblyDoc)doc;
  var math=(IMathUtility)sw.GetMathUtility();
  {
   var paths=Array.ConvertAll(items, i=>i.Path);
   var systems=new string[items.Length];
   var transforms=new double[items.Length*16];
   for(int j=0;j<items.Length;j++){ systems[j]=""; foreach(int k in new[]{0,4,8,12}) transforms[16*j+k]=1; transforms[16*j+9]=items[j].X/1000; transforms[16*j+10]=items[j].Y/1000; transforms[16*j+11]=items[j].Z/1000; }
   var added=assy.AddComponents3(paths,transforms,systems) as object[];
   if(added==null || added.Length!=items.Length) throw new Exception("Batch insert incomplete");
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
  foreach(string path in Directory.GetFiles(source,"*.SLDPRT")) { string dest=Path.Combine(vendor,"R09 "+Path.GetFileName(path)); if(!File.Exists(dest)) File.Copy(path,dest); }
  string[] originals=Directory.GetFiles(vendor,"*.SLDPRT");
  Array.Sort(originals,StringComparer.OrdinalIgnoreCase);

  var coolant=Combine(Pattern(1,13,2.4,Math.PI/8-.24),Pattern(1,13,2.4,Math.PI/8+.24));
  var magnetHoles=Pattern(8,21,5.2);
  var headBolts=Pattern(3,29.4,1.65,Math.PI/2);
  var clampBolts=Pattern(3,29.4,1.65,-Math.PI/2);
  var externalPorts=Combine(Pattern(1,20.8,2.4,Math.PI/8-.24),Pattern(1,20.8,2.4,Math.PI/8+.24));
  
  var boxBolts=Pattern(4,45,1.65,Math.PI/4);
  var plate=Part("101 NW100 plate with power enclosure mounting",Tube(13.7,25.7,65,11.1125),externalPorts,
    doc=>Holes(doc,Pattern(4,45,1.25,Math.PI/4),13.7,20.7));
  var stem=Part("102 Grounded stem weld tube",Tube(25.7,135.7,27,24));
  var fitting=Part("103 R07 Coolant bulkhead",new double[,]{{8,1.65},{25.7,1.65},{25.7,2.35},{13.7,2.35},{13.7,4.5},{8,4.5}});
  var tube=Part("104 Cathode coolant tube",Tube(118.7,159.7,2.25,1.65));
  
  var ceramicBreak=Part("105 Alumina coolant break reserved envelope",Tube(73,97,7,2.4));
  var breakSocket=Part("107 OFHC coolant break socket envelope",new double[,]{
    {66,3.175},{71,3.175},{71,2.4},{73,2.4},{73,4.5},{66,4.5}});
  var breakSocketLive=Part("108 OFHC live coolant break socket envelope",new double[,]{
    {97,2.4},{99,2.4},{99,3.175},{104,3.175},{104,4.5},{97,4.5}});
  var widePorts=Combine(Pattern(1,15.5,7.25,Math.PI/8-.72),Pattern(1,15.5,7.25,Math.PI/8+.72));
  var rod=Part("201 Copper power rod and socket",new double[,]{{50,3.25},{58,3.25},{58,0},{156.7,0},{156.7,3.35},{148.7,3.35},{148.7,3.2},{61,3.2},{61,5},{50,5}});
  var guide=Part("202 Ceramic rod guide around ceramic breaks",Tube(80,86,23.9,3.4),widePorts);
  
  var ceramicBolts=Pattern(3,12,1.65,Math.PI/2);
  var keeperBolts=Pattern(3,32.5,1.65,Math.PI/3);
  var carrier=Part("203 Stepped alumina head carrier",new double[,]{
    {135.7,4.2},{143.7,4.2},{143.7,26.8},{139.7,26.8},{139.7,30},{135.7,30}},Combine(coolant,ceramicBolts));
  var keeper=Part("204 Grounded head carrier keeper",new double[,]{
    {135.7,30.25},{139.7,30.25},{139.7,27},{142.7,27},{142.7,35.5},{135.7,35.5}},Pattern(3,32.5,1.25,Math.PI/3));
  var liveScrew=Part("205 Live ceramic retention M3 screw",new double[,]{
    {131.5,0},{153.7,0},{153.7,1.5},{134.5,1.5},{134.5,2.75},{131.5,2.75}});
  var liveWasher=Part("206 Live ceramic load spreader",Tube(134.5,135.7,3.2,1.65));
  var groundScrew=Part("207 Ground keeper M3 screw",new double[,]{
    {128.7,0},{141.7,0},{141.7,1.5},{131.7,1.5},{131.7,2.75},{128.7,2.75}});
  var locator=Part("301 Nonmagnetic magnet locator 5 mm",Tube(143.7,148.7,30,9.2),Combine(magnetHoles,coolant,ceramicBolts,Pattern(3,29.4,2.85,Math.PI/2)));
  var center=Part("302 Center magnet annular layout",Tube(143.7,148.7,9,4.5));
  var magnet=Part("303 Outer magnet layout",Tube(143.7,148.7,5,0));
  var yoke=Part("304 Steel yoke",Tube(148.7,156.7,34.4,3.35),Combine(coolant,headBolts), doc=>Holes(doc,Pattern(3,12,1.25,Math.PI/2),148.7,154.7));
  var back=Path.Combine(folder,"R09 305 Brazing-land rear closure.SLDPRT");
  if(!File.Exists(back))throw new Exception("Run build-seal-closure.ps1 to create the current rear closure before rebuilding assemblies.");
  var seat=Path.Combine(folder,"R09 308 Integral copper target seat and channel.SLDPRT");
  if(!File.Exists(seat))throw new Exception("Run integrate-seat-channel.ps1 to create the current integral seat before rebuilding assemblies.");
  var target=Part("401 Aluminum target 2 inch",Tube(168.7,171.875,25.4,0));
  var ring=Part("402 Target clamp ring",new double[,]{{169.7,25.6},{174.7,25.6},{174.7,24},{176.7,24},{176.7,34.4},{169.7,34.4}},clampBolts,doc=>Holes(doc,Pattern(3,29.4,3,-Math.PI/2),174.0,176.7));
  var clampScrew=Part("403 Target clamp screw envelope",new double[,]{{165.5,0},{176.7,0},{176.7,2.75},{174,2.75},{174,1.5},{165.5,1.5}});
  var headScrew=Part("309 Head attachment screw envelope",new double[,]{{146,0},{167.5,0},{167.5,1.5},{148.7,1.5},{148.7,2.75},{146,2.75}});
  var shieldBolts=Pattern(3,42.2,1.65);
  var shield=Part("501 Grounded shield with inward lip",new double[,]{{135.7,36.4},{179.7,36.4},{179.7,23.4},{181.7,23.4},{181.7,39},{139.7,39},{139.7,46},{135.7,46}},shieldBolts);
  var shoulder=Part("502 Grounded shield seat",Tube(131.7,135.7,46,27),Combine(Pattern(3,42.2,1.25),keeperBolts));
  var shieldScrew=Part("503 Shield screw envelope",new double[,]{{132,0},{142.4,0},{142.4,2.75},{139.7,2.75},{139.7,1.5},{132,1.5}});
  var mount=Assembly("10 Mount and stem weldment",At(originals[3]),At(plate),At(stem),At(shoulder));
  var kf=Assembly("11 KF25 feedthrough hardware",At(originals[0]),At(originals[1]),At(originals[2]),At(originals[4]));
  
  var carrierItems=new System.Collections.Generic.List<Item>{At(rod),At(guide),At(carrier),At(keeper)};
  for(int i=0;i<3;i++){
   carrierItems.Add(At(liveScrew,0,ceramicBolts[i,0],ceramicBolts[i,1]));
   carrierItems.Add(At(liveWasher,0,ceramicBolts[i,0],ceramicBolts[i,1]));
   carrierItems.Add(At(groundScrew,0,keeperBolts[i,0],keeperBolts[i,1]));
  }
  var live=Assembly("20 Power path and ceramic head mounting",carrierItems.ToArray());
  var plumbing=new System.Collections.Generic.List<Item>();
  for(int i=0;i<2;i++){ plumbing.Add(At(fitting,0,externalPorts[i,0],externalPorts[i,1])); plumbing.Add(At(tube,0,coolant[i,0],coolant[i,1])); 
   for(int j=0;j<3;j++){
    var p=new[]{ceramicBreak,breakSocket,breakSocketLive}[j];
    plumbing.Add(At(p,0,widePorts[i,0],widePorts[i,1]));
   }
   plumbing.Add(At(ImportSolid("109 Ground to ceramic transition "+(i+1),"109-ground-"+(i+1)+".step")));
   plumbing.Add(At(ImportSolid("110 Ceramic to live transition "+(i+1),"110-live-"+(i+1)+".step"))); plumbing.Add(At(ImportSolid("106 Coolant transition "+(i+1),"106-transition-"+(i+1)+".step"))); }
  var cooling=Assembly("21 Coolant plumbing layout",plumbing.ToArray());
  var magItems=new System.Collections.Generic.List<Item>{At(locator),At(center),At(yoke)};
  for(int i=0;i<8;i++)magItems.Add(At(magnet,0,magnetHoles[i,0],magnetHoles[i,1]));
  var magnets=Assembly("30 Rear magnet pack",magItems.ToArray());
  var jacketItems=new System.Collections.Generic.List<Item>{At(back),At(seat)};
  for(int i=0;i<3;i++)jacketItems.Add(At(headScrew,0,headBolts[i,0],headBolts[i,1]));
  var jacket=Assembly("31 Copper cooling head layout",jacketItems.ToArray());
  var targetItems=new System.Collections.Generic.List<Item>{At(target),At(ring)};
  for(int i=0;i<3;i++)targetItems.Add(At(clampScrew,0,clampBolts[i,0],clampBolts[i,1]));
  var targetStack=Assembly("40 Target and clamp",targetItems.ToArray());
  var shItems=new System.Collections.Generic.List<Item>{At(shield)};
  for(int i=0;i<3;i++) shItems.Add(At(shieldScrew,0,shieldBolts[i,0],shieldBolts[i,1]));
  var shieldGroup=Assembly("50 Removable grounded shield",shItems.ToArray());
  
  var box=Part("601 Grounded power guard shell",new double[,]{
   {-126,49},{9.7,49},{9.7,32},{13.7,32},{13.7,55},{-126,55}},
   null,doc=>{Holes(doc,boxBolts,9.7,13.7); Holes(doc,Pattern(4,52,1.25),-126,-120);});
  var cover=Part("602 Power guard rear cover",Tube(-130,-126,55,8),Pattern(4,52,1.65));
  var collet=Part("603 Copper terminal socket envelope",new double[,]{
   {-103,0},{-94,0},{-94,3.2},{-83,3.2},{-83,5.5},{-103,5.5}});
  var insulated=Part("604 Supplier cable insulation envelope",Tube(-140,-103,7.5,2.5));
  var cable=Part("605 Cable live core envelope",Tube(-140,-103,2.5,0));
  var frontScrew=Part("606 Guard mounting M3 screw",new double[,]{
   {6.7,0},{19.7,0},{19.7,1.5},{9.7,1.5},{9.7,2.75},{6.7,2.75}});
  var coverScrew=Part("607 Guard cover M3 screw",new double[,]{
   {-133,0},{-121,0},{-121,1.5},{-130,1.5},{-130,2.75},{-133,2.75}});
  var guardItems=new System.Collections.Generic.List<Item>{At(box),At(cover),At(collet),At(insulated),At(cable)};
  var coverBolts=Pattern(4,52,1.65);
  for(int i=0;i<4;i++){
   guardItems.Add(At(frontScrew,0,boxBolts[i,0],boxBolts[i,1]));
   guardItems.Add(At(coverScrew,0,coverBolts[i,0],coverBolts[i,1]));
  }
  var guard=Assembly("60 Power termination guard",guardItems.ToArray());
  Assembly("Magnetron gun R09",At(mount),At(kf),At(live),At(cooling),At(magnets),At(jacket),At(targetStack),At(shieldGroup),At(guard));
 }
}
'@
[Magnetron]::Build($OutputDirectory,$templates,(Join-Path $PSScriptRoot 'kf25-cad-r01'))



