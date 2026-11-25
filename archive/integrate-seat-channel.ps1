$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;
using System.IO;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public class IntegrateSeatChannel {
 static ISldWorks sw;
 static IModelDoc2 Open(string path,int type){int e=0,w=0;var d=(IModelDoc2)sw.OpenDoc6(path,type,1,"",ref e,ref w);if(d==null||e!=0)throw new Exception("Open failed "+path+" "+e);sw.ActivateDoc3(d.GetTitle(),false,0,ref e);return d;}
 static void Save(IModelDoc2 d,string path){int e=0,w=0;if(!d.Extension.SaveAs(path,0,1,null,ref e,ref w)||e!=0)throw new Exception("Save failed "+path+" "+e);}
 static void Shot(IModelDoc2 d,string folder,string name,string view,int id,bool tilt){
  int e=0;sw.ActivateDoc3(d.GetTitle(),false,0,ref e);d.ClearSelection2(true);d.ShowNamedView2(view,id);
  if(tilt)((IModelView)d.ActiveView).RotateAboutCenter(.35,-.45);
  d.ViewZoomtofit2();d.GraphicsRedraw2();Save(d,Path.Combine(folder,name));
 }
 public static void Run(string folder){
  try{sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");}catch(COMException){sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));}
  string output=Path.Combine(folder,"R09 308 Integral copper target seat and channel.SLDPRT");
  IModelDoc2 part;
  if(!File.Exists(output)){
   var seat=Open(Path.Combine(folder,"R09 308 Copper target seat and jacket cover.SLDPRT"),1);
   var seatBody=(Body2)((Body2)((object[])((IPartDoc)seat).GetBodies2(0,false))[0]).Copy();
   var core=Open(Path.Combine(folder,"R09 306 Copper C-channel core revised.SLDPRT"),1);
   var coreBody=(Body2)((Body2)((object[])((IPartDoc)core).GetBodies2(0,false))[0]).Copy();
   part=(IModelDoc2)sw.NewDocument(@"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2021\templates\Part.PRTDOT",0,0,0);
   if(part==null)throw new Exception("New part failed");
   var p=(IPartDoc)part;
   var f1=(Feature)p.CreateFeatureFromBody3(seatBody,false,0);if(f1==null)throw new Exception("Seat body transfer failed");f1.Name="Seat geometry - target face retained";
   var f2=(Feature)p.CreateFeatureFromBody3(coreBody,false,0);if(f2==null)throw new Exception("Core body transfer failed");f2.Name="Channel geometry - existing port alignment";
   var bodies=(object[])p.GetBodies2(0,false);
   Console.WriteLine("Transferred solid bodies="+bodies.Length);
   if(bodies.Length>1){
    part.ClearSelection2(true);foreach(Body2 b in bodies)b.Select(true,2);
    var joined=part.FeatureManager.InsertCombineFeature(15903,null,null);
    if(joined==null)throw new Exception("SolidWorks Boolean union failed");joined.Name="ONE PIECE copper body - no internal joining seam";
   }
   p.SetMaterialPropertyName2(part.ConfigurationManager.ActiveConfiguration.Name,@"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\lang\english\sldmaterials\solidworks materials.sldmat","Copper");
  }else part=Open(output,1);
  part.ForceRebuild3(false);
  var result=(object[])((IPartDoc)part).GetBodies2(0,false);if(result.Length!=1)throw new Exception("Must be exactly one solid");
  double volume=((double[])((Body2)result[0]).GetMassProperties(1))[3]*1e9;
  if(Math.Abs(volume-26796.70916701314)>.001)throw new Exception("Unexpected merged volume "+volume);
  double minX=1,maxX=-1,maxR=0;
  foreach(Face2 face in (object[])((Body2)result[0]).GetFaces()){
   var surface=(Surface)face.GetSurface();
   if(surface.IsPlane()){var a=(double[])surface.PlaneParams;if(Math.Abs(a[0])>.99){minX=Math.Min(minX,a[3]);maxX=Math.Max(maxX,a[3]);}}
   if(surface.IsCylinder()){var a=(double[])surface.CylinderParams;maxR=Math.Max(maxR,a[6]);}
  }
  if(Math.Abs(minX-.1597)>1e-8||Math.Abs(maxX-.1687)>1e-8||Math.Abs(maxR-.0344)>1e-8)throw new Exception("Envelope changed");
  var props=part.Extension.CustomPropertyManager[""];
  props.Add3("Description",30,"One-piece copper target seat with integral rear C-channel; replaces separate 306 and 308",2);
  props.Add3("BOM item",30,"308; make; quantity 1 per gun; 306 eliminated as separate component",2);
  props.Add3("Nominal dimensions",30,"OD 68.8 mm; total thickness 9 mm; rear channel 4 mm deep, radii 10.4 to 25 mm; remaining target-facing wall 5 mm; target seat X=168.7 mm",2);
  props.Add3("Fastener geometry",30,"Three rear head holes: diameter 3.3 clearance over rear 4 mm, then diameter 2.5 M3 pilot over front 5 mm. Three front clamp holes: diameter 2.5 M3 pilot 5 mm deep. Pattern diameter 58.8 mm. Helical threads not modeled.",2);
  props.Add3("Manufacturing intent",30,"Machine from ONE copper blank. Source-body and Combine features describe shape, not a two-piece manufacturing process. Rear backplate 305 remains separate and requires a qualified continuous seal including divider.",2);
  props.Add3("Release status",30,"Design review only. Copper grade, machining corner radii, joining details, dry-side screw venting, tolerances and clamp adaptation remain open.",2);
  Save(part,output);
  Shot(part,folder,"308 integral rear channel.png","*Left",3,true);
  Shot(part,folder,"308 integral rear face.png","*Left",3,false);
  Shot(part,folder,"308 integral target face.png","*Isometric",7,false);
  string history=Path.Combine(folder,"Review history");Directory.CreateDirectory(history);
  foreach(string name in new[]{"R09 31 Copper cooling head layout.SLDASM","Magnetron gun R09.SLDASM"}){
   string path=Path.Combine(folder,name),backup=Path.Combine(history,"Before integral seat - "+name);if(!File.Exists(backup))File.Copy(path,backup);
  }
  var sub=Open(Path.Combine(folder,"R09 31 Copper cooling head layout.SLDASM"),2);var assembly=(IAssemblyDoc)sub;
  assembly.ResolveAllLightWeightComponents(false);
  foreach(Component2 c in (object[])assembly.GetComponents(true))if(c.GetPathName().EndsWith("R09 308 Copper target seat and jacket cover.SLDPRT")){
   sub.ClearSelection2(true);c.Select4(false,null,false);
   if(!assembly.ReplaceComponents(output,"",false,false))throw new Exception("Replacement failed");break;
  }
  foreach(Component2 c in (object[])assembly.GetComponents(true))if(c.GetPathName().EndsWith("R09 306 Copper C-channel core revised.SLDPRT")){
   sub.ClearSelection2(true);c.Select4(false,null,false);if(!sub.Extension.DeleteSelection2(0))throw new Exception("Remove separate core failed");break;
  }
  foreach(Component2 c in (object[])assembly.GetComponents(true)){sub.ClearSelection2(true);c.Select4(false,null,false);assembly.FixComponent();}
  sub.ClearSelection2(true);sub.ForceRebuild3(false);if(assembly.GetComponentCount(true)!=5)throw new Exception("Cooling head must have five components");
  sub.Extension.CustomPropertyManager[""].Add3("Integrated body revision",30,"2026-11-15: separate 306 eliminated; integral 308 contains seat and channel in one solid",2);
  Save(sub,Path.Combine(folder,"R09 31 Copper cooling head layout.SLDASM"));
  var top=Open(Path.Combine(folder,"Magnetron gun R09.SLDASM"),2);((IAssemblyDoc)top).ShowExploded(false);top.ForceRebuild3(false);
  int leaves=0,integral=0,obsolete=0;
  foreach(Component2 c in (object[])((IAssemblyDoc)top).GetComponents(false)){
   if(c.GetPathName().EndsWith(".SLDPRT"))leaves++;
   if(c.GetPathName()==output)integral++;
   if(c.GetPathName().EndsWith("R09 306 Copper C-channel core revised.SLDPRT"))obsolete++;
  }
  if(leaves!=75||integral!=1||obsolete!=0)throw new Exception("Assembly references failed "+leaves+" "+integral+" "+obsolete);
  Save(top,Path.Combine(folder,"Magnetron gun R09.SLDASM"));
  Console.WriteLine("PASS: one solid, volume="+volume+" mm3; OD=68.8 mm; axial envelope 159.7..168.7 mm; assembly 75 leaf parts, one integral 308, no separate 306.");
  Shot(part,folder,"308 integral rear channel.png","*Left",3,true);
 }
}
'@
[IntegrateSeatChannel]::Run((Join-Path $PSScriptRoot 'magnetron-cad-r09'))
