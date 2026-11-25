$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public static class Preview {
 public static void Run(string folder) {
 ISldWorks sw; try{sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");}catch(COMException){sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));}
 int er=0,wa=0; var doc=(IModelDoc2)sw.OpenDoc6(System.IO.Path.Combine(folder,"Magnetron gun R08.SLDASM"),2,1,"",ref er,ref wa);
 var components=(object[])((IAssemblyDoc)doc).GetComponents(true);
 Console.WriteLine(doc.GetTitle()+" components="+components.Length);
 if(components.Length!=9)throw new Exception("Incorrect component count");
 foreach(Component2 c in components) { Console.WriteLine(c.Name2+" "+c.Visible+" "+string.Join(",", (double[])c.Transform2.ArrayData)+" box "+string.Join(",",(double[])c.GetBox(false,false))); } 
 doc.ShowNamedView2("*Isometric",7);
 doc.ViewZoomtofit2();
 doc.GraphicsRedraw2();
 int e=0,w=0;
 Console.WriteLine(doc.Extension.SaveAs(folder+"\\R08 assembly preview.png",0,1,null,ref e,ref w)+" errors="+e);
 }
}
'@
[Preview]::Run((Join-Path $PSScriptRoot 'magnetron-cad-r08'))

