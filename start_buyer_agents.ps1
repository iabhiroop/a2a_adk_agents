# PowerShell script to start only the buyer agents
Write-Host "Starting Buyer Agents..." -ForegroundColor Green

Write-Host "Starting Individual Buyer Agents..." -ForegroundColor Yellow
Write-Host "Starting Inventory Management Agent..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '.\inventory_management_agent'; python __main__.py" -WindowStyle Normal
Start-Sleep 3

Write-Host "Starting Purchase Validation Agent..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '.\purchase_validation_agent'; python __main__.py" -WindowStyle Normal
Start-Sleep 3

Write-Host "Starting Purchase Order Agent..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '.\purchase_order_agent'; python __main__.py" -WindowStyle Normal
Start-Sleep 3

Write-Host "Starting Buyer Orchestrator Agent..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '.\buyer_orchestrator_agent'; python __main__.py" -WindowStyle Normal

Write-Host "All buyer agents started!" -ForegroundColor Green
Write-Host ""
Write-Host "Buyer Agent URLs:" -ForegroundColor Cyan
Write-Host "- Inventory Management: http://localhost:8088" -ForegroundColor White
Write-Host "- Purchase Validation: http://localhost:8089" -ForegroundColor White
Write-Host "- Purchase Order: http://localhost:8090" -ForegroundColor White
Write-Host "- Buyer Orchestrator: http://localhost:8093" -ForegroundColor White
Write-Host ""
Write-Host ""
Read-Host "Press Enter to exit"
