# grf-inspect.ps1 - GRF 繝倥ャ繝/繝輔ぃ繧､繝ｫ繝・・繝悶Ν縺ｮ隱ｭ縺ｿ蜿悶ｊ蟆ら畑隗｣譫・
# 逕ｨ騾・ 繝ｭ繝ｼ繧ｫ繝ｫ縺ｫ豁｣隕乗園譛峨＠縺ｦ縺・ｋ GRF 縺ｮ讒矩莠呈鋤諤ｧ繧堤｢ｺ隱阪☆繧具ｼ域歓蜃ｺ繝ｻ譖ｸ縺崎ｾｼ縺ｿ縺ｯ陦後ｏ縺ｪ縺・ｼ・
param(
    [Parameter(Mandatory = $true)][string]$Path,
    [string[]]$Probe = @(),
    [switch]$DumpProbeText
)

$ErrorActionPreference = 'Stop'
$fs = [IO.File]::Open($Path, 'Open', 'Read', 'Read')
$br = New-Object IO.BinaryReader($fs)

try {
    # --- header (46 bytes) ---
    $sig = [Text.Encoding]::ASCII.GetString($br.ReadBytes(15))
    $nul = $sig.IndexOf([char]0); if ($nul -ge 0) { $sig = $sig.Substring(0, $nul) }
    $key = $br.ReadBytes(15)
    $tableOffset = $br.ReadUInt32()
    $skip = $br.ReadUInt32()
    $fileCountRaw = $br.ReadUInt32()
    $version = $br.ReadUInt32()

    Write-Host "File        : $Path"
    Write-Host ("Size        : {0:N0} bytes" -f $fs.Length)
    Write-Host "Signature   : '$sig'"
    Write-Host ("Key bytes   : {0}" -f (($key | ForEach-Object { $_.ToString('X2') }) -join ' '))
    Write-Host ("Version     : 0x{0:X}" -f $version)
    Write-Host ("TableOffset : 0x{0:X} (+46 = 0x{1:X})" -f $tableOffset, ($tableOffset + 46))
    Write-Host "Skip        : $skip"
    Write-Host "FileCountRaw: $fileCountRaw"

    if ($sig -ne 'Master of Magic' -and $sig -ne 'Event Horizon') { throw "Unexpected signature '$sig'" }
    if ($version -ne 0x200 -and $version -ne 0x300) { throw ("Unsupported version 0x{0:X} (this script handles 0x200 / 0x300 only)" -f $version) }

    $is300 = ($version -eq 0x300)
    if ($is300) {
        # 0x300: offset 30 = UInt64 file_table_offset, offset 38 = UInt32 filecount (raw count is the real count)
        $fs.Seek(30, 'Begin') | Out-Null
        $tableOffset64 = $br.ReadUInt64()
        $fileCount = $br.ReadUInt32()
        Write-Host ("TableOffset64: 0x{0:X}" -f $tableOffset64)
        $tableStart = [int64]$tableOffset64 + 46 + 4   # 0x300 has an extra Int32 before the table
    } else {
        $fileCount = $fileCountRaw - $skip - 7
        $tableStart = [int64]$tableOffset + 46
    }
    Write-Host "FileCount   : $fileCount"

    # --- file table ---
    $fs.Seek($tableStart, 'Begin') | Out-Null
    $packSize = $br.ReadUInt32()
    $realSize = $br.ReadUInt32()
    Write-Host ("Table       : packed={0:N0} real={1:N0}" -f $packSize, $realSize)

    $packed = $br.ReadBytes([int]$packSize)
    Write-Host ("Table zlib  : {0:X2} {1:X2}" -f $packed[0], $packed[1])
    if ($packed[0] -ne 0x78) { throw "Table is not zlib-compressed (custom encryption?)" }

    $ms = New-Object IO.MemoryStream -ArgumentList @($packed, 2, ($packed.Length - 2))
    $ds = New-Object IO.Compression.DeflateStream($ms, [IO.Compression.CompressionMode]::Decompress)
    $table = New-Object byte[] $realSize
    $read = 0
    while ($read -lt $realSize) {
        $n = $ds.Read($table, $read, $realSize - $read)
        if ($n -le 0) { break }
        $read += $n
    }
    $ds.Close()
    Write-Host "Table read  : $read / $realSize"

    # --- parse entries ---
    $entries = New-Object System.Collections.Generic.List[object]
    $pos = 0
    $typeHist = @{}
    $nonAsciiNames = 0
    $extHist = @{}
    $topDirs = @{}
    $euckr = [Text.Encoding]::GetEncoding(949)
    $cp932 = [Text.Encoding]::GetEncoding(932)

    for ($i = 0; $i -lt $fileCount; $i++) {
        $start = $pos
        while ($table[$pos] -ne 0) { $pos++ }
        $nameBytes = $table[$start..($pos - 1)]
        $pos++
        $ps = [BitConverter]::ToUInt32($table, $pos); $pos += 4
        $la = [BitConverter]::ToUInt32($table, $pos); $pos += 4
        $rs = [BitConverter]::ToUInt32($table, $pos); $pos += 4
        $ty = $table[$pos]; $pos += 1
        if ($is300) {
            $of = [BitConverter]::ToUInt64($table, $pos); $pos += 8
        } else {
            $of = [uint64][BitConverter]::ToUInt32($table, $pos); $pos += 4
        }

        $hasHigh = $false
        foreach ($b in $nameBytes) { if ($b -gt 0x7F) { $hasHigh = $true; break } }
        if ($hasHigh) { $nonAsciiNames++ }

        $nameLatin = [Text.Encoding]::GetEncoding(28591).GetString($nameBytes)
        $typeHist[$ty] = 1 + $(if ($typeHist.ContainsKey($ty)) { $typeHist[$ty] } else { 0 })
        $ext = [IO.Path]::GetExtension($nameLatin).ToLower()
        $extHist[$ext] = 1 + $(if ($extHist.ContainsKey($ext)) { $extHist[$ext] } else { 0 })
        $top = ($nameLatin -split '\\')[0].ToLower()
        $topDirs[$top] = 1 + $(if ($topDirs.ContainsKey($top)) { $topDirs[$top] } else { 0 })

        $entries.Add([pscustomobject]@{
            NameBytes = $nameBytes; NameLatin = $nameLatin; NameEucKr = $euckr.GetString($nameBytes); NameCp932 = $cp932.GetString($nameBytes)
            PackSize = $ps; LenAligned = $la; RealSize = $rs; Type = $ty; Offset = $of
        })
    }

    Write-Host ""
    Write-Host "=== Entry type flags (0x01=file, 0x02=mixed DES, 0x04=header DES) ==="
    foreach ($k in ($typeHist.Keys | Sort-Object)) { Write-Host ("  type 0x{0:X2}: {1:N0}" -f $k, $typeHist[$k]) }
    Write-Host "Non-ASCII filenames: $nonAsciiNames / $fileCount"
    Write-Host ""
    Write-Host "=== Top-level dirs ==="
    foreach ($k in ($topDirs.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 15)) { Write-Host ("  {0,-30} {1:N0}" -f $k.Key, $k.Value) }
    Write-Host ""
    Write-Host "=== Extensions (top 20) ==="
    foreach ($k in ($extHist.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 20)) { Write-Host ("  {0,-8} {1:N0}" -f $k.Key, $k.Value) }

    # --- filename encoding sample ---
    Write-Host ""
    Write-Host "=== Non-ASCII filename samples (bytes -> EUC-KR / CP932 interpretation) ==="
    $shown = 0
    foreach ($e in $entries) {
        $hasHigh = $false
        foreach ($b in $e.NameBytes) { if ($b -gt 0x7F) { $hasHigh = $true; break } }
        if ($hasHigh) {
            Write-Host ("  EUC-KR: {0}" -f $e.NameEucKr)
            Write-Host ("  CP932 : {0}" -f $e.NameCp932)
            Write-Host "  --"
            $shown++
            if ($shown -ge 6) { break }
        }
    }

    # --- probes ---
    if ($Probe.Count -gt 0) {
        Write-Host ""
        Write-Host "=== Probe files ==="
        foreach ($p in $Probe) {
            $hit = $entries | Where-Object { $_.NameLatin.ToLower() -eq $p.ToLower() } | Select-Object -First 1
            if ($hit) {
                Write-Host ("  FOUND  {0}  type=0x{1:X2} real={2:N0} packed={3:N0}" -f $p, $hit.Type, $hit.RealSize, $hit.PackSize)
                if ($DumpProbeText -and $hit.Type -eq 0x01 -and $hit.RealSize -lt 65536) {
                    $fs.Seek([int64]$hit.Offset + 46, 'Begin') | Out-Null
                    $blob = $br.ReadBytes([int]$hit.LenAligned)
                    if ($blob[0] -eq 0x78) {
                        $ms2 = New-Object IO.MemoryStream -ArgumentList @($blob, 2, ($blob.Length - 2))
                        $ds2 = New-Object IO.Compression.DeflateStream($ms2, [IO.Compression.CompressionMode]::Decompress)
                        $out = New-Object byte[] $hit.RealSize
                        $r2 = 0
                        while ($r2 -lt $hit.RealSize) { $n2 = $ds2.Read($out, $r2, $hit.RealSize - $r2); if ($n2 -le 0) { break }; $r2 += $n2 }
                        $ds2.Close()
                        $bom = if ($out[0] -eq 0xEF -and $out[1] -eq 0xBB) { 'UTF-8 BOM' } elseif ($out[0] -eq 0xFF -and $out[1] -eq 0xFE) { 'UTF-16LE BOM' } else { 'no BOM' }
                        Write-Host ("         [{0}] first bytes: {1}" -f $bom, (($out[0..([Math]::Min(15, $out.Length - 1))] | ForEach-Object { $_.ToString('X2') }) -join ' '))
                        Write-Host "         ----- content (CP932 decode, first 1200 chars) -----"
                        $txt = $cp932.GetString($out)
                        Write-Host ($txt.Substring(0, [Math]::Min(1200, $txt.Length)))
                        Write-Host "         ----- end -----"
                    } else {
                        Write-Host ("         first bytes: {0}  (not zlib -> encrypted/custom?)" -f (($blob[0..7] | ForEach-Object { $_.ToString('X2') }) -join ' '))
                    }
                }
            } else {
                Write-Host "  MISSING $p"
            }
        }
    }

    # --- prefix search helper output: count matches for wildcard prefixes ---
    Write-Host ""
    Write-Host "=== Prefix counts ==="
    foreach ($pre in @('data\luafiles514\', 'data\texture\', 'data\sprite\', 'data\model\', 'data\wav\', 'data\imf\', 'data\palette\', 'system\', 'data\luafiles514\lua files\datainfo\', 'data\luafiles514\lua files\skillinfoz\')) {
        $c = ($entries | Where-Object { $_.NameLatin.ToLower().StartsWith($pre) }).Count
        Write-Host ("  {0,-45} {1:N0}" -f $pre, $c)
    }
    $maps = ($entries | Where-Object { $_.NameLatin.ToLower() -match '^data\\[^\\]+\.rsw$' }).Count
    Write-Host ("  {0,-45} {1:N0}" -f 'data\*.rsw (maps)', $maps)

    # --- encrypted-entry breakdown ---
    Write-Host ""
    Write-Host "=== Encrypted entries (type has 0x02 or 0x04) by extension (top 15) ==="
    $encExt = @{}
    $encUI = 0; $encLua = 0; $encMap = 0; $encTex = 0; $encSpr = 0; $encTotal = 0
    $uiPrefix = [Text.Encoding]::GetEncoding(28591).GetString([Text.Encoding]::GetEncoding(949).GetBytes('data\texture\유저인터페이스\')).ToLower()
    foreach ($e in $entries) {
        if (($e.Type -band 0x06) -ne 0) {
            $encTotal++
            $x = [IO.Path]::GetExtension($e.NameLatin).ToLower()
            $encExt[$x] = 1 + $(if ($encExt.ContainsKey($x)) { $encExt[$x] } else { 0 })
            $n = $e.NameLatin.ToLower()
            if ($n.StartsWith($uiPrefix)) { $encUI++ }
            if ($n.StartsWith('data\luafiles514\')) { $encLua++ }
            if ($n -match '^data\\[^\\]+\.(rsw|gnd|gat)$') { $encMap++ }
            if ($n.StartsWith('data\texture\')) { $encTex++ }
            if ($n.StartsWith('data\sprite\')) { $encSpr++ }
        }
    }
    foreach ($k in ($encExt.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 15)) { Write-Host ("  {0,-8} {1:N0}" -f $k.Key, $k.Value) }
    Write-Host ("  encrypted total                            : {0:N0}" -f $encTotal)
    Write-Host ("  encrypted in data\texture\(UI dir)         : {0:N0}" -f $encUI)
    Write-Host ("  encrypted in data\luafiles514\            : {0:N0}" -f $encLua)
    Write-Host ("  encrypted map files (rsw/gnd/gat)          : {0:N0}" -f $encMap)
    Write-Host ("  encrypted in data\texture\                : {0:N0}" -f $encTex)
    Write-Host ("  encrypted in data\sprite\                 : {0:N0}" -f $encSpr)
}
finally {
    $br.Close(); $fs.Close()
}
