param(
    [Parameter(Mandatory = $true)]
    [string]$GameExe,
    [Parameter(Mandatory = $true)]
    [string]$GameData,
    [string[]]$OnlyPacks = @(),
    [string[]]$OnlyModIds = @(),
    [ValidateRange(1, 64)]
    [int]$ShardCount = 1,
    [ValidateRange(0, 63)]
    [int]$ShardIndex = 0,
    [ValidateRange(30, 3600)]
    [int]$TimeoutSeconds = 600
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if ($ShardIndex -ge $ShardCount) {
    throw "ShardIndex must be smaller than ShardCount"
}
$runStamp = Get-Date -Format "yyyyMMdd-HHmmss-fff"
$runRoot = Join-Path $env:TEMP "cdda-h-pack-tests-$runStamp-$PID-shard$ShardIndex-of$ShardCount"
New-Item -ItemType Directory -Path $runRoot -Force | Out-Null

function ConvertTo-CommandLineArgument([string]$Value) {
    return '"' + $Value.Replace('"', '\"') + '"'
}

function Invoke-HCheck([string[]]$CheckArguments, [string]$OutputPath) {
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $GameExe
    $startInfo.Arguments = (($CheckArguments | ForEach-Object { ConvertTo-CommandLineArgument $_ }) -join ' ')
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    [void]$process.Start()
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $finished = $process.WaitForExit($TimeoutSeconds * 1000)
    if (-not $finished) {
        $process.Kill()
        $process.WaitForExit()
    }
    $combinedOutput = $stdoutTask.Result + $stderrTask.Result
    $combinedOutput | Out-File -LiteralPath $OutputPath -Encoding utf8
    if (-not $finished) { return -999 }
    return $process.ExitCode
}

function Get-ErrorStats([string]$DebugLog) {
    if (-not (Test-Path -LiteralPath $DebugLog)) {
        return [pscustomobject]@{ Total = -1; Core = 0; Mod = -1 }
    }
    $text = Get-Content -LiteralPath $DebugLog -Raw -Encoding UTF8
    $total = [regex]::Matches($text, ' ERROR :').Count
    # The H executable currently reports a known set of diagnostics from its
    # bundled data.  Keep those visible, but do not treat them as mod errors.
    $gameDataToken = ((Resolve-Path -LiteralPath $GameData).Path -replace '\\', '/')
    $core = [regex]::Matches(
        $text,
        '(?im)Json error:\s*' + [regex]::Escape($gameDataToken)
    ).Count
    $mod = [math]::Max(0, $total - $core)
    return [pscustomobject]@{ Total = $total; Core = $core; Mod = $mod }
}

$records = [System.Collections.Generic.List[object]]::new()
$modInfoFiles = & rg -l 'MOD_INFO' (Join-Path $repo "data") (Join-Path $repo "workshop") --glob "*.json"
foreach ($file in $modInfoFiles) {
    try {
        $parsed = Get-Content -LiteralPath $file -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        continue
    }
    foreach ($entry in @($parsed)) {
        if ($entry.type -eq "MOD_INFO" -and $entry.id) {
            $relative = $file.Substring($repo.Length).TrimStart([char[]]@([char]92, [char]47))
            $parts = $relative -split '[\\/]'
            $pack = if ($parts[0] -eq "workshop") { "workshop/$($parts[1])" } else { "data/$($parts[1])" }
            $records.Add([pscustomobject]@{
                Id = [string]$entry.id
                Dependencies = @($entry.dependencies)
                Root = Split-Path -Parent $file
                File = $file
                Pack = $pack
            })
        }
    }
}

$byId = @{}
foreach ($record in $records) {
    if (-not $byId.ContainsKey($record.Id)) {
        $byId[$record.Id] = [System.Collections.Generic.List[object]]::new()
    }
    $byId[$record.Id].Add($record)
}

$bundledModIds = [System.Collections.Generic.HashSet[string]]::new()
$bundledModsRoot = Join-Path $GameData "mods"
if (Test-Path -LiteralPath $bundledModsRoot) {
    foreach ($file in (Get-ChildItem -LiteralPath $bundledModsRoot -Recurse -File -Filter "modinfo.json")) {
        try {
            $parsed = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
        } catch {
            continue
        }
        foreach ($entry in @($parsed)) {
            if ($entry.type -eq "MOD_INFO" -and $entry.id) {
                [void]$bundledModIds.Add([string]$entry.id)
            }
        }
    }
}

$globallyUnavailable = [System.Collections.Generic.HashSet[string]]::new()
$changed = $true
while ($changed) {
    $changed = $false
    foreach ($record in $records) {
        if ($globallyUnavailable.Contains($record.Id)) { continue }
        foreach ($dependency in $record.Dependencies) {
            if ([string]::IsNullOrWhiteSpace([string]$dependency)) { continue }
            if (
                $dependency -ne "dda" -and
                -not $bundledModIds.Contains([string]$dependency) -and
                (-not $byId.ContainsKey($dependency) -or $globallyUnavailable.Contains([string]$dependency))
            ) {
                if ($globallyUnavailable.Add($record.Id)) { $changed = $true }
                break
            }
        }
    }
}

$packs = @($records.Pack | Sort-Object -Unique)
if ($OnlyPacks.Count -gt 0) {
    $packs = @($packs | Where-Object { $_ -in $OnlyPacks })
}

$results = [System.Collections.Generic.List[object]]::new()
$failed = $false
foreach ($pack in $packs) {
    $packRecords = @($records | Where-Object Pack -eq $pack)
    $allPackIds = @($packRecords.Id | Sort-Object -Unique)
    $checkIds = @($allPackIds | Where-Object { -not $globallyUnavailable.Contains($_) })
    $skippedIds = @($allPackIds | Where-Object { $globallyUnavailable.Contains($_) })
    if ($OnlyModIds.Count -gt 0) {
        $checkIds = @($checkIds | Where-Object { $_ -in $OnlyModIds })
    }
    if ($ShardCount -gt 1) {
        $checkIds = @(
            for ($checkIndex = 0; $checkIndex -lt $checkIds.Count; $checkIndex++) {
                if (($checkIndex % $ShardCount) -eq $ShardIndex) { $checkIds[$checkIndex] }
            }
        )
    }
    if ($checkIds.Count -eq 0) { continue }

    $selected = @{}
    foreach ($checkId in $checkIds) {
        $selected[$checkId] = @($packRecords | Where-Object Id -eq $checkId)[0]
    }

    $missing = [System.Collections.Generic.HashSet[string]]::new()
    $pending = [System.Collections.Generic.Queue[object]]::new()
    foreach ($record in $selected.Values) { $pending.Enqueue($record) }
    while ($pending.Count -gt 0) {
        $record = $pending.Dequeue()
        foreach ($dependency in $record.Dependencies) {
            if ([string]::IsNullOrWhiteSpace([string]$dependency)) { continue }
            if (
                $dependency -eq "dda" -or
                $bundledModIds.Contains([string]$dependency) -or
                $selected.ContainsKey($dependency)
            ) { continue }
            if ($byId.ContainsKey($dependency)) {
                # Several collections intentionally carry their own version
                # of a shared compatibility dependency.  Prefer the version
                # shipped in the same pack instead of an unrelated global
                # first match.
                $dependencyRecord = @($byId[$dependency] | Where-Object Pack -eq $record.Pack | Select-Object -First 1)
                if ($dependencyRecord.Count -gt 0) {
                    $dependencyRecord = $dependencyRecord[0]
                } else {
                    $dependencyRecord = $byId[$dependency][0]
                }
                $selected[$dependency] = $dependencyRecord
                $pending.Enqueue($dependencyRecord)
            } else {
                [void]$missing.Add([string]$dependency)
            }
        }
    }

    $safePack = $pack -replace '[^A-Za-z0-9_.-]', '_'
    $userDir = Join-Path $runRoot $safePack
    $modsDir = Join-Path $userDir "mods"
    New-Item -ItemType Directory -Path $modsDir, (Join-Path $userDir "config") -Force | Out-Null

    $index = 0
    foreach ($record in @($selected.Values | Sort-Object Id)) {
        $safeId = $record.Id -replace '[^A-Za-z0-9_.-]', '_'
        $link = Join-Path $modsDir ("{0:D4}_{1}" -f $index, $safeId)
        New-Item -ItemType Junction -Path $link -Target $record.Root | Out-Null
        $index++
    }

    $arguments = @("--userdir", $userDir, "--datadir", $GameData, "--check-mods") + $checkIds
    $stdout = Join-Path $userDir "output.log"
    $gameExit = Invoke-HCheck -CheckArguments $arguments -OutputPath $stdout
    $debugLog = Join-Path $userDir "config\debug.log"
    $errorStats = Get-ErrorStats $debugLog
    $results.Add([pscustomobject]@{
        Pack = $pack
        Mods = $checkIds.Count
        Exit = $gameExit
        Errors = $errorStats.Mod
        CoreErrors = $errorStats.Core
        MissingDependencies = (@($missing) -join ',')
        UserDir = $userDir
    })
    if ($gameExit -ne 0 -or $errorStats.Mod -gt 0 -or $missing.Count -gt 0) { $failed = $true }
    Write-Output ("PACK`t{0}`tSHARD={1}/{2}`tMODS={3}`tEXIT={4}`tERRORS={5}`tCORE_ERRORS={6}`tMISSING={7}`tSKIPPED={8}`tUSERDIR={9}" -f $pack, $ShardIndex, $ShardCount, $checkIds.Count, $gameExit, $errorStats.Mod, $errorStats.Core, (@($missing) -join ','), ($skippedIds -join ','), $userDir)
}

# A pack can contain more than one implementation of the same mod id.  The
# normal pack run checks the first; check every alternate implementation in a
# clean directory as well.
foreach ($id in @($byId.Keys | Sort-Object)) {
    if ($ShardIndex -ne 0) { break }
    if ($OnlyModIds.Count -gt 0 -and $id -notin $OnlyModIds) { continue }
    $groupedByPack = @($byId[$id] | Group-Object Pack)
    foreach ($group in $groupedByPack) {
        if ($group.Count -le 1 -or ($OnlyPacks.Count -gt 0 -and $group.Name -notin $OnlyPacks)) { continue }
        for ($alternateIndex = 1; $alternateIndex -lt $group.Count; $alternateIndex++) {
            $record = $group.Group[$alternateIndex]
            $safePack = $record.Pack -replace '[^A-Za-z0-9_.-]', '_'
            $safeId = $id -replace '[^A-Za-z0-9_.-]', '_'
            $userDir = Join-Path $runRoot ("alternate_{0}_{1}_{2}" -f $safePack, $safeId, $alternateIndex)
            $modsDir = Join-Path $userDir "mods"
            New-Item -ItemType Directory -Path $modsDir, (Join-Path $userDir "config") -Force | Out-Null
            New-Item -ItemType Junction -Path (Join-Path $modsDir $safeId) -Target $record.Root | Out-Null
            $arguments = @("--userdir", $userDir, "--datadir", $GameData, "--check-mods", $id)
            $stdout = Join-Path $userDir "output.log"
            $gameExit = Invoke-HCheck -CheckArguments $arguments -OutputPath $stdout
            $debugLog = Join-Path $userDir "config\debug.log"
            $errorStats = Get-ErrorStats $debugLog
            if ($gameExit -ne 0 -or $errorStats.Mod -gt 0) { $failed = $true }
            Write-Output ("ALT`t{0}`tID={1}`tEXIT={2}`tERRORS={3}`tCORE_ERRORS={4}`tUSERDIR={5}" -f $record.Pack, $id, $gameExit, $errorStats.Mod, $errorStats.Core, $userDir)
        }
    }
}

Write-Output ("RUNROOT`t{0}" -f $runRoot)
if ($failed) { exit 1 }
exit 0
