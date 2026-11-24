Add-Type -TypeDefinition @'
using System;using System.Text;using System.Runtime.InteropServices;using System.Diagnostics;
public class SWWinRead {
 delegate bool Callback(IntPtr h,IntPtr p);
 [DllImport("user32.dll")]static extern bool EnumWindows(Callback c,IntPtr p);
 [DllImport("user32.dll")]static extern bool EnumChildWindows(IntPtr h,Callback c,IntPtr p);
 [DllImport("user32.dll")]static extern uint GetWindowThreadProcessId(IntPtr h,out uint p);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)]static extern int GetWindowText(IntPtr h,StringBuilder s,int n);
 public static void Run(){EnumWindows((h,p)=>{uint id;GetWindowThreadProcessId(h,out id);string n="";try{n=Process.GetProcessById((int)id).ProcessName;}catch{}if(n.ToLower().Contains("sld")||n.ToLower().Contains("solid")){var s=new StringBuilder(1024);GetWindowText(h,s,1024);Console.WriteLine(id+" "+h+" "+n+" "+s);EnumChildWindows(h,(ch,z)=>{var t=new StringBuilder(1024);GetWindowText(ch,t,1024);if(t.Length>0)Console.WriteLine("  "+ch+" "+t);return true;},IntPtr.Zero);}return true;},IntPtr.Zero);}
}
'@
[SWWinRead]::Run()
