$ErrorActionPreference = 'Stop'
$docxPath = (Resolve-Path 'output\Reporte_Funcionalidad_TANK650_T160MB.docx').Path
$pdfPath = Join-Path (Split-Path $docxPath -Parent) 'Reporte_Funcionalidad_TANK650_T160MB.pdf'
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $document = $word.Documents.Open($docxPath, $false, $true)
    try {
        $document.ExportAsFixedFormat($pdfPath, 17)
    }
    finally {
        $document.Close($false)
    }
}
finally {
    $word.Quit()
}
Write-Output $pdfPath
