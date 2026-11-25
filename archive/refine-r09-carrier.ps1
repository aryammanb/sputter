$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public class CloseReview {
 public static void Run(){
  var sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");
  object[] docs=sw.GetDocuments() as object[];
  var names=new System.Collections.Generic.List<string>();
  if(docs!=null)foreach(IModelDoc2 d in docs)if(d.GetPathName().Contains("magnetron-cad-r09"))names.Add(d.GetTitle());
  foreach(string name in names)sw.CloseDoc(name);
 }
}
'@
[CloseReview]::Run()
$src=Get-Content (Join-Path $PSScriptRoot 'build-magnetron-r09.ps1') -Raw
$src=$src.Replace('{135.7,9.5},{143.7,9.5}','{135.7,4.2},{143.7,4.2}')
Set-Content (Join-Path $PSScriptRoot 'build-magnetron-r09.ps1') $src
$part=Join-Path $PSScriptRoot 'magnetron-cad-r09/R09 203 Stepped alumina head carrier.SLDPRT'
Copy-Item -LiteralPath $part -Destination (Join-Path $PSScriptRoot '.r09-carrier-before.SLDPRT')
Remove-Item -LiteralPath $part
