$files = @(
  ".\assets\js\brython.js",
  ".\assets\js\brython_modules.js",
  ".\assets\js\brython_stdlib.js",
  ".\assets\js\app.js"
)
foreach ($file in $files) {
  if (Test-Path $file) {
    Remove-Item $file -Force
    Write-Host "Removido: $file"
  }
}
