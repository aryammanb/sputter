$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll,'System.Web.Extensions' -TypeDefinition @'
using System;using System.IO;using System.Text;using System.Collections.Generic;using System.Web.Script.Serialization;using SolidWorks.Interop.sldworks;
public class VerifyATPackage {
 public static void Run(string root){
  var sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));int e=0,w=0;
  string folder=Path.Combine(root,"SolidWorks delivery"),path=Path.Combine(folder,"Advanced Tinkering magnetron - full reconstruction.SLDASM");
  var d=(IModelDoc2)sw.OpenDoc6(path,2,3,"",ref e,ref w);if(d==null||e!=0)throw new Exception("Packaged root open error="+e+" warnings="+w);
  if(!String.Equals(d.GetPathName(),path,StringComparison.OrdinalIgnoreCase))throw new Exception("Wrong root document opened "+d.GetPathName());
  var a=(IAssemblyDoc)d;a.ResolveAllLightWeightComponents(false);int leaves=0;var native=new HashSet<string>(StringComparer.OrdinalIgnoreCase);var problems=new List<string>();
  foreach(Component2 c in (object[])a.GetComponents(false)){
   string p=c.GetPathName();native.Add(p);if(!File.Exists(p))problems.Add("Missing:"+p);if(!p.StartsWith(folder+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase))problems.Add("Outside delivery:"+p);
   if(p.EndsWith(".SLDPRT",StringComparison.OrdinalIgnoreCase)){leaves++;if(c.GetModelDoc2()==null)problems.Add("Unresolved:"+c.Name2);}
  }
  if(leaves!=120||problems.Count!=0)throw new Exception("Package reference failure leaves="+leaves+" "+String.Join(";",problems));
  var js=new JavaScriptSerializer();File.WriteAllText(Path.Combine(root,"package-verification.json"),js.Serialize(new {opened_root=path,leaf_instances=leaves,unique_referenced_native_documents=native.Count,missing_or_external_native_references=problems.Count,open_warnings=w}),Encoding.UTF8);
  Console.WriteLine("PASS: packaged root opened;120 leaf instances;all native component references resolve inside delivery folder.");
  sw.CloseDoc(d.GetTitle());
 }
}
'@
[VerifyATPackage]::Run($PSScriptRoot)
