$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Collections.Generic;
using SolidWorks.Interop.sldworks;
public class FinalizeReview {
 public static void Run(string folder){
  var sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");
  int e=0,w=0;
  var paths=new List<string>(Directory.GetFiles(folder,"R09 *.SLDASM"));
  paths.Add(Path.Combine(folder,"Magnetron gun R09.SLDASM"));
  foreach(string path in paths){
   var d=(IModelDoc2)sw.OpenDoc6(path,2,1,"",ref e,ref w);
   sw.ActivateDoc3(d.GetTitle(),false,0,ref e);
   var a=(IAssemblyDoc)d;a.ResolveAllLightWeightComponents(false);
   foreach(Component2 c in (object[])a.GetComponents(true)){
    d.ClearSelection2(true);c.Select4(false,null,false);a.FixComponent();
   }
   d.ClearSelection2(true);
   d.Extension.CustomPropertyManager[""].Add3("Review status",30,"R09 design review - not released for manufacture. Components fixed at reviewed nominal locations; no kinematic mate validation.",2);
   d.ForceRebuild3(false);
   if(!d.Save3(1,ref e,ref w)||e!=0)throw new Exception("Save error "+path+" "+e);
   Console.WriteLine("Saved fixed review assembly: "+Path.GetFileName(path)+" warnings="+w);
  }
  var doc=(IModelDoc2)sw.ActiveDoc;
  var assy=(IAssemblyDoc)doc;
  var bom=new List<string>{"Group,Instance,File,Fixed"};
  foreach(Component2 c in (object[])assy.GetComponents(false))if(c.GetPathName().EndsWith(".SLDPRT"))
   bom.Add("\""+c.Name2.Split('/')[0]+"\",\""+c.Name2+"\",\""+c.GetPathName()+"\","+c.IsFixed());
  File.WriteAllLines(Path.Combine(folder,"R09 part instances.csv"),bom);
  if(assy.GetExplodedViewCount()==0){
   doc.ClearSelection2(true);
   doc.Extension.SelectByID2("Front Plane","PLANE",0,0,0,false,0,null,0);
   doc.Extension.SelectByID2("Top Plane","PLANE",0,0,0,true,0,null,0);
   if(!doc.InsertAxis2(true))throw new Exception("Explode axis failed");
   IFeature axis=null;
   for(var f=(IFeature)doc.FirstFeature();f!=null;f=(IFeature)f.GetNextFeature())if(f.GetTypeName2()=="RefAxis")axis=f;
   if(axis==null)throw new Exception("No reference axis");axis.Name="Review explosion axis";
   doc.ClearSelection2(true);
   if(!assy.CreateExplodedView())throw new Exception("Create exploded view failed");
   int i=0;
   foreach(Component2 c in (object[])assy.GetComponents(true)){
    string n=c.Name2;double distance=0;
    if(n.Contains("11 KF25"))distance=-.10;
    if(n.Contains("20 Power"))distance=.08;
    if(n.Contains("21 Coolant"))distance=.16;
    if(n.Contains("30 Rear"))distance=.24;
    if(n.Contains("31 Copper"))distance=.32;
    if(n.Contains("40 Target"))distance=.40;
    if(n.Contains("50 Removable"))distance=.48;
    if(n.Contains("60 Power"))distance=-.24;
    if(distance==0)continue;
    doc.ClearSelection2(true);c.SelectByMark(false,1);axis.Select2(true,2);
    int err=0;
    var step=(ExplodeStep)doc.ConfigurationManager.ActiveConfiguration.AddExplodeStep2(Math.Abs(distance),-1,distance<0,0,-1,false,false,false,out err);
    if(step==null)throw new Exception("Explode step failed "+n+" "+err);
    step.Name="Inspect "+n;i++;
   }
   Console.WriteLine("Native exploded view steps="+i);
   doc.ClearSelection2(true);assy.ShowExploded(false);
  }
  doc.ShowNamedView2("*Isometric",7);doc.ViewZoomtofit2();doc.GraphicsRedraw2();
  if(!doc.Save3(1,ref e,ref w)||e!=0)throw new Exception("Final save failed "+e);
  Console.WriteLine("Preview="+doc.Extension.SaveAs(Path.Combine(folder,"R09 SolidWorks assembly.png"),0,1,null,ref e,ref w)+" errors="+e);
 }
}
'@
[FinalizeReview]::Run((Join-Path $PSScriptRoot 'magnetron-cad-r09'))

