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
  var sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");
  int e=0,w=0;
  var doc=(IModelDoc2)sw.OpenDoc6(file,2,1,"",ref e,ref w);
  if(doc==null) throw new Exception("Open failed "+e);
  var asm=(IAssemblyDoc)doc;
  var items=(object[])asm.GetComponents(false);
  int missing=0, leaves=0;
  foreach(Component2 c in items){
   if(!File.Exists(c.GetPathName())) missing++;
   if(Path.GetExtension(c.GetPathName()).Equals(".SLDPRT",StringComparison.OrdinalIgnoreCase)) leaves++;
  }
  Console.WriteLine("open errors="+e+" warnings="+w+" top="+asm.GetComponentCount(true)+" instances="+items.Length+" parts="+leaves+" missing files="+missing);
  if(e!=0||missing!=0||asm.GetComponentCount(true)!=8) throw new Exception("Reference check failed");
 }
}
'@
[CheckAssembly]::Run((Join-Path $PSScriptRoot 'magnetron-cad-r02\Magnetron gun R02.SLDASM'))
