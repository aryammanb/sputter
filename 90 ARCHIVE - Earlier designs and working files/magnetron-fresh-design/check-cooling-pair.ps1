$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;using System.IO;using System.Runtime.InteropServices;using SolidWorks.Interop.sldworks;
public class CheckFreshPair {
 public static void Run(string folder){
  ISldWorks sw;try{sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");}catch(COMException){sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));}int e=0,w=0;
  string path=Path.Combine(folder,"F01 Cooling body and cover RevA.SLDASM");var d=(IModelDoc2)sw.OpenDoc6(path,2,1,"",ref e,ref w);if(d==null||e!=0)throw new Exception("Assembly open "+e);sw.ActivateDoc3(d.GetTitle(),false,0,ref e);
  var a=(IAssemblyDoc)d;a.ResolveAllLightWeightComponents(false);var components=(object[])a.GetComponents(true);if(components.Length!=2)throw new Exception("Count");
  foreach(Component2 c in components){var tx=(double[])c.Transform2.ArrayData;for(int k=9;k<12;k++)if(Math.Abs(tx[k])>1e-9)throw new Exception("Misplaced "+c.Name2);if(!File.Exists(c.GetPathName()))throw new Exception("Missing reference");}
  var mgr=a.InterferenceDetectionManager;mgr.TreatCoincidenceAsInterference=false;mgr.TreatSubAssembliesAsComponents=false;mgr.IgnoreHiddenBodies=false;var hits=mgr.GetInterferences() as object[];if(hits!=null&&hits.Length>0)throw new Exception("Unexpected interference "+hits.Length);
  mgr.Done();
  string report="Native two-part subassembly: PASS\r\nBoth component origins at zero: PASS\r\nReferenced files exist: PASS\r\nVolumetric interference (coincidence ignored): ZERO\r\n";
  foreach(Component2 c in components){var part=(IModelDoc2)c.GetModelDoc2();var bodies=(object[])((IPartDoc)part).GetBodies2(0,false);if(bodies.Length!=1)throw new Exception("Not one solid");report+=Path.GetFileName(c.GetPathName())+": one solid\r\n";}
  report+="O-rings, strip, fittings and fasteners are not modeled. No seal or pressure qualification performed.\r\n";
  File.WriteAllText(Path.Combine(folder,"Cooling pair fit checks.txt"),report);Console.WriteLine(report);
 }
}
'@
[CheckFreshPair]::Run($PSScriptRoot)
