# Run all source checks without starting services or calling Gemini.
$ErrorActionPreference='Stop'
$projectDirectory=Split-Path -Parent $PSScriptRoot
Push-Location (Join-Path $projectDirectory 'frontend')
try {
 npm run check
 if ($LASTEXITCODE -ne 0) { throw 'Frontend checks failed' }
 npm run build
 if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed' }
} finally { Pop-Location }
Push-Location (Join-Path $projectDirectory 'backend')
try {
 & './.venv/Scripts/python.exe' -m ruff check app main.py tests
 if ($LASTEXITCODE -ne 0) { throw 'Backend lint failed' }
 & './.venv/Scripts/python.exe' -m ruff format --check app main.py tests
 if ($LASTEXITCODE -ne 0) { throw 'Backend format check failed' }
 & './.venv/Scripts/python.exe' -m pytest -q
 if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed' }
} finally { Pop-Location }
