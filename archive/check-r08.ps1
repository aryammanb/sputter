$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;
using System.IO;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public class CheckAssembly {
 public static void Run(string file) {
  ISldWorks sw;
  try { sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application"); }
  catch(COMException){ sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application")); }
  int e=0,w=0;
  var doc=(IModelDoc2)sw.OpenDoc6(file,2,1,"",ref e,ref w);
  if(doc==null) throw new Exception("Open failed "+e);
  var asm=(IAssemblyDoc)doc; asm.ResolveAllLightWeightComponents(false);
  var items=(object[])asm.GetComponents(false);
  int missing=0, leaves=0;
  foreach(Component2 c in items){
   if(!File.Exists(c.GetPathName())) missing++;
   if(Path.GetExtension(c.GetPathName()).Equals(".SLDPRT",StringComparison.OrdinalIgnoreCase)) leaves++;
  }
  Console.WriteLine("open errors="+e+" warnings="+w+" top="+asm.GetComponentCount(true)+" instances="+items.Length+" parts="+leaves+" missing files="+missing);
  foreach(Component2 component in items){
   if(!component.Name2.Contains("C-channel core")) continue;
   object info;
   var bodies=(object[])component.GetBodies3(0,out info);
   double volume=0;
   foreach(Body2 body in bodies) volume+=((double[])body.GetMassProperties(1))[3]*1e9;
   Console.WriteLine("Channel core solid volume="+volume.ToString("F3")+" mm3");
   double expected=8355.795910;
   if(Math.Abs(volume-expected)>.1)throw new Exception("Channel volume mismatch: expected "+expected);
  }
  var mgr=asm.InterferenceDetectionManager;
  mgr.TreatCoincidenceAsInterference=false;
  mgr.TreatSubAssembliesAsComponents=false;
  var hits=mgr.GetInterferences() as object[];
  Console.WriteLine("Interferences="+(hits==null?0:hits.Length));
  if(hits!=null) foreach(Interference hit in hits){
   var names=new System.Collections.Generic.List<string>();
   foreach(Component2 component in (object[])hit.Components) names.Add(component.Name2);
   Console.WriteLine((hit.Volume*1e9).ToString("F3")+" mm3 "+string.Join(" | ",names.ToArray()));
  }
  if((hits!=null && hits.Length!=0)||e!=0||missing!=0||asm.GetComponentCount(true)!=9) throw new Exception("Reference check failed");
 }
}
'@
[CheckAssembly]::Run((Join-Path $PSScriptRoot 'magnetron-cad-r08\Magnetron gun R08.SLDASM'))




