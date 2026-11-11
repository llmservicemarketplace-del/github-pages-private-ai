param(
  [string]$Repo = (Get-Location).Path,
  [string]$Url = '',          # Zeffy donate URL; auto-detected from the site if blank
  [switch]$DryRun,
  [switch]$Remove             # take the box back out of every page
)
$ErrorActionPreference = 'Stop'
$utf8 = New-Object System.Text.UTF8Encoding($false)
$dirs = 'disaster-recovery','health-help','money-help','moving-on'
$files = foreach ($d in $dirs) { $p = Join-Path $Repo $d; if (Test-Path $p) { Get-ChildItem $p -Recurse -Filter *.html } }
$start = '<!-- nfccop-donate -->'; $end = '<!-- /nfccop-donate -->'

if ($Remove) {
  $n = 0
  foreach ($f in $files) {
    $h = [IO.File]::ReadAllText($f.FullName, $utf8)
    if ($h.Contains($start)) {
      $h = [regex]::Replace($h, '(?s)\r?\n?' + [regex]::Escape($start) + '.*?' + [regex]::Escape($end) + '\r?\n?', "`n")
      if (-not $DryRun) { [IO.File]::WriteAllText($f.FullName, $h, $utf8) }; $n++
    }
  }
  Write-Host "Removed donate box from $n page(s)."; return
}

# Find the Zeffy link already on the site
if (-not $Url) {
  $hits = Get-ChildItem $Repo -Recurse -Include *.html -File | Where-Object { $_.FullName -notmatch '\\(\.git|node_modules|_[^\\]+)\\' } |
    Select-String -Pattern 'https://(www\.)?zeffy\.com/[^"''\s<>]+' -AllMatches |
    ForEach-Object { $_.Matches.Value } | Group-Object | Sort-Object Count -Descending
  if (-not $hits) { throw 'No zeffy.com link found in the site. Re-run with -Url "https://www.zeffy.com/..."' }
  $hits | Select-Object -First 5 | ForEach-Object { Write-Host ("  found {0}x  {1}" -f $_.Count, $_.Name) }
  $Url = $hits[0].Name
}
Write-Host "Using donate link: $Url"

# Does the conversion script already treat Zeffy clicks as Donate?
$bc = Join-Path $Repo 'button-conversions.js'
if (Test-Path $bc) {
  $js = [IO.File]::ReadAllText($bc, $utf8)
  if ($js -match '(?i)zeffy|donate') { Write-Host "button-conversions.js mentions zeffy/donate -- Donate conversion should fire." }
  else { Write-Warning "button-conversions.js has no zeffy/donate rule. Send me that file and I'll add one." }
}

$box = @"
$start
<aside class="nfccop-donate" aria-label="Support these free guides" style="margin:28px 0;padding:18px 18px 16px;border:2px solid #163432;border-radius:12px;background:#f2f8f7">
  <p style="margin:0 0 6px;font-size:1.15em;font-weight:700;color:#163432">This guide is free. Help keep it free.</p>
  <p style="margin:0 0 12px">These guides are written and kept up to date by The New Faith Church and Co-op, Inc. (NFCcop), a small 501(c)(3) nonprofit. No paywall, no sign-up. If this page helped you or someone you love, a gift keeps it online for the next family.</p>
  <p style="margin:0 0 10px;display:flex;flex-wrap:wrap;gap:8px">
    <a href="$Url" target="_blank" rel="noopener" data-event="donate_click" class="nfccop-donate-btn" style="display:inline-block;padding:10px 18px;border-radius:8px;background:#163432;color:#fff;font-weight:700;text-decoration:none">Donate</a>
    <a href="$Url" target="_blank" rel="noopener" data-event="donate_click" class="nfccop-donate-btn" style="display:inline-block;padding:10px 18px;border-radius:8px;border:2px solid #163432;color:#163432;font-weight:700;text-decoration:none">Give monthly</a>
  </p>
  <p style="margin:0;font-size:.85em;color:#4a5a59">Secure giving through Zeffy. 100% of your gift goes to NFCcop. Donations are tax-deductible to the extent allowed by law.</p>
</aside>
$end
"@

$rx = [regex]'(?i)<h2[^>]*>\s*(Frequently asked|FAQ|Common questions|Questions people ask|Official sources|Sources|Related)'
$added = 0; $skipped = 0
foreach ($f in $files) {
  if ($f.Name -eq 'offline.html') { continue }
  $h = [IO.File]::ReadAllText($f.FullName, $utf8)
  if ($h.Contains($start)) { $skipped++; continue }
  $m = $rx.Match($h)
  if ($m.Success) { $h = $h.Insert($m.Index, "$box`n") }
  elseif ($h -match '(?i)</main>') { $h = $h.Insert($h.ToLower().LastIndexOf('</main>'), "$box`n") }
  else { Write-Warning "no insert point: $($f.FullName.Substring($Repo.Length))"; continue }
  if (-not $DryRun) { [IO.File]::WriteAllText($f.FullName, $h, $utf8) }
  $added++
}
Write-Host "$(if($DryRun){'[dry run] would add'}else{'Added'}) donate box to $added page(s); $skipped already had it."
