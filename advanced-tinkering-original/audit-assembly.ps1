$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll,'System.Web.Extensions' -TypeDefinition @'
using System;using System.IO;using System.Text;using System.Collections.Generic;using System.Web.Script.Serialization;using System.Runtime.InteropServices;using SolidWorks.Interop.sldworks;
public class AuditAT {
 public static void Run(string root){
  ISldWorks sw;try{sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");}catch(COMException){sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));}
  int e=0,w=0;var d=(IModelDoc2)sw.OpenDoc6(Path.Combine(root,"Advanced Tinkering magnetron - full reconstruction.SLDASM"),2,1,"",ref e,ref w);if(d==null||e!=0)throw new Exception("Assembly open "+e);sw.ActivateDoc3(d.GetTitle(),false,0,ref e);var a=(IAssemblyDoc)d;a.ResolveAllLightWeightComponents(false);d.ForceRebuild3(false);
  var records=new List<object>();int solids=0,leaves=0;
  foreach(Component2 c in (object[])a.GetComponents(false)){
   if(!c.GetPathName().EndsWith(".SLDPRT",StringComparison.OrdinalIgnoreCase))continue;leaves++;var part=(IModelDoc2)c.GetModelDoc2();if(part==null)throw new Exception("Missing "+c.Name2);var bs=(object[])((IPartDoc)part).GetBodies2(0,false);if(bs==null)throw new Exception("No bodies "+c.Name2);double v=0;var checks=new List<int>();foreach(Body2 b in bs){v+=((double[])b.GetMassProperties(1))[3]*1e9;checks.Add(b.Check());solids++;}
   records.Add(new {name=c.Name2,path=c.GetPathName(),solids=bs.Length,volume_mm3=v,body_check_return_codes=checks,transform=(double[])c.GetTotalTransform(true).ArrayData});
  }
  var mgr=a.InterferenceDetectionManager;mgr.TreatCoincidenceAsInterference=false;mgr.TreatSubAssembliesAsComponents=false;mgr.IgnoreHiddenBodies=false;var hits=mgr.GetInterferences() as object[];var collisions=new List<object>();
  if(hits!=null)foreach(Interference hit in hits){var names=new List<string>();var paths=new List<string>();foreach(Component2 c in (object[])hit.Components){names.Add(c.Name2);paths.Add(c.GetPathName());}collisions.Add(new {names=names,paths=paths,volume_mm3=hit.Volume*1e9,possible=hit.IsPossibleInterference,fastener=hit.IsFastener});}
  mgr.Done();var js=new JavaScriptSerializer();js.MaxJsonLength=10000000;File.WriteAllText(Path.Combine(root,"native-assembly-audit.json"),js.Serialize(new {leaves=leaves,solids=solids,components=records,interferences=collisions}),Encoding.UTF8);
  Console.WriteLine("Leaf instances="+leaves+" solids="+solids+" raw interference regions="+collisions.Count);Console.WriteLine("Saved native-assembly-audit.json");
 }
}
'@
[AuditAT]::Run($PSScriptRoot)
