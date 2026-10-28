# install_all.ps1 - Sequential installer with retry logic
Write-Host "=== Citation Parser - Full Install ===" -ForegroundColor Cyan

$pip = ".\venv\Scripts\pip"
$flags = @("--prefer-binary", "--timeout", "180", "--retries", "5")

$groups = @(
    @("pydantic", "pydantic-settings"),
    @("fastapi", "uvicorn[standard]", "python-multipart"),
    @("httpx", "openai", "aiofiles", "regex", "python-dotenv"),
    @("pdfplumber"),
    @("PyMuPDF"),
    @("pytest", "pytest-asyncio", "httpx")
)

foreach ($group in $groups) {
    $names = $group -join ", "
    Write-Host "`n[+] Installing: $names" -ForegroundColor Yellow
    $args = @("install") + $flags + $group
    & $pip @args
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Warning: Some packages may have had issues, continuing..." -ForegroundColor DarkYellow
    } else {
        Write-Host "  OK" -ForegroundColor Green
    }
}

Write-Host "`n=== Verifying installs ===" -ForegroundColor Cyan
& .\venv\Scripts\python -c "import fastapi, pydantic, pdfplumber, openai, httpx; print('All core imports OK')"

Write-Host "`n=== Running Tests ===" -ForegroundColor Cyan
& .\venv\Scripts\pytest tests/test_doi_parser.py tests/test_metadata_parser.py tests/test_bibtex_generator.py -v --tb=short

Write-Host "`n=== Starting Server ===" -ForegroundColor Cyan
Write-Host "Server: http://localhost:8000" -ForegroundColor Green
Write-Host "Docs:   http://localhost:8000/docs" -ForegroundColor Green
& .\venv\Scripts\python main.py
