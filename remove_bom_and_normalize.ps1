# remove_bom_and_normalize.ps1
$root = Join-Path (Get-Location) "docs"
if (-not (Test-Path $root)) { Write-Error "docs フォルダが見つかりません"; exit 1 }

$encNoBom = New-Object System.Text.UTF8Encoding($false)  # ← これが BOM なしUTF-8
$fixed = 0; $scanned = 0; $bomRemoved = 0

Get-ChildItem $root -Recurse -Include *.md | ForEach-Object {
  $scanned++
  $p = $_.FullName
  $bytes = [IO.File]::ReadAllBytes($p)

  $hadBom = $false
  if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    # ★ 先頭3バイト（BOM）を物理的に削除
    [IO.File]::WriteAllBytes("$p.bak", $bytes)  # バックアップ
    $bytes = $bytes[3..($bytes.Length-1)]
    $hadBom = $true
    $bomRemoved++
  }

  # テキスト化 → 改行を LF に統一 → BOMなしUTF-8 で保存
  $text = [Text.Encoding]::UTF8.GetString($bytes)
  $text = $text -replace "`r`n","`n" -replace "`r","`n"
  $newBytes = $encNoBom.GetBytes($text)

  if ($hadBom -or -not [System.Linq.Enumerable]::SequenceEqual($bytes, $newBytes)) {
    # （BOM削除だけでなく、改行の変更や再エンコードも含めて）更新がある場合のみ上書き
    [IO.File]::WriteAllBytes($p, $newBytes)
    Write-Host "[fixed] $p"
    $fixed++
  }
}

Write-Host "`nScanned : $scanned"
Write-Host "BOM removed in : $bomRemoved file(s)"
Write-Host "Updated : $fixed file(s) (BOM除去/改行LF/UTF-8無BOMで保存)"
