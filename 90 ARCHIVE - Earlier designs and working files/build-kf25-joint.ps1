param([string]$OutputDirectory = (Join-Path $PSScriptRoot 'kf25-cad'))
$swDirectory = 'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS'
$templates = 'C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2021\templates'
$dll = Join-Path $swDirectory 'SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;
using System.IO;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public static class KfJoint {
 static ISldWorks sw;
 static string templates;
 static string folder;
 static void Save(IModelDoc2 doc, string path) {
  int errors=0,warnings=0;
  if (!doc.Extension.SaveAs(path,0,1,null,ref errors,ref warnings) || errors!=0)
   throw new Exception("Save failed: "+path+" ("+errors+")");
  Console.WriteLine(Path.GetFileName(path)+" warnings="+warnings);
 }
 static string Part(string name, double[,] profile) {
  var doc=(IModelDoc2)sw.NewDocument(Path.Combine(templates,"Part.PRTDOT"),0,0,0);
  if(doc==null) throw new Exception("Missing part template");
  string path=Path.Combine(folder,name+".SLDPRT");
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
   doc.ViewZoomtofit2();
   Save(doc,path);
   return path;
  } finally { sw.CloseDoc(doc.GetTitle()); }
 }
 public static void Build(string output, string templateDirectory) {
  sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");
  templates=templateDirectory;
  folder=output;
  Directory.CreateDirectory(folder);
  string[] paths={
   Part("01 Ceramaseal 16959-01-KF envelope",new double[,]{{-94,2.4},{58,2.4},{58,3.2},{13,3.2},{13,6},{0,6},{0,20},{-2,20},{-5,17},{-5,7.9},{-19,7.9},{-19,5.7},{-23,5.7},{-23,6.7},{-27,6.7},{-27,6.4},{-49,6.4},{-49,3.2},{-94,3.2}}),
   Part("02 KF25 centering ring envelope",new double[,]{{-2.4,11.1},{2.4,11.1},{2.4,12.9},{-2.4,12.9}}),
   Part("03 KF25 O-ring envelope",new double[,]{{-1,14.0},{1,14.0},{1,16.5},{-1,16.5}}),
   Part("04 KF25 mating stub",new double[,]{{1,11.1125},{13.7,11.1125},{13.7,12.7},{6,12.7},{6,17},{3,19.94},{1,19.94}}),
   Part("05 KF25 clamp envelope",new double[,]{{-5,17.1},{-2,20.1},{3,20.1},{6,17.1},{6,24},{-5,24}})
  };
  var assembly=(IModelDoc2)sw.NewDocument(Path.Combine(templates,"Assembly.ASMDOT"),0,0,0);
  if(assembly==null) throw new Exception("Missing assembly template");
  var assy=(IAssemblyDoc)assembly;
  var math=(IMathUtility)sw.GetMathUtility();
  foreach(string path in paths){
   int errors=0,warnings=0;
   var part=(IModelDoc2)sw.OpenDoc6(path,1,1,"",ref errors,ref warnings);
   if(part==null) throw new Exception("Could not open "+path);
   sw.ActivateDoc3(assembly.GetTitle(),false,0,ref errors);
   var component=assy.AddComponent5(path,0,"",false,"",0,0,0);
   if(component==null) throw new Exception("Could not insert "+path);
   component.Transform2=(MathTransform)math.CreateTransform(new double[]{1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0});
  }
  assembly.ForceRebuild3(false);
  assembly.ShowNamedView2("*Isometric",7);
  assembly.ViewZoomtofit2();
  Save(assembly,Path.Combine(folder,"KF25 joint R00.SLDASM"));
 }
}
'@
[KfJoint]::Build($OutputDirectory,$templates)

