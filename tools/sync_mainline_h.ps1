param(
    [Parameter(Mandatory = $true)]
    [string]$HDataRoot
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$sourceMods = (Resolve-Path (Join-Path $HDataRoot "mods")).Path
$targetMods = (Resolve-Path (Join-Path $repo "data\Mainline_mods\Mods")).Path
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$copied = 0
$emptied = 0

foreach ($targetMod in Get-ChildItem -LiteralPath $targetMods -Directory) {
    $sourceMod = Join-Path $sourceMods $targetMod.Name
    if (-not (Test-Path -LiteralPath $sourceMod -PathType Container)) {
        throw "The exact H data tree does not contain $($targetMod.Name)"
    }

    $sourceFiles = @{}
    foreach ($sourceFile in Get-ChildItem -LiteralPath $sourceMod -Recurse -File) {
        $relative = $sourceFile.FullName.Substring($sourceMod.Length).TrimStart([char[]]@([char]92, [char]47))
        $sourceFiles[$relative] = $true
        $targetFile = Join-Path $targetMod.FullName $relative
        $targetParent = Split-Path -Parent $targetFile
        if (-not (Test-Path -LiteralPath $targetParent)) {
            New-Item -ItemType Directory -Path $targetParent -Force | Out-Null
        }
        Copy-Item -LiteralPath $sourceFile.FullName -Destination $targetFile -Force
        $copied++
    }

    # H does not conditionally ignore newer-only JSON paths.  Keep every
    # repository JSON file, but remove entries from files absent in 0.H.
    foreach ($targetJson in Get-ChildItem -LiteralPath $targetMod.FullName -Recurse -File -Filter *.json) {
        $relative = $targetJson.FullName.Substring($targetMod.FullName.Length).TrimStart([char[]]@([char]92, [char]47))
        if (-not $sourceFiles.ContainsKey($relative)) {
            [System.IO.File]::WriteAllText($targetJson.FullName, "[]`n", $utf8NoBom)
            $emptied++
        }
    }
}

Write-Output "Copied exact H files: $copied"
Write-Output "Preserved newer-only JSON files as empty arrays: $emptied"
