$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll,'System.Web.Extensions' -TypeDefinition @'
using System;using System.IO;using System.Linq;using System.Text;using System.Collections.Generic;using System.Runtime.InteropServices;using System.Web.Script.Serialization;using SolidWorks.Interop.sldworks;
public class IntegratedCoaxR02 {
 public class Item {public string name,path,step,kind,net;public double[] transform;}
 public class Part {public string name,step,net,note;public double volume_mm3;}
 public class Plan {public Item[] items;public Part[] parts;}
 static ISldWorks sw;static IModelDoc2 d;
 static void Save(string p){int e=0,w=0;if(!d.Extension.SaveAs(p,0,1,null,ref e,ref w)||e!=0)throw new Exception("Save "+p+" "+e);}
 public static void Run(string folder){
  var js=new JavaScriptSerializer();js.MaxJsonLength=10000000;var plan=js.Deserialize<Plan>(File.ReadAllText(Path.Combine(folder,"native-build-manifest.json")));string output=Path.Combine(folder,"SolidWorks delivery");Directory.CreateDirectory(output);
  try{sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");}catch(COMException){sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));}
  var imports=new List<object>();
  foreach(var part in plan.parts){
   string local=Path.Combine(output,Path.GetFileName(part.step));File.Copy(part.step,local,true);int e=0;
   d=(IModelDoc2)sw.LoadFile4(local,"r",null,ref e);if(d==null||e!=0)throw new Exception("Import "+part.name+" "+e);sw.ActivateDoc3(d.GetTitle(),false,0,ref e);
   d.Extension.CustomPropertyManager[""].Add3("Integration status",30,"R02 mechanical integration; electrical and thermal performance not qualified",2);d.Extension.CustomPropertyManager[""].Add3("Evidence and limits",30,part.note,2);d.Extension.CustomPropertyManager[""].Add3("Electrical node",30,part.net,2);
   double[] c=part.net=="live"?new double[]{.87,.50,.25}:part.net=="ground"?new double[]{.48,.62,.70}:part.net=="insulator"?new double[]{.91,.89,.77}:new double[]{.2,.23,.27};d.MaterialPropertyValues=new double[]{c[0],c[1],c[2],.3,.8,.2,.25,0,0};d.ForceRebuild3(false);
   var bs=(object[])((IPartDoc)d).GetBodies2(0,false);if(bs==null||bs.Length!=1)throw new Exception("Body count "+part.name);var b=(Body2)bs[0];double vol=((double[])b.GetMassProperties(1))[3]*1e9;if(b.Check()!=1)throw new Exception("Invalid body "+part.name);if(Math.Abs(vol-part.volume_mm3)>Math.Max(.01,part.volume_mm3*.0001))throw new Exception("Volume mismatch "+part.name);
   Save(Path.Combine(output,part.name+".SLDPRT"));imports.Add(new {part=part.name,volume_mm3=vol,body_check=b.Check(),box_m=(double[])b.GetBodyBox()});sw.CloseDoc(d.GetTitle());Console.WriteLine("Imported "+part.name);
  }
  d=(IModelDoc2)sw.NewDocument(@"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2021\templates\Assembly.ASMDOT",0,0,0);if(d==null)throw new Exception("Assembly");int ee=0;sw.ActivateDoc3(d.GetTitle(),false,0,ref ee);var a=(IAssemblyDoc)d;var tx=new double[16*plan.items.Length];for(int i=0;i<plan.items.Length;i++)Array.Copy(plan.items[i].transform,0,tx,16*i,16);
  var added=(object[])a.AddComponents3(plan.items.Select(q=>q.path).ToArray(),tx,plan.items.Select(q=>"").ToArray());if(added==null||added.Length!=plan.items.Length)throw new Exception("Insertion count");foreach(Component2 c in added){d.ClearSelection2(true);c.Select4(false,null,false);a.FixComponent();}d.ClearSelection2(true);d.ForceRebuild3(false);
  d.Extension.CustomPropertyManager[""].Add3("Design status",30,"Integrated single coax R02 - source hardware plus catalogue-size study components; not manufacturing release",2);d.Extension.CustomPropertyManager[""].Add3("Source preservation",30,"Original files unchanged. Boden pilot and service tube are separate revision parts. Old HV hook/lead and short terminal screw are replaced.",2);
  d.ShowNamedView2("*Isometric",7);d.ViewZoomtofit2();string assembly=Path.Combine(output,"Integrated single coax magnetron R02.SLDASM");Save(assembly);Save(Path.Combine(output,"Integrated single coax magnetron R02.step"));
  var components=new List<object>();using(var writer=new BinaryWriter(File.Create(Path.Combine(folder,"integrated-mesh.bin"))))foreach(Component2 c in added){
   if(!Path.GetDirectoryName(c.GetPathName()).Equals(output,StringComparison.OrdinalIgnoreCase))throw new Exception("External part reference "+c.GetPathName());object info;var bs=(object[])c.GetBodies3(0,out info);if(bs==null||bs.Length!=1)throw new Exception("Assembly body "+c.Name2);var t=(double[])c.GetTotalTransform(true).ArrayData;var coords=new List<float>();double vol=0;
   foreach(Body2 b in bs){if(b.Check()!=1)throw new Exception("Assembly invalid "+c.Name2);vol+=((double[])b.GetMassProperties(1))[3]*1e9;foreach(Face2 f in (object[])b.GetFaces()){var v=(float[])f.GetTessTriangles(true);if(v==null)throw new Exception("Missing tessellation "+c.Name2);for(int j=0;j<v.Length;j+=3)for(int k=0;k<3;k++)coords.Add((float)(1000*(t[k]*v[j]+t[3+k]*v[j+1]+t[6+k]*v[j+2]+t[9+k])));}}
   writer.Write(c.Name2);writer.Write(Path.GetFileName(c.GetPathName()));writer.Write(coords.Count/9);foreach(float v in coords)writer.Write(v);components.Add(new {name=c.Name2,path=c.GetPathName(),volume_mm3=vol,transform=t,triangles=coords.Count/9});
  }
  var mgr=a.InterferenceDetectionManager;mgr.TreatCoincidenceAsInterference=false;mgr.IgnoreHiddenBodies=false;var hits=mgr.GetInterferences() as object[];var collisions=new List<object>();if(hits!=null)foreach(Interference h in hits)collisions.Add(new {volume_mm3=h.Volume*1e9,parts=((object[])h.Components).Cast<Component2>().Select(c=>Path.GetFileName(c.GetPathName())).ToArray()});mgr.Done();
  File.WriteAllText(Path.Combine(folder,"native-verification.json"),js.Serialize(new {assembly=assembly,components=components,imports=imports,interferences=collisions}),Encoding.UTF8);Console.WriteLine("COMPLETE: "+components.Count+" components; "+collisions.Count+" raw interferences");
 }
}
'@
[IntegratedCoaxR02]::Run($PSScriptRoot)
