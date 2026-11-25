$ErrorActionPreference='Stop'
$dll='C:/Program Files/SOLIDWORKS Corp/SOLIDWORKS/SolidWorks.Interop.sldworks.dll'
Add-Type -Path $dll
Add-Type -ReferencedAssemblies $dll -TypeDefinition @'
using System;using System.Runtime.InteropServices;using SolidWorks.Interop.sldworks;
public class SWR06Probe{public static void Run(){var sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");Console.WriteLine(sw.RevisionNumber());Console.WriteLine("Documents "+sw.GetDocumentCount());foreach(var p in typeof(IFeatureManager).GetMethod("FeatureCut3").GetParameters())Console.WriteLine(p.Name+" "+p.ParameterType);}}
'@
[SWR06Probe]::Run()
