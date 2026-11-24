$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public static class CadProbe {
 public static string Save(string path) {
  var app = (ISldWorks)Marshal.GetActiveObject("SldWorks.Application");
  var doc = (IModelDoc2)app.NewDocument(@"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2021\templates\Part.PRTDOT",0,0,0);
  if(doc == null) throw new Exception("No part created");
  int errors=0,warnings=0;
  bool ok=doc.Extension.SaveAs(path,0,1,null,ref errors,ref warnings);
  app.CloseDoc(doc.GetTitle());
  return ok+" errors="+errors+" warnings="+warnings;
 }
}
'@
[CadProbe]::Save('C:\Users\Aryamman\Documents\ChatGPT\sputter\sw-api-probe.sldprt')

