# Script PowerShell para contar elementos det no XML
$xmlPath = "c:\Users\enzoa\Downloads\xml girassol (1).XML"

try {
    Write-Host "Lendo arquivo XML..."
    $xml = [xml](Get-Content $xmlPath)
    
    # Contar elementos det
    $dets = $xml.GetElementsByTagName('det')
    Write-Host "Total de elementos <det> encontrados: $($dets.Count)"
    
    # Contar elementos prod
    $prods = $xml.GetElementsByTagName('prod')
    Write-Host "Total de elementos <prod> encontrados: $($prods.Count)"
    
    # Listar os primeiros 5 produtos
    Write-Host "`nPrimeiros 5 produtos:"
    for ($i = 0; $i -lt [Math]::Min(5, $prods.Count); $i++) {
        $prod = $prods[$i]
        $codigo = $prod.GetElementsByTagName('cProd')[0].InnerText
        $descricao = $prod.GetElementsByTagName('xProd')[0].InnerText
        $quantidade = $prod.GetElementsByTagName('qCom')[0].InnerText
        Write-Host "  $($i+1). Código: $codigo | Qtd: $quantidade | Descrição: $descricao"
    }
    
} catch {
    Write-Host "Erro ao processar XML: $_"
}
