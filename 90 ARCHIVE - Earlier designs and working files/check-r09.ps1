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
  int ae=0; sw.ActivateDoc3(doc.GetTitle(),false,0,ref ae); var asm=(IAssemblyDoc)doc; asm.ResolveAllLightWeightComponents(false);
  var items=(object[])asm.GetComponents(false);
  int missing=0, leaves=0;
  foreach(Component2 c in items){
   if(!File.Exists(c.GetPathName())) missing++;
   if(Path.GetExtension(c.GetPathName()).Equals(".SLDPRT",StringComparison.OrdinalIgnoreCase)) leaves++;
  }
  Console.WriteLine("open errors="+e+" warnings="+w+" top="+asm.GetComponentCount(true)+" instances="+items.Length+" parts="+leaves+" missing files="+missing);
  foreach(Component2 component in items){
   if(!component.GetPathName().Contains("308 Integral copper")) continue;
   object info;
   var bodies=(object[])component.GetBodies3(0,out info);
   double volume=0;
   foreach(Body2 body in bodies) volume+=((double[])body.GetMassProperties(1))[3]*1e9;
   Console.WriteLine("Integral seat/channel solid volume="+volume.ToString("F3")+" mm3");
   double expected=26796.709167;
   if(Math.Abs(volume-expected)>.1)throw new Exception("Channel volume mismatch: expected "+expected);
  }
  var mgr=asm.InterferenceDetectionManager;
  mgr.TreatCoincidenceAsInterference=false;
  mgr.TreatSubAssembliesAsComponents=false;
  mgr.IgnoreHiddenBodies=false; var hits=mgr.GetInterferences() as object[];
  Console.WriteLine("Interferences="+(hits==null?0:hits.Length));
  int verifiedThreads=0;
  var engagement=new System.Collections.Generic.Dictionary<string,double>{{"101/606",6},{"204/207",6},{"205/304",5},{"308/309",3.8},{"308/403",3.2},{"502/503",3.7},{"601/607",5}};
  if(hits!=null) foreach(Interference hit in hits){
   var names=new System.Collections.Generic.List<string>();
   var codes=new System.Collections.Generic.List<string>();
   foreach(Component2 component in (object[])hit.Components) {names.Add(component.Name2);codes.Add(Path.GetFileName(component.GetPathName()).Split(' ')[1]);}
   codes.Sort();string key=string.Join("/",codes.ToArray());
   if(!engagement.ContainsKey(key))throw new Exception("Unexpected interference: "+key);
   double expectedVolume=Math.PI*(1.5*1.5-1.25*1.25)*engagement[key];
   if(Math.Abs(hit.Volume*1e9-expectedVolume)>0.02)throw new Exception("Unexpected thread overlap volume: "+key);
   verifiedThreads++;
   Console.WriteLine((hit.Volume*1e9).ToString("F3")+" mm3 "+string.Join(" | ",names.ToArray()));
  }
  if(verifiedThreads!=23)throw new Exception("Expected exactly 23 verified thread-envelope overlaps");
  Console.WriteLine("PASS: 23 expected thread envelopes; no other reported volumetric interference");
  if(e!=0||missing!=0||asm.GetComponentCount(true)!=9||leaves!=75) throw new Exception("Reference check failed");
 }
}
'@
[CheckAssembly]::Run((Join-Path $PSScriptRoot 'magnetron-cad-r09\Magnetron gun R09.SLDASM'))






