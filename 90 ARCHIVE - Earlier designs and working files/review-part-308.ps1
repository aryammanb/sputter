$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;
using System.IO;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public class ReviewSeat308 {
 public static void Run(string folder){
  ISldWorks sw; try { sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application"); } catch(COMException) { sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application")); } int e=0,w=0;
  string file=Path.Combine(folder,"R09 308 Copper target seat and jacket cover.SLDPRT");
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
  d.Extension.CustomPropertyManager[""].Add3("BOM make or buy",30,"Make; quantity 1 per gun; fabricator and copper grade TBD",2); d.Extension.CustomPropertyManager[""].Add3("Part review 2026-11-15",30,"Nominal geometry checked. See 308 part review.md. Joining process, tolerances, thread preload and clamp adaptation pending. Not released for manufacture.",2); if(!d.Save3(1,ref e,ref w)||e!=0)throw new Exception("Save failed"); d.ShowNamedView2("*Isometric",7);d.ViewZoomtofit2();d.GraphicsRedraw2();
  Console.WriteLine("Image saved="+d.Extension.SaveAs(Path.Combine(folder,"308 seat review.png"),0,1,null,ref e,ref w)+" error="+e);
 }
}
'@
[ReviewSeat308]::Run((Join-Path $PSScriptRoot 'magnetron-cad-r09'))



