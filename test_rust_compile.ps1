# Test script to verify Rust compilation works after installing Visual Studio Build Tools
Write-Host "Testing Rust compilation..." -ForegroundColor Green

cd optimization_program

# Clean previous build attempts
if (Test-Path "target") {
    Write-Host "Cleaning previous build..." -ForegroundColor Yellow
    cargo clean
}

# Try to compile
Write-Host "Attempting to compile Rust project..." -ForegroundColor Green
cargo build --release

if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS! Rust compilation working!" -ForegroundColor Green
    Write-Host "Binary location: target\release\optimization_program.exe" -ForegroundColor Cyan
} else {
    Write-Host "FAILED! Rust compilation still not working." -ForegroundColor Red
    Write-Host "Make sure you restarted PowerShell after installing Visual Studio Build Tools" -ForegroundColor Yellow
}

cd ..

