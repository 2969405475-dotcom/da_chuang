$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot "venv\Scripts\python.exe"
$EntryPoint = Join-Path $ProjectRoot "src\benes\app.py"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "venv not found. Create the Python 3.11 environment and install requirements-dev.txt."
}

Push-Location $ProjectRoot
try {
    & $Python -m PyInstaller `
        --noconfirm `
        --clean `
        --windowed `
        --onedir `
        --name BenesPathPlanner `
        --paths src `
        --distpath dist\onedir `
        --workpath build\onedir `
        --specpath build\onedir `
        $EntryPoint
    if ($LASTEXITCODE -ne 0) {
        throw "The onedir build failed."
    }

    & $Python -m PyInstaller `
        --noconfirm `
        --clean `
        --windowed `
        --onefile `
        --name BenesPathPlanner `
        --paths src `
        --distpath dist `
        --workpath build\onefile `
        --specpath build\onefile `
        $EntryPoint
    if ($LASTEXITCODE -ne 0) {
        throw "The onefile build failed."
    }
}
finally {
    Pop-Location
}

Write-Host "Build complete: dist\BenesPathPlanner.exe"
