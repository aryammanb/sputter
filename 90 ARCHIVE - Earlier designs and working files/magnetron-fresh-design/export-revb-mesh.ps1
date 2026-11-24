$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;using System.IO;using System.Collections.Generic;using System.Runtime.InteropServices;using SolidWorks.Interop.sldworks;
public class ExportRevBMesh {
 public static void Run(string folder){
 ISldWorks sw;try{sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");}catch(COMException){sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));}
 int e=0,w=0;var d=(IModelDoc2)sw.OpenDoc6(Path.Combine(folder,"F01 Magnetic cooling head RevB.SLDASM"),2,1,"",ref e,ref w);if(d==null||e!=0)throw new Exception("Assembly open");var a=(IAssemblyDoc)d;a.ResolveAllLightWeightComponents(false);
 int n=0;using(var writer=new BinaryWriter(File.Create(Path.Combine(folder,"actual-head-mesh.bin"))))
 foreach(Component2 c in (object[])a.GetComponents(true)){
  object info;var bs=(object[])c.GetBodies3(0,out info);if(bs==null)throw new Exception("Missing component bodies");var tx=(double[])c.GetTotalTransform(true).ArrayData;var coords=new List<float>();
  foreach(Body2 b in bs)foreach(Face2 f in (object[])b.GetFaces()){
   var triangles=f.GetTessTriangles(true) as float[];if(triangles==null)throw new Exception("No tessellation");
   for(int j=0;j<triangles.Length;j+=3){double x=triangles[j],y=triangles[j+1],z=triangles[j+2];for(int k=0;k<3;k++)coords.Add((float)(1000*(tx[k]*x+tx[3+k]*y+tx[6+k]*z+tx[9+k])));}
  }
  writer.Write(Path.GetFileName(c.GetPathName()));writer.Write(coords.Count/9);foreach(float v in coords)writer.Write(v);n++;
 }
 if(n!=15)throw new Exception("Instance count "+n);Console.WriteLine("Actual RevB CAD exported: "+n+" instances");
 }
}
'@
[ExportRevBMesh]::Run((Join-Path $PSScriptRoot 'RevB'))
