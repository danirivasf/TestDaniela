<#
.SYNOPSIS
    One-command bootstrap for KM provisioning. Checks prerequisites, walks you
    through Microsoft 365 login, verifies it, then launches Claude Code with the
    provisioning runbook loaded.

.DESCRIPTION
    Run this instead of typing the setup commands by hand. It runs each step in
    order and stops on the first real failure with a specific next action, so a
    Conditional Access refusal is reported as such rather than cascading into
    confusing downstream errors.

.EXAMPLE
    .\Start-KMProvisioning.ps1

.EXAMPLE
    .\Start-KMProvisioning.ps1 -SkipLogin
    Skips login if you are already authenticated.
#>

[CmdletBinding()]
param(
    [switch]$SkipLogin,
    [switch]$ReadOnly,
    [string]$Runbook = "m365-knowledge-architecture/provisioning/LOCAL-RUNBOOK.md"
)

$ErrorActionPreference = 'Stop'
$mcp = '@softeria/ms-365-mcp-server'

function Write-Step  { param($n, $t) Write-Host "`n[$n] $t" -ForegroundColor Cyan }
function Write-Ok    { param($t) Write-Host "  OK  $t" -ForegroundColor Green }
function Write-Warn2 { param($t) Write-Host "  !   $t" -ForegroundColor Yellow }
function Write-Fail  { param($t) Write-Host "  X   $t" -ForegroundColor Red }

function Test-Command {
    param([string]$Name)
    $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

Write-Host ""
Write-Host "  KM Provisioning Bootstrap" -ForegroundColor White
Write-Host "  Target: https://octaveint.sharepoint.com/sites/DaniandEthan" -ForegroundColor Gray
Write-Host ""

# -- 1. Repo location ----------------------------------------------------------

Write-Step 1 "Checking repository"

# Allow running from either the repo root or the provisioning folder.
if (-not (Test-Path $Runbook)) {
    $up = Join-Path $PSScriptRoot "..\.."
    if (Test-Path (Join-Path $up $Runbook)) {
        Set-Location $up
        Write-Warn2 "Changed directory to repo root: $(Get-Location)"
    } else {
        Write-Fail "Cannot find $Runbook"
        Write-Host "     Run this from the TestDaniela repo root, or from" -ForegroundColor Gray
        Write-Host "     m365-knowledge-architecture/provisioning/." -ForegroundColor Gray
        exit 1
    }
}
Write-Ok "Runbook found"

$branch = (git rev-parse --abbrev-ref HEAD 2>$null)
if ($branch -and $branch -ne 'claude/m365-knowledge-automation-a7ahvl') {
    Write-Warn2 "On branch '$branch', expected 'claude/m365-knowledge-automation-a7ahvl'"
    Write-Host "     Switch with: git checkout claude/m365-knowledge-automation-a7ahvl" -ForegroundColor Gray
} elseif ($branch) {
    Write-Ok "On branch $branch"
}

# -- 2. Prerequisites ----------------------------------------------------------

Write-Step 2 "Checking prerequisites"

if (-not (Test-Command 'node')) {
    Write-Fail "Node.js is not installed"
    Write-Host "     Install it from https://nodejs.org (LTS), reopen PowerShell, re-run." -ForegroundColor Gray
    exit 1
}

$nodeVersion = (node --version)
$nodeMajor = [int](($nodeVersion -replace '^v','').Split('.')[0])
if ($nodeMajor -lt 18) {
    Write-Fail "Node $nodeVersion found; the MCP server needs Node 18 or newer"
    Write-Host "     Update from https://nodejs.org, reopen PowerShell, re-run." -ForegroundColor Gray
    exit 1
}
Write-Ok "Node $nodeVersion"

if (-not (Test-Command 'claude')) {
    Write-Warn2 "Claude Code CLI not found - installing"
    npm install -g @anthropic-ai/claude-code
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Install failed"
        Write-Host "     Try manually: npm install -g @anthropic-ai/claude-code" -ForegroundColor Gray
        Write-Host "     If it is a permissions error, reopen PowerShell as Administrator." -ForegroundColor Gray
        exit 1
    }
    # A fresh global npm install is not on PATH in the current session.
    if (-not (Test-Command 'claude')) {
        Write-Warn2 "Installed, but not yet on PATH in this session."
        Write-Host "     Close this window, open a new PowerShell, and re-run this script." -ForegroundColor Gray
        exit 0
    }
}
Write-Ok "Claude Code CLI present"

