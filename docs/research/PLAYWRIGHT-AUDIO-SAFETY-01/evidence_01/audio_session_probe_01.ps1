# PLAYWRIGHT-AUDIO-SAFETY-01: enumerate Windows audio sessions (volume mixer entries per app). Read-only, API 0, makes no sound.
# Output: JSON [{pid, process, state(0=Inactive,1=Active,2=Expired), peak(session or ENDPOINT_MASTER_METER(pid=-1) peak level 0..1; endpoint=what the speaker device actually renders)}]. Active + browser-descendant pid = that process is sending audio to Windows.
Add-Type -TypeDefinition @"
using System; using System.Runtime.InteropServices; using System.Collections.Generic;
public static class AudioSessionProbe {
  [ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")] class MMDeviceEnumeratorCom {}
  [ComImport, Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  interface IMMDeviceEnumerator { int EnumAudioEndpoints(int f, int m, out IntPtr c); int GetDefaultAudioEndpoint(int f, int r, out IMMDevice d); }
  [ComImport, Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  interface IMMDevice { int Activate(ref Guid iid, int ctx, IntPtr p, [MarshalAs(UnmanagedType.IUnknown)] out object o); }
  [ComImport, Guid("77AA99A0-1BD6-484F-8BC7-2C654C9A9B6F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  interface IAudioSessionManager2 { int GetAudioSessionControl(IntPtr a, int f, out IntPtr c); int GetSimpleAudioVolume(IntPtr a, int f, out IntPtr v); int GetSessionEnumerator(out IAudioSessionEnumerator e); }
  [ComImport, Guid("E2F5BB11-0570-40CA-ACDD-3AA01277DEE8"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  interface IAudioSessionEnumerator { int GetCount(out int n); int GetSession(int i, out IAudioSessionControl2 s); }
  [ComImport, Guid("BFB7FF88-7239-4FC9-8FA2-07C950BE9C6D"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  interface IAudioSessionControl2 {
    int GetState(out int s); int GetDisplayName(out IntPtr n); int SetDisplayName(IntPtr n, IntPtr c); int GetIconPath(out IntPtr p); int SetIconPath(IntPtr p, IntPtr c);
    int GetGroupingParam(out Guid g); int SetGroupingParam(ref Guid g, IntPtr c); int RegisterAudioSessionNotification(IntPtr n); int UnregisterAudioSessionNotification(IntPtr n);
    int GetSessionIdentifier(out IntPtr i); int GetSessionInstanceIdentifier(out IntPtr i); int GetProcessId(out uint pid); int IsSystemSoundsSession(); int SetDuckingPreference(bool b); }
  [ComImport, Guid("C02216F6-8C67-4B5B-9D00-D008E73E0064"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  interface IAudioMeterInformation { int GetPeakValue(out float peak); }
  public static List<string> Probe() {
    var res = new List<string>();
    var en = (IMMDeviceEnumerator)(new MMDeviceEnumeratorCom());
    IMMDevice dev; en.GetDefaultAudioEndpoint(0, 1, out dev);
    Guid iid = new Guid("77AA99A0-1BD6-484F-8BC7-2C654C9A9B6F"); object o; dev.Activate(ref iid, 23, IntPtr.Zero, out o);
    var mgr = (IAudioSessionManager2)o; IAudioSessionEnumerator se; mgr.GetSessionEnumerator(out se);
    int n; se.GetCount(out n);
    for (int i = 0; i < n; i++) { IAudioSessionControl2 c; se.GetSession(i, out c); uint pid; c.GetProcessId(out pid); int st; c.GetState(out st); float pk = -1; try { ((IAudioMeterInformation)c).GetPeakValue(out pk); } catch {} res.Add(pid + "," + st + "," + pk.ToString("R")); }
    float epk = -1; try { Guid mi = new Guid("C02216F6-8C67-4B5B-9D00-D008E73E0064"); object mo; dev.Activate(ref mi, 23, IntPtr.Zero, out mo); ((IAudioMeterInformation)mo).GetPeakValue(out epk); } catch {}
    res.Add("ENDPOINT,0," + epk.ToString("R"));
    return res;
  }
}
"@
$rows = foreach ($l in [AudioSessionProbe]::Probe()) { $a = $l.Split(',')
  if ($a[0] -eq 'ENDPOINT') { [pscustomobject]@{ pid = -1; process = 'ENDPOINT_MASTER_METER'; state = 0; peak = [double]$a[2] }; continue }
  $p = Get-Process -Id ([int]$a[0]) -ErrorAction SilentlyContinue
  [pscustomobject]@{ pid = [int]$a[0]; process = $(if ($p) { $p.ProcessName } else { '' }); state = [int]$a[1]; peak = [double]$a[2] } }
@($rows) | ConvertTo-Json -Compress
