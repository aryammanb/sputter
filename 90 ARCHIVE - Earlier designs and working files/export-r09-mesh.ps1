$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;
using System.IO;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public class ExportGun {
 public static void Run(string input,string output){
 ISldWorks sw;
 try{sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");}
 catch(COMException){sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));}
 int e=0,w=0;
 var doc=(IModelDoc2)sw.OpenDoc6(input,2,1,"",ref e,ref w);
 if(doc==null||e!=0)throw new Exception("Open error "+e);
 var assy=(IAssemblyDoc)doc;
 assy.ResolveAllLightWeightComponents(false);
 var comps=(object[])assy.GetComponents(false);
 int count=0;
 using(var writer=new BinaryWriter(File.Create(output))){
 foreach(Component2 c in comps){
 if(!c.GetPathName().EndsWith(".SLDPRT",StringComparison.OrdinalIgnoreCase))continue;
 var bodies=c.GetBodies3(0,out varInfo) as object[];
 if(bodies==null)throw new Exception("No bodies "+c.Name2);
 var m=(double[])c.GetTotalTransform(true).ArrayData;
 var coords=new System.Collections.Generic.List<float>();
 foreach(Body2 body in bodies)
 foreach(Face2 f in (object[])body.GetFaces()){
 var ts=f.GetTessTriangles(true) as float[];
 if(ts==null||ts.Length==0)continue;
 for(int j=0;j<ts.Length;j+=3){
 double x=ts[j],y=ts[j+1],z=ts[j+2];
 for(int k=0;k<3;k++)coords.Add((float)(1000*(m[k]*x+m[3+k]*y+m[6+k]*z+m[9+k])));
 }
 }
 if(coords.Count==0)throw new Exception("No triangles "+c.Name2);
 writer.Write(c.Name2); writer.Write(coords.Count/9);
 foreach(float value in coords)writer.Write(value);
 count++;
 }}
 Console.WriteLine("Exported "+count+" native part instances");
 if(count!=75)throw new Exception("Expected 75 part instances");
 }
 static object varInfo;
}
'@
[ExportGun]::Run((Join-Path $PSScriptRoot 'magnetron-cad-r09\Magnetron gun R09.SLDASM'),(Join-Path $PSScriptRoot '.r09-mesh.bin'))



