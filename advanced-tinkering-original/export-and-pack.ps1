$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll,'System.Web.Extensions' -TypeDefinition @'
using System;using System.IO;using System.Text;using System.Collections.Generic;using System.Runtime.InteropServices;using System.Web.Script.Serialization;using SolidWorks.Interop.sldworks;
public class PackAT {
 public static void Run(string root){
  ISldWorks sw;try{sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");}catch(COMException){sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));}int e=0,w=0;
  string path=Path.Combine(root,"Advanced Tinkering magnetron - full reconstruction.SLDASM");var d=(IModelDoc2)sw.OpenDoc6(path,2,1,"",ref e,ref w);if(d==null||e!=0)throw new Exception("Open root "+e);sw.ActivateDoc3(d.GetTitle(),false,0,ref e);var a=(IAssemblyDoc)d;a.ResolveAllLightWeightComponents(false);d.ForceRebuild3(false);
  int count=0,triangles=0;using(var writer=new BinaryWriter(File.Create(Path.Combine(root,"actual-assembly-mesh.bin"))))
  foreach(Component2 c in (object[])a.GetComponents(false)){
   if(!c.GetPathName().EndsWith(".SLDPRT",StringComparison.OrdinalIgnoreCase))continue;object info;var bs=(object[])c.GetBodies3(0,out info);if(bs==null||bs.Length!=1)throw new Exception("Bodies "+c.Name2);var tx=(double[])c.GetTotalTransform(true).ArrayData;var coords=new List<float>();
   foreach(Body2 b in bs)foreach(Face2 face in (object[])b.GetFaces()){
    var t=face.GetTessTriangles(true) as float[];if(t==null||t.Length==0)throw new Exception("Tessellation "+c.Name2);
    for(int j=0;j<t.Length;j+=3){double x=t[j],y=t[j+1],z=t[j+2];for(int k=0;k<3;k++)coords.Add((float)(1000*(tx[k]*x+tx[3+k]*y+tx[6+k]*z+tx[9+k])));}
   }
   writer.Write(c.Name2);writer.Write(Path.GetFileName(c.GetPathName()));writer.Write(coords.Count/9);foreach(float p in coords)writer.Write(p);count++;triangles+=coords.Count/9;
  }
  if(count!=120)throw new Exception("Unexpected leaf count "+count);Console.WriteLine("Exported actual assembly mesh: "+count+" instances, "+triangles+" triangles");
  d.ShowNamedView2("*Isometric",7);d.ViewZoomtofit2();d.GraphicsRedraw2();if(!d.Save3(1,ref e,ref w)||e!=0)throw new Exception("Root resave");
  string delivery=Path.Combine(root,"SolidWorks delivery");Directory.CreateDirectory(delivery);
  var pg=(PackAndGo)d.Extension.GetPackAndGo();pg.IncludeDrawings=false;pg.IncludeSimulationResults=false;pg.IncludeToolboxComponents=true;pg.IncludeSuppressed=true;pg.FlattenToSingleFolder=true;
  if(!pg.SetSaveToName(true,delivery))throw new Exception("Pack and Go destination");var status=(int[])d.Extension.SavePackAndGo(pg);if(status==null)throw new Exception("Pack and Go did not return status");foreach(int s in status)if(s!=0)throw new Exception("Pack and Go save status "+s);
  File.Copy(Path.Combine(root,"Advanced Tinkering magnetron - full reconstruction.step"),Path.Combine(delivery,"Advanced Tinkering magnetron - full reconstruction.step"),true);
  var js=new JavaScriptSerializer();File.WriteAllText(Path.Combine(root,"pack-and-go-status.json"),js.Serialize(new {folder=delivery,statuses=status,leaf_instances=count,triangles=triangles}),Encoding.UTF8);
  Console.WriteLine("Pack and Go complete: "+status.Length+" native documents -> "+delivery);
 }
}
'@
[PackAT]::Run($PSScriptRoot)
