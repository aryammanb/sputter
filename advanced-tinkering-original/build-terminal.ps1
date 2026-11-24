param([switch]$ReuseUnchanged)
$ErrorActionPreference='Stop'
$dll='C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll,'System.Web.Extensions' -TypeDefinition @'
using System;using System.IO;using System.Linq;using System.Text;using System.Collections.Generic;using System.Runtime.InteropServices;using System.Web.Script.Serialization;using SolidWorks.Interop.sldworks;
public class TerminalR01 {
 static ISldWorks sw;static IModelDoc2 d;static string root;static List<object> log=new List<object>();
 static string Template(string n){return @"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2021\templates\"+n;}
 static void Save(string p){int e=0,w=0;if(!d.Extension.SaveAs(p,0,1,null,ref e,ref w)||e!=0)throw new Exception("Save "+p+" "+e);}
 static void Profile(double[,] p){
  d=(IModelDoc2)sw.NewDocument(Template("Part.PRTDOT"),0,0,0);int e=0;sw.ActivateDoc3(d.GetTitle(),false,0,ref e);
  d.Extension.SelectByID2("Front Plane","PLANE",0,0,0,false,0,null,0);var s=d.SketchManager;s.InsertSketch(true);s.AddToDB=true;var sk=(IFeature)s.ActiveSketch;var axis=s.CreateCenterLine(0,-.2,0,0,.1,0);
  for(int i=0;i<p.GetLength(0);i++){int j=(i+1)%p.GetLength(0);s.CreateLine(p[i,1]/1000,p[i,0]/1000,0,p[j,1]/1000,p[j,0]/1000,0);}
  s.AddToDB=false;s.InsertSketch(true);d.ClearSelection2(true);sk.Select2(false,0);var sel=(SelectData)((ISelectionMgr)d.SelectionManager).CreateSelectData();sel.Mark=16;axis.Select4(true,sel);
  if(d.FeatureManager.FeatureRevolve2(true,true,false,false,false,false,0,0,2*Math.PI,0,false,false,0,0,0,0,0,true,true,true)==null)throw new Exception("Revolve");
 }
 static void Ring(double a,double b,double ro,double ri){Profile(new double[,]{{a,ri},{b,ri},{b,ro},{a,ro}});}
 static double[] SP(double x,double z){var math=(IMathUtility)sw.GetMathUtility();return (double[])((IMathPoint)((IMathPoint)math.CreatePoint(new double[]{x/1000,0,z/1000})).MultiplyTransform((MathTransform)d.SketchManager.ActiveSketch.ModelToSketchTransform)).ArrayData;}
 static void PlateHoles(){
  d.ClearSelection2(true);d.Extension.SelectByID2("Top Plane","PLANE",0,0,0,false,0,null,0);var s=d.SketchManager;s.InsertSketch(true);s.AddToDB=true;
  var dr=SP(Math.Sqrt(3),1.75);var dl=SP(-Math.Sqrt(3),1.75);var dm=SP(0,7.75);
  if(s.Create3PointArc(dr[0],dr[1],0,dl[0],dl[1],0,dm[0],dm[1],0)==null)throw new Exception("SMA D hole arc");s.CreateLine(dl[0],dl[1],0,dr[0],dr[1],0);
  foreach(var h in new[]{new double[]{-5.4,-3.6,3.6},new double[]{5.4,-3.6,3.6},new double[]{0,-9,1}}){var p=SP(h[0],h[1]);s.CreateCircleByRadius(p[0],p[1],0,h[2]/1000);}
  var sk=(IFeature)s.ActiveSketch;s.AddToDB=false;s.InsertSketch(true);sk.Name="SMA D6.5 - hoses D7.2 - vent D2";d.ClearSelection2(true);sk.Select2(false,0);
  var f=d.FeatureManager.FeatureCut4(false,false,false,1,1,.01,.01,false,false,false,false,0,0,false,false,false,false,false,true,true,false,false,false,0,0,false,false);
  if(f==null)throw new Exception("Plate holes");f.Name="Four through holes - both directions";
 }
 static void JackFlat(){
  d.ClearSelection2(true);d.Extension.SelectByID2("Front Plane","PLANE",0,0,0,false,0,null,0);var s=d.SketchManager;s.InsertSketch(true);s.AddToDB=true;
  double[,] p=new double[,]{{-.004,0},{.004,0},{.004,.0114},{-.004,.0114}};for(int i=0;i<4;i++){int j=(i+1)%4;s.CreateLine(p[i,0],p[i,1],0,p[j,0],p[j,1],0);}var sk=(IFeature)s.ActiveSketch;s.AddToDB=false;s.InsertSketch(true);d.ClearSelection2(true);sk.Select2(false,0);
  var f=d.FeatureManager.FeatureCut4(true,false,false,0,1,.02,.02,false,false,false,false,0,0,false,false,false,false,false,true,true,false,false,false,3,-.00265,false,false);
  if(f==null)throw new Exception("Connector antirotation flat");f.Name="Packaging flat at Z minus2p65";
 }
 static string Finish(string n,string note,double[] color){
  d.Extension.CustomPropertyManager[""].Add3("Design status",30,"Mechanical fit study R01; not an RF or pressure qualification",2);d.Extension.CustomPropertyManager[""].Add3("Details",30,note,2);
  d.MaterialPropertyValues=new double[]{color[0],color[1],color[2],.3,.8,.2,.25,0,0};d.ForceRebuild3(false);var bs=(object[])((IPartDoc)d).GetBodies2(0,false);if(bs==null||bs.Length!=1)throw new Exception(n+" body count");var b=(Body2)bs[0];if(b.Check()!=1)throw new Exception(n+" invalid");
  string p=Path.Combine(root,n+".SLDPRT");d.ShowNamedView2("*Isometric",7);d.ViewZoomtofit2();Save(p);Save(Path.Combine(root,n+".step"));log.Add(new {name=n,note=note,volume_mm3=((double[])b.GetMassProperties(1))[3]*1e9,check=b.Check(),box=(double[])b.GetBodyBox()});sw.CloseDoc(d.GetTitle());Console.WriteLine("Created "+n);return p;
 }
 class Item{public string Path;public double[] Tx;public Item(string p,double x=0,double z=0){Path=p;Tx=new double[]{1,0,0,0,1,0,0,0,1,x/1000,0,z/1000,1,0,0,0};}}
 public static void Run(string folder,bool reuse){
  root=folder;try{sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");}catch(COMException){sw=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));}sw.CloseDoc("One inch terminal - mechanical fit R01.SLDASM");
  var steel=new double[]{.58,.64,.70};var gold=new double[]{.86,.66,.25};var blue=new double[]{.12,.40,.77};var black=new double[]{.13,.15,.19};
  string tube=Path.Combine(root,"01 Tube service-end study D25p4x1p5.SLDPRT");if(!reuse){Ring(-100,0,12.7,11.2);tube=Finish("01 Tube service-end study D25p4x1p5","100mm straight service-end segment only. OD25.4 ID22.4. Upper magnetron/KF16 transition outside this subassembly.",steel);}
  string plate=Path.Combine(root,"02 Terminal plate D25p2 T2.SLDPRT");if(!reuse){Ring(0,2,12.6,0);PlateHoles();plate=Finish("02 Terminal plate D25p2 T2","316L or compatible stainless. Attach to tube end by qualified flush weld; finish all fixed parts within tube OD. SMA D hole6.5 diameter/6.0 overall height atX0 Z4.5, two7.2 hose guides atX+/-5.4 Z-3.6, vent2 atX0 Z-9. Antirotation D flat matches manufacturer recommended mounting hole.",steel);}
  Profile(new double[,]{{-18,2.665},{-5,2.665},{-5,.55},{11.4,.55},{11.4,3.175},{0,3.175},{0,4.619},{-3,4.619},{-3,3.24},{-18,3.24}});
  JackFlat();
  string sma=Finish("03 SMA132118 mechanical envelope","Amphenol132118 rear-mount crimp jack packaging envelope, not manufacturer CAD. 8AF hex represented by circumscribed circle9.238. D6.35 mating thread. Nose11.4 ahead of shoulder, total body22.7 nominal from drawing; crimp ferrule rear extension reserved18. Threads, contact and dielectric omitted. RF qualification pending.",gold);
  string washer=Path.Combine(root,"04 SMA washer D10p2 envelope.SLDPRT");if(!reuse){Ring(2,2.5,5.1,3.3);washer=Finish("04 SMA washer D10p2 envelope","Manufacturer drawing washerOD10.2 ID6.5; modeled ID6.6 and0.5 thickness are packaging assumptions. Drawing general tolerance permits OD10.6 maximum.",gold);}
  string nut=Path.Combine(root,"05 SMA nut 8AF envelope.SLDPRT");if(!reuse){Ring(2.5,4.1,4.619,3.25);nut=Finish("05 SMA nut 8AF envelope","8AF nut,1.6 thick per drawing, conservative round envelope9.238 OD. Thread omitted.",gold);}
  string guide=Path.Combine(root,"06 Hose guide D8 ID6p3.SLDPRT");if(!reuse){Profile(new double[,]{{-.8,3.15},{2.8,3.15},{2.8,4},{2,4},{2,3.55},{0,3.55},{0,4},{-.8,4}});guide=Finish("06 Hose guide D8 ID6p3","Custom flexible double-flanged grommet, non-sealing. Bore6.3 for hoseOD<=6; shank7.1, two8.0x0.8 lips straddle2mm plate, platehole7.2. Flexible material/installation to qualify; smaller-bore insert may be substituted for4mm hose. No pressure seal and no axial hose restraint implied.",new double[]{.88,.88,.78});}
  string hose=Path.Combine(root,"07 Hose D6 mechanical allowance.SLDPRT");if(!reuse){Ring(-100,35,3,2);hose=Finish("07 Hose D6 mechanical allowance","Maximum packaging study envelope only,6OD4ID. Source reference hoses were4OD; this is not a selected pressure-rated hose or proof of cooling flow.",blue);}
  string coax=Path.Combine(root,"08 Coax D5 packaging allowance.SLDPRT");if(!reuse){Ring(-100,-18,2.5,0);coax=Finish("08 Coax D5 packaging allowance","5mm OD internal coax study allowance for a connector-compatible cable. Cable dielectric, voltage/current ratings and head termination remain to select.",black);}
  var items=new List<Item>{new Item(tube),new Item(plate),new Item(sma,0,4.5),new Item(washer,0,4.5),new Item(nut,0,4.5),new Item(guide,-5.4,-3.6),new Item(guide,5.4,-3.6),new Item(hose,-5.4,-3.6),new Item(hose,5.4,-3.6),new Item(coax,0,4.5)};
  d=(IModelDoc2)sw.NewDocument(Template("Assembly.ASMDOT"),0,0,0);int e=0;sw.ActivateDoc3(d.GetTitle(),false,0,ref e);var a=(IAssemblyDoc)d;var tx=new double[16*items.Count];for(int i=0;i<items.Count;i++)Array.Copy(items[i].Tx,0,tx,i*16,16);var added=(object[])a.AddComponents3(items.Select(i=>i.Path).ToArray(),tx,items.Select(i=>"").ToArray());if(added==null||added.Length!=items.Count)throw new Exception("Assembly insertion");
  foreach(Component2 c in added){d.ClearSelection2(true);c.Select4(false,null,false);a.FixComponent();}d.ClearSelection2(true);d.ForceRebuild3(false);d.ShowNamedView2("*Isometric",7);d.ViewZoomtofit2();Save(Path.Combine(root,"One inch terminal - mechanical fit R01.SLDASM"));Save(Path.Combine(root,"One inch terminal - mechanical fit R01.step"));
  var mgr=a.InterferenceDetectionManager;mgr.TreatCoincidenceAsInterference=false;mgr.IgnoreHiddenBodies=false;var hits=mgr.GetInterferences() as object[];var collisions=new List<object>();if(hits!=null)foreach(Interference h in hits){collisions.Add(new {volume_mm3=h.Volume*1e9,parts=((object[])h.Components).Cast<Component2>().Select(c=>c.Name2).ToArray()});}mgr.Done();
  using(var wr=new BinaryWriter(File.Create(Path.Combine(root,"terminal-mesh.bin")) ))foreach(Component2 c in added){object info;var bs=(object[])c.GetBodies3(0,out info);var t=(double[])c.GetTotalTransform(true).ArrayData;var coords=new List<float>();foreach(Body2 b in bs)foreach(Face2 f in (object[])b.GetFaces()){var v=(float[])f.GetTessTriangles(true);for(int j=0;j<v.Length;j+=3)for(int k=0;k<3;k++)coords.Add((float)(1000*(t[k]*v[j]+t[3+k]*v[j+1]+t[6+k]*v[j+2]+t[9+k])));}wr.Write(c.Name2);wr.Write(Path.GetFileName(c.GetPathName()));wr.Write(coords.Count/9);foreach(float v in coords)wr.Write(v);}
  var checks=new List<object>();foreach(Component2 c in added){var pd=(IModelDoc2)c.GetModelDoc2();foreach(Body2 b in (object[])((IPartDoc)pd).GetBodies2(0,false)){if(b.Check()!=1)throw new Exception("Invalid assembly body "+c.Name2);checks.Add(new {name=c.Name2,check=b.Check(),volume_mm3=((double[])b.GetMassProperties(1))[3]*1e9,path=c.GetPathName()});}}
  var js=new JavaScriptSerializer();js.MaxJsonLength=10000000;File.WriteAllText(Path.Combine(root,"native-verification.json"),js.Serialize(new {parts=checks,components=added.Length,interferences=collisions}),Encoding.UTF8);Console.WriteLine("Complete components="+added.Length+" interferences="+collisions.Count);
 }
}
'@
[TerminalR01]::Run($PSScriptRoot,$ReuseUnchanged.IsPresent)


