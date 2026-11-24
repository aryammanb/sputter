$swRead = [Runtime.InteropServices.Marshal]::GetActiveObject('SldWorks.Application')
Write-Output ('PID ' + $swRead.GetProcessID())
Write-Output ('Title ' + $swRead.ActiveDoc.GetTitle())
