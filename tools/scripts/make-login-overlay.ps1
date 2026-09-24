<#
.SYNOPSIS
  Generate the kRO-only login UI textures that jRO data.grf does not contain, as a *loose overlay*
  under the working copy (C:\RO-Lab\client\clientdata). Nothing under C:\Gravity is modified.

  Created files (data\texture\유저인터페이스\):
    login_interface\bg_login.tga          301x132  self-drawn login panel (uncompressed 32bit TGA)
    login_interface\bt_start_{normal,over,press}.bmp   84x84  self-drawn "Login" button
    login_interface\bt_join_{normal,over,press}.bmp    84x21  self-drawn small button
    t_배경1-1.bmp .. t_배경3-4.bmp          4x3 tiles sliced from the locally owned bgi_temp.bmp
                                          (fetched through ro-glue; local use only, not redistributed)
#>
param(
    [string]$OutRoot = "C:\RO-Lab\client\clientdata\data\texture\유저인터페이스",
    [string]$Glue = "http://127.0.0.1:8000/client/"
)
Add-Type -AssemblyName System.Drawing
$ErrorActionPreference = 'Stop'
$li = Join-Path $OutRoot 'login_interface'
New-Item -ItemType Directory -Path $li -Force | Out-Null

function New-Bitmap([int]$w, [int]$h, [scriptblock]$draw) {
    $bmp = New-Object System.Drawing.Bitmap $w, $h, ([System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = 'AntiAlias'; $g.TextRenderingHint = 'AntiAliasGridFit'
    & $draw $g $w $h
    $g.Dispose()
    return $bmp
}
function Save-Bmp($bmp, $path) { $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Bmp); $bmp.Dispose() }

# --- buttons -----------------------------------------------------------------
$font = New-Object System.Drawing.Font 'Arial', 11, ([System.Drawing.FontStyle]::Bold)
$fontS = New-Object System.Drawing.Font 'Arial', 8
$sf = New-Object System.Drawing.StringFormat; $sf.Alignment = 'Center'; $sf.LineAlignment = 'Center'
$states = @{ normal = '#3b6ea5'; over = '#4f8ad0'; press = '#2a4f78' }
foreach ($s in $states.Keys) {
    $c = [System.Drawing.ColorTranslator]::FromHtml($states[$s])
    $b = New-Bitmap 84 84 { param($g, $w, $h)
        $g.Clear([System.Drawing.Color]::Magenta)   # magenta = transparent key in RO UI
        $br = New-Object System.Drawing.SolidBrush $c
        $g.FillEllipse($br, 2, 2, $w - 5, $h - 5)
        $g.DrawEllipse([System.Drawing.Pens]::White, 2, 2, $w - 5, $h - 5)
        $g.DrawString('Login', $font, [System.Drawing.Brushes]::White, (New-Object System.Drawing.RectangleF 0, 0, $w, $h), $sf)
    }
    Save-Bmp $b (Join-Path $li "bt_start_$s.bmp")
    $b2 = New-Bitmap 84 21 { param($g, $w, $h)
        $g.Clear([System.Drawing.Color]::Magenta)
        $br = New-Object System.Drawing.SolidBrush $c
        $g.FillRectangle($br, 0, 0, $w, $h)
        $g.DrawRectangle([System.Drawing.Pens]::White, 0, 0, $w - 1, $h - 1)
    }
    Save-Bmp $b2 (Join-Path $li "bt_join_$s.bmp")
}

# --- bg_login.tga (301x132, uncompressed 32bpp, top-left origin) --------------
$panel = New-Object System.Drawing.Bitmap 301, 132, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$g = [System.Drawing.Graphics]::FromImage($panel)
$g.SmoothingMode = 'AntiAlias'; $g.TextRenderingHint = 'AntiAliasGridFit'
$g.Clear([System.Drawing.Color]::FromArgb(230, 24, 32, 48))
$g.DrawRectangle((New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(255, 200, 170, 90)), 2), 1, 1, 298, 129)
$g.DrawString('RO PreRE  -  Login', $font, [System.Drawing.Brushes]::Gold, 12, 10)
$white = [System.Drawing.Brushes]::White
foreach ($y in 39, 61) { $g.FillRectangle($white, 17, $y, 129, 18) }  # input boxes (match WinLoginV2.css)
$g.DrawString('ID', $fontS, [System.Drawing.Brushes]::Gainsboro, 150, 40)
$g.DrawString('PW', $fontS, [System.Drawing.Brushes]::Gainsboro, 150, 62)
$g.DrawString('keep', $fontS, [System.Drawing.Brushes]::Gainsboro, 95, 82)
$g.Dispose()
$tga = Join-Path $li 'bg_login.tga'
$fs = [IO.File]::Create($tga)
$bw = New-Object IO.BinaryWriter $fs
$bw.Write([byte]0); $bw.Write([byte]0); $bw.Write([byte]2)            # id len, no colormap, type 2 = uncompressed truecolor
$bw.Write([uint16]0); $bw.Write([uint16]0); $bw.Write([byte]0)        # colormap spec
$bw.Write([uint16]0); $bw.Write([uint16]0)                            # x/y origin
$bw.Write([uint16]$panel.Width); $bw.Write([uint16]$panel.Height)
$bw.Write([byte]32); $bw.Write([byte]0x28)                            # 32 bpp, 8 alpha bits + top-left origin
for ($y = 0; $y -lt $panel.Height; $y++) {
    for ($x = 0; $x -lt $panel.Width; $x++) {
        $p = $panel.GetPixel($x, $y)
        $bw.Write([byte]$p.B); $bw.Write([byte]$p.G); $bw.Write([byte]$p.R); $bw.Write([byte]$p.A)
    }
}
$bw.Dispose(); $fs.Dispose(); $panel.Dispose()

# --- background tiles from bgi_temp.bmp (via glue, read-only source) ----------
$src = Invoke-WebRequest -UseBasicParsing -Uri ($Glue + 'data/texture/' + [uri]::EscapeDataString('유저인터페이스') + '/bgi_temp.bmp')
$ms = New-Object IO.MemoryStream (, $src.Content)
$big = [System.Drawing.Image]::FromStream($ms)
"bgi_temp.bmp: $($big.Width)x$($big.Height)"
$tw = [int]($big.Width / 4); $th = [int]($big.Height / 3)
for ($r = 0; $r -lt 3; $r++) {
    for ($c = 0; $c -lt 4; $c++) {
        $tile = New-Object System.Drawing.Bitmap $tw, $th, ([System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
        $tg = [System.Drawing.Graphics]::FromImage($tile)
        $tg.DrawImage($big, (New-Object System.Drawing.Rectangle 0, 0, $tw, $th), (New-Object System.Drawing.Rectangle ($c * $tw), ($r * $th), $tw, $th), 'Pixel')
        $tg.Dispose()
        Save-Bmp $tile (Join-Path $OutRoot ("t_배경{0}-{1}.bmp" -f ($r + 1), ($c + 1)))
    }
}
$big.Dispose()
Get-ChildItem $OutRoot -Recurse -File | Select-Object @{n = 'File'; e = { $_.FullName.Replace($OutRoot, '') } }, Length | Format-Table -AutoSize
