$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;
using System.IO;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public class AssignMaterials {
 public static void Run(string folder,string library) {
  ISldWorks sw;
  try { sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application"); }
  catch(COMException){ sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application")); }
  const int materialLocations=28;
  string existing=sw.GetUserPreferenceStringValue(materialLocations);
  if(Array.IndexOf(existing.Split(';'),folder)<0)
   sw.SetUserPreferenceStringValue(materialLocations,existing.TrimEnd(';')+";"+folder);
  var rows=new string[,] {
   {"101","AISI 304","304L stainless steel, with guard mounting bosses/taps"},
   {"105","Alumina","CFT05W0321 candidate, supplier dimensions and wet RF qualification open"},
   {"107","Copper","OFHC copper socket, purchased break envelope"},
   {"108","Copper","OFHC copper socket, purchased break envelope"},
   {"109","Copper","C10100 OFE copper, ground-side reducing transition"},
   {"110","Copper","C10100 OFE copper, live-side reducing transition"},
   {"202","Alumina","Electrical grade 99.5% alumina rod guide"},
   {"203","Alumina","Electrical grade 99.5% alumina, stepped structural carrier"},
   {"204","AISI 304","304L ground-side carrier keeper"},
   {"205","AISI Type 316L stainless steel","A4-80 M3 live retainer proposed, verify certified procurement and preload"},
   {"206","AISI Type 316L stainless steel","316L load spreading washers, lapped ceramic-side face"},
   {"207","AISI Type 316L stainless steel","A4-80 M3 ground keeper screw proposed"},
   {"301","Alumina","Nonmagnetic alumina magnet locator"},
   {"302","N42SH NdFeB (density only)","Axially magnetized N42SH annular center, pole toward yoke opposite to outer magnets"},
   {"303","N42SH NdFeB (density only)","Axially magnetized N42SH outer magnets, same polarity as each other"},
   {"304","AISI 1010 Steel, hot rolled bar","Low carbon magnetic steel, verify supplier B-H curve"},
   {"309","AISI Type 316L stainless steel","A4-80 M3 head screws proposed, verify copper thread engagement"},
   {"403","AISI Type 316L stainless steel","A4-80 M3 clamp screws proposed, verify copper thread engagement"},
   {"502","AISI 304","304L stainless steel weld seat"},
   {"503","AISI Type 316L stainless steel","A4-80 M3 shield screws proposed"},
   {"601","AISI 304","304L conductive power guard shell"},
   {"602","AISI 304","304L removable conductive rear guard cover"},
   {"603","Copper","C10100 OFE copper terminal socket envelope; supplier interface open"},
   {"604","PTFE (general)","Cable dielectric envelope, supplier assembly open"},
   {"605","Copper","Supplier cable center conductor envelope"},
   {"606","AISI Type 316L stainless steel","A4-80 M3 guard mounting screws proposed"},
   {"607","AISI Type 316L stainless steel","A4-80 M3 cover screws proposed"}
  };
  int n=0, assigned=0;
  foreach(string file in Directory.GetFiles(folder,"R08 *.SLDPRT")){
   string name=Path.GetFileName(file);
   if(name=="R08 306 Copper C-channel core.SLDPRT")continue;
   for(int i=0;i<rows.GetLength(0);i++){
    if(!name.StartsWith("R08 "+rows[i,0]+" ")) continue;
    int e=0,w=0;
    var doc=(IModelDoc2)sw.OpenDoc6(file,1,1,"",ref e,ref w);
    if(doc==null||e!=0)throw new Exception("Open failed "+name+" "+e);
    string material=rows[i,1];
    if(material!=""){
     var part=(IPartDoc)doc;
     string config=doc.ConfigurationManager.ActiveConfiguration.Name;
     part.SetMaterialPropertyName2(config,material.StartsWith("N42SH")?"Magnetron R08 materials":library,material);
     string database="";
     string readback=part.GetMaterialPropertyName2(config,out database);
     if(readback!=material && !material.StartsWith("N42SH"))throw new Exception("Assignment mismatch "+name+": "+readback);
     if(readback==material) assigned++; else Console.WriteLine("Custom database must be registered for "+name);
    }
    var props=doc.Extension.CustomPropertyManager[""];
    if(props.Add3("Engineering Material",30,rows[i,2],2)<0 || props.Add3("Material Status",30,"Provisional design selection",2)<0)
     throw new Exception("Property write failed "+name);
    if(!doc.Save3(1,ref e,ref w)||e!=0)throw new Exception("Save failed "+name+" "+e);
    Console.WriteLine(name+" | "+material+" | "+rows[i,2]);
    n++;
    break;
   }
  }
  Console.WriteLine("Verified "+assigned+" native assignments and "+n+" engineering material records");
 }
}
'@
[AssignMaterials]::Run((Join-Path $PSScriptRoot 'magnetron-cad-r08'),'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\lang\english\sldmaterials\solidworks materials.sldmat')




