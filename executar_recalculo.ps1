# Script PowerShell para executar o endpoint de recalculculo de precos via API

$BASE_URL = "https://higiplas-system.onrender.com"
$EMAIL = "enzo.alverde@gmail.com"
$SENHA = "senha123"

Write-Host "Fazendo login..." -ForegroundColor Cyan

# Fazer login
$loginBody = @{
    username = $EMAIL
    password = $SENHA
}

try {
    $loginResponse = Invoke-RestMethod -Uri "$BASE_URL/users/token" -Method Post -Body $loginBody -ContentType "application/x-www-form-urlencoded"
    
    $token = $loginResponse.access_token
    
    if (-not $token) {
        Write-Host "ERRO: Token nao recebido" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Login realizado com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executando recalculculo de ranges de precos..." -ForegroundColor Cyan
    
    # Executar recálculo
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    
    $recalculoResponse = Invoke-RestMethod -Uri "$BASE_URL/orcamentos/admin/recalcular-precos" -Method Post -Headers $headers
    
    Write-Host ""
    Write-Host "Recalculculo concluido com sucesso!" -ForegroundColor Green
    Write-Host "   - Orcamentos processados: $($recalculoResponse.orcamentos_processados)" -ForegroundColor Yellow
    Write-Host "   - Clientes processados: $($recalculoResponse.clientes_processados)" -ForegroundColor Yellow
    Write-Host "   - Registros atualizados: $($recalculoResponse.registros_precos_atualizados)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Processo concluido! Os ranges de precos agora devem aparecer no frontend." -ForegroundColor Green
    
} catch {
    Write-Host ""
    Write-Host "ERRO ao executar:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    }
    exit 1
}