# -- 3. Microsoft 365 login ----------------------------------------------------

if (-not $SkipLogin) {
    Write-Step 3 "Microsoft 365 sign-in"
    Write-Host ""
    Write-Host "  A device code will appear below." -ForegroundColor White
    Write-Host "  LEAVE THIS WINDOW RUNNING, then in your browser:" -ForegroundColor White
    Write-Host ""
    Write-Host "    1. Open  https://microsoft.com/devicelogin" -ForegroundColor Yellow
    Write-Host "    2. Enter the code shown below" -ForegroundColor Yellow
    Write-Host "    3. Sign in with your Octave account" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  This command waits for you. It exits once you approve." -ForegroundColor Gray
    Write-Host "  ---------------------------------------------------------------" -ForegroundColor DarkGray

    npx -y $mcp --org-mode --login

    Write-Host "  ---------------------------------------------------------------" -ForegroundColor DarkGray
} else {
    Write-Step 3 "Skipping sign-in (-SkipLogin)"
}

# -- 4. Verify -----------------------------------------------------------------

Write-Step 4 "Verifying authentication"

$verify = (npx -y $mcp --org-mode --verify-login 2>&1 | Out-String)
Write-Host $verify.Trim() -ForegroundColor Gray

$looksBlocked = $verify -match 'does not meet the criteria|AADSTS53003|Conditional Access|blocked by'
$looksConsent = $verify -match 'admin (consent|approval)|AADSTS65001|need admin'
$looksOk      = $verify -match '"?success"?\s*[:=]\s*true|Logged in|verified'

if ($looksBlocked) {
    Write-Host ""
    Write-Fail "Conditional Access refused the token"
    Write-Host ""
    Write-Host "  Your credentials are fine; a policy declined to issue a token." -ForegroundColor White
    Write-Host "  Since this is your managed laptop, the policy is likely app-based" -ForegroundColor White
    Write-Host "  rather than device-based. Next step: register your own app." -ForegroundColor White
    Write-Host ""
    Write-Host "    See m365-knowledge-architecture/MCP-SETUP.md" -ForegroundColor Yellow
    Write-Host "    section: 'If your tenant blocks the default app registration'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Also confirm you are on the corporate network or VPN." -ForegroundColor Gray
    exit 2
}

if ($looksConsent) {
    Write-Host ""
    Write-Fail "Tenant requires admin consent for this application"
    Write-Host ""
    Write-Host "    See m365-knowledge-architecture/MCP-SETUP.md" -ForegroundColor Yellow
    Write-Host "    section: 'If your tenant blocks the default app registration'" -ForegroundColor Yellow
    exit 3
}

if (-not $looksOk) {
    Write-Host ""
    Write-Warn2 "Could not confirm authentication from the output above."
    $answer = Read-Host "  Did the sign-in appear to succeed? (y/N)"
    if ($answer -notmatch '^(y|yes)$') {
        Write-Host "  Stopping. Re-run this script to try again." -ForegroundColor Gray
        exit 4
    }
} else {
    Write-Ok "Authenticated"
}

# -- 5. Launch -----------------------------------------------------------------

Write-Step 5 "Starting Claude Code"

if ($ReadOnly) {
    $env:READ_ONLY = '1'
    Write-Warn2 "READ_ONLY=1 - inspection only, no writes to SharePoint"
}

Write-Host ""
Write-Host "  Claude Code is starting with the runbook loaded." -ForegroundColor White
Write-Host "  It will inspect the site and pause for your approval before" -ForegroundColor Gray
Write-Host "  creating anything. Approve the ms365 MCP server when prompted." -ForegroundColor Gray
Write-Host ""

claude "Follow $Runbook. Start at Phase 0.3 since login is already done. Show me what exists on the site before creating anything."
