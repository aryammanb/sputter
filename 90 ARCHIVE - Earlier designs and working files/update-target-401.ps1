$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;
using System.IO;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public class UpdateTarget401 {
 public static void Run(string folder){
  ISldWorks sw;try{sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");}catch(COMException){sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));}
  int e=0,w=0;string file=Path.Combine(folder,"R09 401 Aluminum target 2 inch.SLDPRT");
  string backup=Path.Combine(folder,"Review history");Directory.CreateDirectory(backup);
  string old=Path.Combine(backup,"401 before 3.175 mm thickness.SLDPRT");if(!File.Exists(old))File.Copy(file,old);
  var d=(IModelDoc2)sw.OpenDoc6(file,1,1,"",ref e,ref w);if(d==null||e!=0)throw new Exception("Open failed");
  sw.ActivateDoc3(d.GetTitle(),false,0,ref e);
  var feature=(IFeature)((IPartDoc)d).FeatureByName("Axial profile (mm)");
  if(feature==null)throw new Exception("Profile missing");
  var sk=(ISketch)feature.GetSpecificFeature2();
  d.ClearSelection2(true);feature.Select2(false,0);d.EditSketch();int changed=0;
  foreach(SketchPoint pt in (object[])sk.GetSketchPoints2())if(Math.Abs(pt.X-.1747)<1e-7){if(!pt.SetCoords(.171875,pt.Y,pt.Z))throw new Exception("Point update failed");changed++;}
  d.SketchManager.InsertSketch(true);d.ClearSelection2(true);d.ForceRebuild3(false);
  var bodies=(object[])((IPartDoc)d).GetBodies2(0,false);if(bodies.Length!=1)throw new Exception("Body count");
  double volume=((double[])((Body2)bodies[0]).GetMassProperties(1))[3]*1e9;
  double expected=Math.PI*25.4*25.4*3.175;
  if(Math.Abs(volume-expected)>.001)throw new Exception("Wrong volume: "+volume);
  d.Extension.CustomPropertyManager[""].Add3("User confirmed nominal size",30,"Diameter 2.000 inch (50.800 mm); thickness 0.125 inch (3.175 mm). Confirmed 2026-11-15. Material and tolerances not confirmed.",2);
  d.Extension.CustomPropertyManager[""].Add3("Procurement specification",30,"Aluminium sputtering target; 99.99% purity per supplier listing; diameter 2 inch; thickness 0.125 inch; quantity 1 per gun. Tolerances and certificate availability not stated.",2);
  d.Extension.CustomPropertyManager[""].Add3("Supplier",30,"Vritra Technologies",2);
  d.Extension.CustomPropertyManager[""].Add3("Supplier URL",30,"https://www.vritratech.com/store/product/aluminium-al-sputtering-target/",2);
  d.Extension.CustomPropertyManager[""].Add3("Supplier part number",30,"Not stated on product page",2);
  d.Extension.CustomPropertyManager[""].Add3("Material status",30,"1060 Alloy is a legacy CAD proxy only. Purchased target specification: 99.99% aluminum per Vritra listing.",2);
  d.Extension.CustomPropertyManager[""].Add3("Listed price 2026-11-15",30,"INR 8300 excluding GST; 18% GST; INR 9794 including GST; shipping unspecified.",2);
  d.Extension.CustomPropertyManager[""].Add3("Interface review status",30,"Existing R09 clamp is for former 6 mm target; 2.825 mm axial gap remains. Clamp redesign pending part-by-part review.",2);
  if(!d.Save3(1,ref e,ref w)||e!=0)throw new Exception("Save failed");
  Console.WriteLine("Changed profile points="+changed+"; target volume="+volume+" mm3; thickness verified=3.175 mm");
  d.ShowNamedView2("*Isometric",7);d.ViewZoomtofit2();d.GraphicsRedraw2();
  d.Extension.SaveAs(Path.Combine(folder,"401 target review.png"),0,1,null,ref e,ref w);
  foreach(string name in new[]{"R09 40 Target and clamp.SLDASM","Magnetron gun R09.SLDASM"}){
   var a=(IModelDoc2)sw.OpenDoc6(Path.Combine(folder,name),2,1,"",ref e,ref w);if(a==null)throw new Exception("Assembly open failed");
   a.ForceRebuild3(false);a.Extension.CustomPropertyManager[""].Add3("Target thickness revision",30,"401 is now 3.175 mm thick. Clamp adaptation pending; previous complete-assembly verification predates this change.",2);
   if(!a.Save3(1,ref e,ref w)||e!=0)throw new Exception("Assembly save failed");
  }
  sw.ActivateDoc3(d.GetTitle(),false,0,ref e);
 }
}
'@
[UpdateTarget401]::Run((Join-Path $PSScriptRoot 'magnetron-cad-r09'))

