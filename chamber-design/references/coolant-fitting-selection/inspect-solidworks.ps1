$sw=[Runtime.InteropServices.Marshal]::GetActiveObject('SldWorks.Application')
$sw.RevisionNumber()
if($sw.ActiveDoc){$sw.ActiveDoc.GetPathName()}
Add-Type -Path 'C:/Program Files/SOLIDWORKS Corp/SOLIDWORKS/SolidWorks.Interop.sldworks.dll'
[SolidWorks.Interop.sldworks.IFeatureManager].GetMethods() | Where-Object Name -eq FeatureCut3 | ForEach-Object { $_.ToString() }
