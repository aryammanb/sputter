$ErrorActionPreference = 'Stop'
$dll = 'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;
using System.IO;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public class FreshCoolingBody01 {
 static ISldWorks sw;
 static IModelDoc2 d;
 static double Rad(double a){return a*Math.PI/180;}
 static double[] P(double r,double a){return new double[]{r*Math.Cos(Rad(a)),r*Math.Sin(Rad(a))};}
 static void Save(string path){int e=0,w=0;if(!d.Extension.SaveAs(path,0,1,null,ref e,ref w)||e!=0)throw new Exception("Save failed "+path+" error="+e);Console.WriteLine(Path.GetFileName(path)+" warnings="+w);}
 static void Prop(string key,string value){d.Extension.CustomPropertyManager[""].Add3(key,30,value,2);}
 static IFeature StartSketch(){
  d.ClearSelection2(true);
  if(!d.Extension.SelectByID2("Right Plane","PLANE",0,0,0,false,0,null,0))throw new Exception("Right plane selection");
  d.SketchManager.InsertSketch(true);d.SketchManager.AddToDB=true;
  return (IFeature)d.SketchManager.ActiveSketch;
 }
 static double[] SP(double y,double z){
  var m=(IMathUtility)sw.GetMathUtility();var p=(IMathPoint)m.CreatePoint(new double[]{0,y/1000,z/1000});
  return (double[])((IMathPoint)p.MultiplyTransform((MathTransform)d.SketchManager.ActiveSketch.ModelToSketchTransform)).ArrayData;
 }
 static void Circle(double y,double z,double r){var p=SP(y,z);d.SketchManager.CreateCircleByRadius(p[0],p[1],0,r/1000);}
 static void Arc(double[] a,double[] b,double[] mid){var p=SP(a[0],a[1]);var q=SP(b[0],b[1]);var t=SP(mid[0],mid[1]);if(d.SketchManager.Create3PointArc(p[0],p[1],0,q[0],q[1],0,t[0],t[1],0)==null)throw new Exception("Arc creation failed");}
 static void Cut(IFeature sk,string name,double from,double depth){
  d.SketchManager.AddToDB=false;d.SketchManager.InsertSketch(true);sk.Name=name+" sketch";
  d.ClearSelection2(true);sk.Select2(false,0);
  var f=d.FeatureManager.FeatureCut4(true,false,true,0,1,depth/1000,.4,false,false,false,false,0,0,false,false,false,false,false,true,true,false,false,false,3,from/1000,false,false);
  if(f==null)throw new Exception("Cut failed "+name);f.Name=name;
 }
 static void Shot(string path,string view,int id,bool tilt){d.ClearSelection2(true);d.ShowNamedView2(view,id);if(tilt)((IModelView)d.ActiveView).RotateAboutCenter(.38,-.42);d.ViewZoomtofit2();d.GraphicsRedraw2();Save(path);}
 public static void Run(string folder){
  Directory.CreateDirectory(folder);
  try{sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");}catch(COMException){sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));}
  d=(IModelDoc2)sw.NewDocument(@"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2021\templates\Part.PRTDOT",0,0,0);
  if(d==null)throw new Exception("Part template unavailable");
  int activateError=0;sw.ActivateDoc3(d.GetTitle(),false,0,ref activateError);
  // Axial coordinate X: rear mating face 0, target face +7 mm.
  IFeature plane=(IFeature)d.FirstFeature();while(plane!=null&&plane.GetTypeName2()!="RefPlane")plane=(IFeature)plane.GetNextFeature();
  if(plane==null||(!plane.Select2(false,0)&&!d.Extension.SelectByID2(plane.Name,"PLANE",0,0,0,false,0,null,0)))throw new Exception("Revolve plane selection");
  var s=d.SketchManager;s.InsertSketch(true);s.AddToDB=true;
  var axis=s.CreateCenterLine(-.01,0,0,.02,0,0);
  double[,] profile={{0,0},{7,0},{7,35},{0,35}};
  for(int i=0;i<4;i++){int j=(i+1)%4;s.CreateLine(profile[i,0]/1000,profile[i,1]/1000,0,profile[j,0]/1000,profile[j,1]/1000,0);}
  var sf=(IFeature)s.ActiveSketch;s.AddToDB=false;s.InsertSketch(true);sf.Name="Blank OD70 thickness7 mm";
  d.ClearSelection2(true);sf.Select2(false,0);var sel=(SelectData)((ISelectionMgr)d.SelectionManager).CreateSelectData();sel.Mark=16;axis.Select4(true,sel);
  var rev=d.FeatureManager.FeatureRevolve2(true,true,false,false,false,false,0,0,2*Math.PI,0,false,false,0,0,0,0,0,true,true,true);
  if(rev==null)throw new Exception("Blank revolve failed");rev.Name="Copper blank - OD70 x7";
  // C passage: concentric R11/R25 arcs over 300 degrees, R7 round ends.
  var c=StartSketch();
  var oa=P(25,30);var ob=P(25,330);var ia=P(11,30);var ib=P(11,330);
  Arc(oa,ob,P(25,180));
  var cb=P(18,330);Arc(ob,ib,new double[]{cb[0]-7*Math.Sin(Rad(330)),cb[1]+7*Math.Cos(Rad(330))});
  Arc(ib,ia,P(11,180));
  var ca=P(18,30);Arc(ia,oa,new double[]{ca[0]+7*Math.Sin(Rad(30)),ca[1]-7*Math.Cos(Rad(30))});
  Cut(c,"Water passage R11-25 depth3 round-end C",0,3);
  var g=StartSketch();Circle(0,0,6.7);Circle(0,0,9.3);
  Cut(g,"Inner face-seal gland width2p6 depth1p5",0,1.5);
  g=StartSketch();Circle(0,0,26.7);Circle(0,0,29.3);
  Cut(g,"Outer face-seal gland width2p6 depth1p5",0,1.5);
  var h=StartSketch();for(int i=0;i<6;i++){var p=P(32,60*i);Circle(p[0],p[1],1.25);}Cut(h,"Six rear cover M3 pilot bores depth4",0,4);
  h=StartSketch();for(int i=0;i<3;i++){var p=P(32,30+120*i);Circle(p[0],p[1],1.25);}Cut(h,"Three front clamp M3 pilot bores depth3",4,3);
  ((IPartDoc)d).SetMaterialPropertyName2(d.ConfigurationManager.ActiveConfiguration.Name,@"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\lang\english\sldmaterials\solidworks materials.sldmat","Copper");
  Prop("Part number","F01-001 revision A");Prop("Specified material","C110 copper; native Copper material is a display/density proxy");
  Prop("Status","CONCEPT CAD - NOT RELEASED FOR MANUFACTURE. No power or pressure rating assigned.");
  Prop("Coordinate system","X0 rear seal/cover face; X7 target seat. Axis X. All dimensions mm.");
  Prop("Nominal geometry","OD70 x7; C-channel R11-25 depth3; R7 closed ends; remaining front wall4; target nominal OD50.8.");
  Prop("Face seal intent","Nominal ID14 x2 and ID54 x2 O-rings. Glands R6.7-9.3 and R26.7-29.3, depth1.5. 25 percent nominal squeeze and 80.55 percent nominal fill. Compound/tolerances/thermal swell and retaining geometry unresolved.");
  Prop("Fastener intent","Rear: 6 M3x0.5 blind nominal pilot pockets diameter2.5 depth4 on PCD64 at 0+60n deg. Front: 3 M3 pilots depth3 on PCD64 at 30+120n deg. Threads/drill points/runout/vents not modeled. Copper thread strength and preload unresolved.");
  Prop("Cover interface","Rear mating cover not yet modeled. Ports must align over C passage endpoints at radius18 angles +/-30 deg. Two endpoint center separation18 mm. Water boundary not closed in this part alone.");
  Prop("Atmospheric architecture","Dry rear cavity intended to vent to atmosphere. This part alone does not establish vacuum sealing or an atmospheric cavity. Peripheral insulating support seal interface remains to design.");
  Prop("Model method","Native revolve and sketch cuts generated from build-part01.ps1; coordinate-defined sketches, not fully dimension-constrained production sketches.");
  d.ForceRebuild3(false);
  var bodies=(object[])((IPartDoc)d).GetBodies2(0,false);if(bodies==null||bodies.Length!=1)throw new Exception("Expected one solid");
  var body=(Body2)bodies[0];double actual=((double[])body.GetMassProperties(1))[3]*1e9;
  double passageArea=(300.0/360)*Math.PI*(25*25-11*11)+Math.PI*7*7;
  double expected=Math.PI*35*35*7-passageArea*3-Math.PI*(9.3*9.3-6.7*6.7+29.3*29.3-26.7*26.7)*1.5-Math.PI*1.25*1.25*(6*4+3*3);
  if(Math.Abs(actual-expected)>.01)throw new Exception("Volume mismatch actual="+actual+" expected="+expected);
  Save(Path.Combine(folder,"F01-001 Copper cooling body RevA.SLDPRT"));
  Save(Path.Combine(folder,"F01-001 Copper cooling body RevA.step"));
  Shot(Path.Combine(folder,"F01-001 rear isometric.png"),"*Left",3,true);
  Shot(Path.Combine(folder,"F01-001 rear face.png"),"*Left",3,false);
  Shot(Path.Combine(folder,"F01-001 target face.png"),"*Right",4,true);
  Shot(Path.Combine(folder,"F01-001 rear isometric.png"),"*Left",3,true);
  var box=(double[])body.GetBodyBox();
  string report="Single solid: PASS\r\nAnalytic volume comparison: PASS\r\nVolume mm3: "+actual.ToString("F6")+"\r\nExpected mm3: "+expected.ToString("F6")+"\r\nBounding box m: "+String.Join(", ",box)+"\r\nWater passage volume mm3: "+(passageArea*3).ToString("F6")+"\r\nFront wall mm: 4\r\nChannel-to-gland radial ligament mm: 1.7\r\nOuter gland to rear hole edge mm: 1.45\r\nRear hole to OD edge mm: 1.75\r\nNominal O-ring squeeze: 25 percent\r\nNominal gland fill: "+(Math.PI/(2.6*1.5)*100).ToString("F3")+" percent\r\nNot checked: pressure/thermal/magnetic/electrical performance, seal and fastener qualification.\r\n";
  File.WriteAllText(Path.Combine(folder,"F01-001 geometry checks.txt"),report);Console.WriteLine(report);
 }
}
'@
[FreshCoolingBody01]::Run($PSScriptRoot)
