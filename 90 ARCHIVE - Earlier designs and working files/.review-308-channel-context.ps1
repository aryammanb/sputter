$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;
using System.IO;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public class ReviewChannel306 {
 public static void Run(string folder){
  ISldWorks sw; try { sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application"); } catch(COMException) { sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application")); } int e=0,w=0;
  string file=Path.Combine(folder,"R09 306 Copper C-channel core revised.SLDPRT");
  var d=(IModelDoc2)sw.OpenDoc6(file,1,1,"",ref e,ref w);
  if(d==null||e!=0)throw new Exception("Open failed "+e);
  sw.ActivateDoc3(d.GetTitle(),false,0,ref e);
  var p=(IPartDoc)d;string db="";
  Console.WriteLine("Material="+p.GetMaterialPropertyName2(d.ConfigurationManager.ActiveConfiguration.Name,out db));
  var bodies=(object[])p.GetBodies2(0,false);Console.WriteLine("Solid bodies="+bodies.Length);
  foreach(Body2 b in bodies){
   Console.WriteLine("Volume mm3="+((double[])b.GetMassProperties(1))[3]*1e9);
   foreach(Face2 face in (object[])b.GetFaces()){
    var s=(Surface)face.GetSurface();
    if(s.IsCylinder())Console.WriteLine("Cylinder parameters (m): "+string.Join(",",(double[])s.CylinderParams));
    if(s.IsPlane())Console.WriteLine("Plane parameters (m): "+string.Join(",",(double[])s.PlaneParams));
   }
  }
  d.ShowNamedView2("*Right",4);d.ViewZoomtofit2();d.GraphicsRedraw2();
  Console.WriteLine("Image saved="+d.Extension.SaveAs(Path.Combine(folder,"308 cooling channel context.png"),0,1,null,ref e,ref w)+" error="+e);
 }
}
'@
[ReviewChannel306]::Run((Join-Path $PSScriptRoot 'magnetron-cad-r09'))


