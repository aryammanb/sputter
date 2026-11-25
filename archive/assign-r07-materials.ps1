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
  var rows=new string[,] {
   {"101","AISI 304","304L stainless steel"},
   {"102","AISI 304","304L stainless steel"},
   {"103","AISI Type 316L stainless steel","316L stainless steel for weldable bulkhead"},
   {"104","Copper","Oxygen-free copper tube for brazed jacket joint"},
   {"106","AISI Type 316L stainless steel","316L stainless steel transition tube"},
   {"201","Copper","High-conductivity copper, verify socket contact and retention"},
   {"202","Alumina","Electrical-grade alumina, grade pending"},
   {"203","Alumina","Electrical-grade alumina, grade pending carrier retention design"},
   {"301","Alumina","Nonmagnetic alumina locator, provisional"},
   {"304","AISI 1010 Steel, hot rolled bar","Low-carbon magnetic steel, verify B-H curve"},
   {"305","Copper","Oxygen-free copper for vacuum brazing"},
   {"306","Copper","Oxygen-free copper for vacuum brazing"},
   {"308","Copper","Oxygen-free copper for vacuum brazing"},
   {"401","1060 Alloy","High-purity aluminum sputtering target, 1060 is a CAD proxy only"},
   {"402","AISI Type 316L stainless steel","316L stainless steel, verify clamp stiffness and deposition compatibility"},
   {"501","AISI 304","304L stainless steel"},
   {"502","AISI 304","304L stainless steel"},
   {"105","","Supplier-qualified dielectric liquid break, selection pending"},
   {"302","","Permanent magnet material and grade pending field design"},
   {"303","","Permanent magnet material and grade pending field design"},
   {"309","","Fastener material and grade pending procurement"},
   {"403","","Fastener material and grade pending procurement"},
   {"503","","Fastener material and grade pending procurement"}
  };
  int n=0, assigned=0;
  foreach(string file in Directory.GetFiles(folder,"R07 *.SLDPRT")){
   string name=Path.GetFileName(file);
   if(name=="R07 306 Copper C-channel core.SLDPRT")continue;
   for(int i=0;i<rows.GetLength(0);i++){
    if(!name.StartsWith("R07 "+rows[i,0]+" ")) continue;
    int e=0,w=0;
    var doc=(IModelDoc2)sw.OpenDoc6(file,1,1,"",ref e,ref w);
    if(doc==null||e!=0)throw new Exception("Open failed "+name+" "+e);
    string material=rows[i,1];
    if(material!=""){
     var part=(IPartDoc)doc;
     string config=doc.ConfigurationManager.ActiveConfiguration.Name;
     part.SetMaterialPropertyName2(config,library,material);
     string database="";
     string readback=part.GetMaterialPropertyName2(config,out database);
     if(readback!=material)throw new Exception("Assignment mismatch "+name+": "+readback);
     assigned++;
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
[AssignMaterials]::Run((Join-Path $PSScriptRoot 'magnetron-cad-r07'),'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\lang\english\sldmaterials\solidworks materials.sldmat')

