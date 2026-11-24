$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;
using System.IO;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public class FinalInspection {
 public static void Run(string root){
  var sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");int e=0,w=0;
  var d=(IModelDoc2)sw.OpenDoc6(Path.Combine(root,"Magnetron gun R09.SLDASM"),2,1,"",ref e,ref w);
  sw.ActivateDoc3(d.GetTitle(),false,0,ref e);var a=(IAssemblyDoc)d;
  int leaves=0,fixedCount=0;
  foreach(Component2 c in (object[])a.GetComponents(false))if(c.GetPathName().EndsWith(".SLDPRT")){
   leaves++;if(c.IsFixed())fixedCount++;
   if(!c.GetPathName().StartsWith(root,StringComparison.OrdinalIgnoreCase))throw new Exception("Reference outside R09: "+c.GetPathName());
  }
  int steps=d.ConfigurationManager.ActiveConfiguration.GetNumberOfExplodeSteps();
  for(int i=steps-1;i>=0;i--){
   var step=(ExplodeStep)d.ConfigurationManager.ActiveConfiguration.GetExplodeStep(i);
   Console.WriteLine("Step "+i+" "+step.Name+" components="+step.GetNumOfComponents());
   if(step.GetNumOfComponents()==0||step.Name=="Chain1")d.ConfigurationManager.ActiveConfiguration.DeleteExplodeStep(step.Name);
  }
  steps=d.ConfigurationManager.ActiveConfiguration.GetNumberOfExplodeSteps();
  if(leaves!=76||fixedCount!=76||steps!=8)throw new Exception("Count mismatch "+leaves+" "+fixedCount+" "+steps);
  Console.WriteLine("PASS: 76 fixed leaf instances, all CAD references within R09, 8 native explode steps");
  a.ShowExploded(true);d.ShowNamedView2("*Isometric",7);d.ViewZoomtofit2();d.GraphicsRedraw2();
  if(!d.Extension.SaveAs(Path.Combine(root,"R09 SolidWorks exploded.png"),0,1,null,ref e,ref w))throw new Exception("Exploded image save failed");
  a.ShowExploded(false);d.ViewZoomtofit2();
  d.Extension.CustomPropertyManager[""].Add3("Mechanical review report",30,Path.Combine(root,"R09 mechanical design review.md"),2);
  d.Extension.CustomPropertyManager[""].Add3("Open build blockers",30,"Power contacts; coolant joining and head removal; ceramic preload/tolerances; real purchased parts; flange and utility interfaces; standard fasteners; magnetic circuit verification.",2);
  if(!d.Save3(1,ref e,ref w)||e!=0)throw new Exception("Final save failed");
  Console.WriteLine("Saved collapsed assembly; native inspection explosion retained");
 }
}
'@
[FinalInspection]::Run((Join-Path $PSScriptRoot 'magnetron-cad-r09'))

