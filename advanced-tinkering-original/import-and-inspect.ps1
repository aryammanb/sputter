$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;using System.IO;using System.Text;using System.Collections.Generic;using System.Globalization;using System.Runtime.InteropServices;using SolidWorks.Interop.sldworks;
public class InspectAT {
 static string Vec(double[] a){var v=new List<string>();foreach(double d in a)v.Add(d.ToString("R",CultureInfo.InvariantCulture));return "["+String.Join(",",v)+"]";}
 public static void Run(string folder,string downloads){
  Directory.CreateDirectory(folder);Directory.CreateDirectory(Path.Combine(folder,"source"));Directory.CreateDirectory(Path.Combine(folder,"parts"));
  ISldWorks sw;try{sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");}catch(COMException){sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));}
  string[] names={"Dunkelraumabschirmung","Groundshield Rohr","Magnet Joke","Target Klemme","Abstandshalter","Boden","Flanschklemme","Isolator","Kuehlkoerper","Backplate"};
  var records=new List<string>();
  foreach(string n in names){
   string src=Path.Combine(downloads,n+".step"),copy=Path.Combine(folder,"source",n+".step"),native=Path.Combine(folder,"parts",n+".SLDPRT");
   if(!File.Exists(copy))File.Copy(src,copy);int e=0,w=0;IModelDoc2 d;
   if(File.Exists(native))d=(IModelDoc2)sw.OpenDoc6(native,1,1,"",ref e,ref w);else d=(IModelDoc2)sw.LoadFile4(copy,"r",null,ref e);
   if(d==null||e!=0)throw new Exception("Import "+n+" error="+e);sw.ActivateDoc3(d.GetTitle(),false,0,ref e);d.ForceRebuild3(false);
   var bs=(object[])((IPartDoc)d).GetBodies2(0,false);if(bs==null)throw new Exception("No solids "+n);
   var bodies=new List<string>();int bi=0;double total=0;
   foreach(Body2 b in bs){double vol=((double[])b.GetMassProperties(1))[3];total+=vol;var faces=new List<string>();int fi=0;
    foreach(Face2 f in (object[])b.GetFaces()){
     var s=(Surface)f.GetSurface();string kind="other",data="[]";
     if(s.IsCylinder()){kind="cylinder";data=Vec((double[])s.CylinderParams);}else if(s.IsPlane()){kind="plane";data=Vec((double[])s.PlaneParams);}
     faces.Add("{\"id\":"+(fi++)+",\"kind\":\""+kind+"\",\"area_m2\":"+f.GetArea().ToString("R",CultureInfo.InvariantCulture)+",\"params\":"+data+",\"box_m\":"+Vec((double[])f.GetBox())+"}");
    }
    bodies.Add("{\"id\":"+(bi++)+",\"name\":\""+b.Name+"\",\"volume_m3\":"+vol.ToString("R",CultureInfo.InvariantCulture)+",\"box_m\":"+Vec((double[])b.GetBodyBox())+",\"faces\":["+String.Join(",",faces)+"]}");
   }
   var props=d.Extension.CustomPropertyManager[""];props.Add3("Source",30,"Advanced Tinkering supplied original STEP: "+n+".step",2);props.Add3("Reconstruction status",30,"Original STEP geometry preserved. Assembly placement to be established from geometric interfaces and source video.",2);
   if(!d.Extension.SaveAs(native,0,1,null,ref e,ref w)||e!=0)throw new Exception("Save "+n+" error="+e);
   records.Add("{\"name\":\""+n+"\",\"bodies\":["+String.Join(",",bodies)+"]}");
   Console.WriteLine(n+" solids="+bs.Length+" volume_mm3="+(total*1e9).ToString("F3",CultureInfo.InvariantCulture));
   sw.CloseDoc(d.GetTitle());
  }
  File.WriteAllText(Path.Combine(folder,"original-geometry.json"),"["+String.Join(",",records)+"]",Encoding.UTF8);
 }
}
'@
[InspectAT]::Run($PSScriptRoot,'C:\Users\Aryamman\Downloads')
