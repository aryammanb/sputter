param([string]$PartName='F01-001 Copper cooling body RevA.SLDPRT',[string]$MeshName='part01-video-mesh.bin')
$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;
using System.IO;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public class ExportFreshVideo {
 public static void Run(string input,string output){
 ISldWorks sw;try{sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");}catch(COMException){sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));}int e=0,w=0;
 var doc=(IModelDoc2)sw.OpenDoc6(input,1,1,"",ref e,ref w);if(doc==null||e!=0)throw new Exception("Open error "+e);
 var bodies=(object[])((IPartDoc)doc).GetBodies2(0,false);if(bodies.Length!=1)throw new Exception("One solid required");int triangles=0,faces=0;
 using(var writer=new BinaryWriter(File.Create(output)))
 foreach(Face2 face in (object[])((Body2)bodies[0]).GetFaces()){
 var t=face.GetTessTriangles(true) as float[];if(t==null||t.Length==0)throw new Exception("Empty tessellation");
 var feature=(Feature)face.GetFeature();writer.Write(feature.Name);writer.Write(t.Length/9);
 foreach(float v in t)writer.Write(v*1000);triangles+=t.Length/9;faces++;
 }
 Console.WriteLine("Exported actual CAD: "+faces+" faces, "+triangles+" triangles");
 }
}
'@
[ExportFreshVideo]::Run((Join-Path $PSScriptRoot $PartName),(Join-Path $PSScriptRoot $MeshName))
