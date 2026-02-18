taskkill /F /IM python.exe /IM node.exe 2>$null; Start-Sleep -Seconds 2; "Processes killed"

taskkill /F /IM node.exe 2>$null; Start-Sleep -Seconds 2; "Frontend stopped"

uvicorn app.main:app --reload