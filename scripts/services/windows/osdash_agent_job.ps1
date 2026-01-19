param(
  [string]$AgentId = "AIC",
  [string]$RepoRoot = "C:\\OSDashboardAI",
  [int]$ProcessMemoryMB = 4096,
  [int]$JobMemoryMB = 4096
)

$ErrorActionPreference = "Stop"

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public static class JobObjectApi
{
    public const int JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x100;
    public const int JOB_OBJECT_LIMIT_JOB_MEMORY = 0x200;
    public const int JobObjectExtendedLimitInformation = 9;

    [StructLayout(LayoutKind.Sequential)]
    public struct JOBOBJECT_BASIC_LIMIT_INFORMATION
    {
        public long PerProcessUserTimeLimit;
        public long PerJobUserTimeLimit;
        public int LimitFlags;
        public UIntPtr MinimumWorkingSetSize;
        public UIntPtr MaximumWorkingSetSize;
        public int ActiveProcessLimit;
        public long Affinity;
        public int PriorityClass;
        public int SchedulingClass;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct IO_COUNTERS
    {
        public ulong ReadOperationCount;
        public ulong WriteOperationCount;
        public ulong OtherOperationCount;
        public ulong ReadTransferCount;
        public ulong WriteTransferCount;
        public ulong OtherTransferCount;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct JOBOBJECT_EXTENDED_LIMIT_INFORMATION
    {
        public JOBOBJECT_BASIC_LIMIT_INFORMATION BasicLimitInformation;
        public IO_COUNTERS IoInfo;
        public UIntPtr ProcessMemoryLimit;
        public UIntPtr JobMemoryLimit;
        public UIntPtr PeakProcessMemoryUsed;
        public UIntPtr PeakJobMemoryUsed;
    }

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
    public static extern IntPtr CreateJobObject(IntPtr lpJobAttributes, string lpName);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool SetInformationJobObject(IntPtr hJob, int infoType, IntPtr lpJobObjectInfo, uint cbJobObjectInfoLength);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool AssignProcessToJobObject(IntPtr hJob, IntPtr hProcess);
}
"@

$jobName = "OSDashAgent_$AgentId"
$jobHandle = [JobObjectApi]::CreateJobObject([IntPtr]::Zero, $jobName)
if ($jobHandle -eq [IntPtr]::Zero) {
  throw "Failed to create Job Object for $jobName"
}

$limitInfo = New-Object JobObjectApi+JOBOBJECT_EXTENDED_LIMIT_INFORMATION
$limitInfo.BasicLimitInformation.LimitFlags = [JobObjectApi]::JOB_OBJECT_LIMIT_PROCESS_MEMORY -bor [JobObjectApi]::JOB_OBJECT_LIMIT_JOB_MEMORY
$limitInfo.ProcessMemoryLimit = [UIntPtr]::new([UInt64]$ProcessMemoryMB * 1MB)
$limitInfo.JobMemoryLimit = [UIntPtr]::new([UInt64]$JobMemoryMB * 1MB)

$size = [System.Runtime.InteropServices.Marshal]::SizeOf($limitInfo)
$ptr = [System.Runtime.InteropServices.Marshal]::AllocHGlobal($size)
[System.Runtime.InteropServices.Marshal]::StructureToPtr($limitInfo, $ptr, $false)

$result = [JobObjectApi]::SetInformationJobObject($jobHandle, [JobObjectApi]::JobObjectExtendedLimitInformation, $ptr, [uint32]$size)
[System.Runtime.InteropServices.Marshal]::FreeHGlobal($ptr)

if (-not $result) {
  throw "Failed to apply Job Object limits for $jobName"
}

$python = "python"
$script = Join-Path $RepoRoot "unified_launcher.py"
$args = "`"$script`" --agent-id $AgentId"

$proc = Start-Process -FilePath $python -ArgumentList $args -PassThru -WindowStyle Hidden
$assigned = [JobObjectApi]::AssignProcessToJobObject($jobHandle, $proc.Handle)
if (-not $assigned) {
  throw "Failed to assign process to Job Object for $jobName"
}

try {
  $proc.PriorityClass = "AboveNormal"
} catch {
  Write-Host "Priority update failed: $($_.Exception.Message)"
}

Write-Host "OS Dash agent $AgentId started with Job Object limits. PID=$($proc.Id)"
