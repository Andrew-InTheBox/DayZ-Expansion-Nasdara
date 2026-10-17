# Wipe Nasdara mission persistence only after stopping the server.
$basePath = [IO.Path]::GetFullPath($PSScriptRoot)
$storage = [IO.Path]::GetFullPath((Join-Path $basePath 'mpmissions\expansion.nasdara\storage_1'))
if (-not $storage.StartsWith($basePath + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Storage path is outside this server folder.'
}
if (-not (Test-Path -LiteralPath $storage)) {
    Write-Host 'No Nasdara mission storage found.'
    exit
}
$confirmation = Read-Host "Delete Nasdara mission persistence in $storage? Type yes to continue"
if ($confirmation -ne 'yes') {
    Write-Host 'Cancelled.'
    exit
}
Get-ChildItem -LiteralPath $storage -Force | Remove-Item -Recurse -Force
Write-Host 'Nasdara mission persistence cleared.'
