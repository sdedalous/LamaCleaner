param(
    [string]$maskBase64
)

if (-not $maskBase64) {
    Write-Error "Please provide the Base64 mask string as the -maskBase64 parameter."
    exit 1
}

try {
    $body = @{ mask_base64 = $maskBase64 } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri http://127.0.0.1:8000/inpaint -Method POST -ContentType "application/json" -Body $body

    if ($response.ok -eq $true) {
        Write-Host "Works: Output saved to $($response.output_path)"
    } else {
        Write-Host "Doesn't work: $($response.error)"
    }
} catch {
    Write-Host "Request failed: $_"
}

# Usage example:
# Save your Base64 mask string (including the 'data:image/png;base64,' prefix) into a text file, e.g. C:\Users\stebe\Documents\test_text.txt
# Then run this script like:
# $maskBase64 = Get-Content -Raw -Path "C:\Users\stebe\Documents\test_text.txt"
# .\test_inpaint.ps1 -maskBase64 $maskBase64
