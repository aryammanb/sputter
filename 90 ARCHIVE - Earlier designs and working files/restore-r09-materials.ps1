$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;
using System.IO;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public class RestoreReviewMaterials {
 public static void Run(string root){
  var sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");
  foreach(string code in new[]{"101","203","204","304","308","501","502","601"}){
   int e=0,w=0;
   string src=Directory.GetFiles(Path.Combine(root,"magnetron-cad-r08"),"R08 "+code+" *.SLDPRT")[0];
   string dst=Directory.GetFiles(Path.Combine(root,"magnetron-cad-r09"),"R09 "+code+" *.SLDPRT")[0];
   var old=(IModelDoc2)sw.OpenDoc6(src,1,1,"",ref e,ref w);
   string db="";string mat=((IPartDoc)old).GetMaterialPropertyName2(old.ConfigurationManager.ActiveConfiguration.Name,out db);
   var d=(IModelDoc2)sw.OpenDoc6(dst,1,1,"",ref e,ref w);
   if(mat!="")((IPartDoc)d).SetMaterialPropertyName2(d.ConfigurationManager.ActiveConfiguration.Name,db,mat);
   string actualDb="";string actual=((IPartDoc)d).GetMaterialPropertyName2(d.ConfigurationManager.ActiveConfiguration.Name,out actualDb);
   if(actual!=mat)throw new Exception("Material mismatch "+code);
   d.Extension.CustomPropertyManager[""].Add3("Engineering material basis",30,"Preserved R08 selection: "+mat+"; provisional, see design review",2);
   if(code=="203")d.Extension.CustomPropertyManager[""].Add3("R09 change",30,"Center bore reduced from diameter 19 to 8.4 mm for positive rear support of center magnet. Set magnet axial clearance by tolerance stack.",2);
   if(code=="501")d.Extension.CustomPropertyManager[""].Add3("R09 change",30,"Removed diameter 5.7 through counterbores. Diameter 3.3 holes now leave screw-head bearing material.",2);
   if(!d.Save3(1,ref e,ref w)||e!=0)throw new Exception("Save error "+code);
   Console.WriteLine(code+" material="+actual);
  }
  int err=0;var top=(IModelDoc2)sw.ActivateDoc3("Magnetron gun R09.SLDASM",false,0,ref err);
  if(top!=null){int e=0,w=0;top.ForceRebuild3(false);top.Save3(1,ref e,ref w);}
 }
}
'@
[RestoreReviewMaterials]::Run($PSScriptRoot)
