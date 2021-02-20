  Write-Output "JSON formatting script begins."
  $scriptDir = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
  Set-Location -Path (Join-Path -Path $scriptDir -ChildPath "..")
  $blacklist = Get-Content "Community-Mod-Compilation-redux\json_blacklist" | Resolve-Path -Relative
  $files = Get-ChildItem -Recurse -Include *.json "Community-Mod-Compilation-redux\data" | Resolve-Path -Relative | ?{$blacklist -notcontains $_}
  $files | ForEach-Object { Invoke-Expression "Community-Mod-Compilation-redux\tools\format\json_formatter.exe $_" }
  Write-Output "JSON formatting script ends."
