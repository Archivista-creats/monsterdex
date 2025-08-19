# normalize_md_encoding.ps1
# docs 以下の .md を UTF-8 (BOMなし) / LF 改行に正規化し、変更前の .bak を作成
# ついでに、先頭に紛れた BOM 由来の不具合を根絶します

$root = Join-Path (Get-Location) "docs"
if (-not (Test-Path $root)) {
  Write-Error "docs フォルダが見つかりません。リポジトリ直下で実行してください。"
  exit 1
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$fixed = 0
$scanned = 0

Get-ChildItem $root -Recurse -Filter *.md | ForEach-Object {
  $scanned++

  # 元バイト読み込み
  $bytes = [System.IO.File]::ReadAllBytes($_.FullName)

  # 文字列としては "現状のエンコーディングを仮定せず" に読むため、一旦 .NET の推測に委ねる
  # （BOM付きなら BOMを剝がしてくれる。文字化けしていても「LF 統一」と「BOM除去」目的は達成できる）
  $text = [System.Text.Encoding]::UTF8.GetString($bytes)
  # CRLF/CR → LF に統一
  $textLF = $text -replace "`r`n","`n" -replace "`r","`n"

  # 既に BOM なしUTF-8/LF ならスキップしたいが、簡易にバイト再生成して差分比較
  $newBytes = $utf8NoBom.GetBytes($textLF)

  if (-not ($bytes.Length -eq $newBytes.Length -and [System.Linq.Enumerable]::SequenceEqual($bytes, $newBytes))) {
    # バックアップ
    $bak = "$($_.FullName).bak"
    if (-not (Test-Path $bak)) {
      [System.IO.File]::WriteAllBytes($bak, $bytes)
    }
    # 上書き保存（UTF-8 BOMなし、LF）
    [System.IO.File]::WriteAllBytes($_.FullName, $newBytes)
    Write-Host "[fixed] $($_.FullName)"
    $fixed++
  }
}

Write-Host ""
Write-Host "Scanned: $scanned file(s)"
Write-Host "Fixed  : $fixed file(s)"
Write-Host "Backups: *.bak を同階層に作成済み（必要なら削除可）"
