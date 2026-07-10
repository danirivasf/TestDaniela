<#
.SYNOPSIS
    Provisions all KM document libraries, metadata columns, content types,
    and SharePoint lists on the DaniandEthan site.

.PREREQUISITES
    Install-Module PnP.PowerShell -Scope CurrentUser
    Register an Entra ID app with Sites.FullControl.All (or use interactive login below)

.USAGE
    # Interactive login (simplest — works for most M365 users)
    .\Provision-KMSite.ps1 -SiteUrl "https://octaveint.sharepoint.com/sites/DaniandEthan"

    # App-only (CI/CD)
    .\Provision-KMSite.ps1 -SiteUrl "https://octaveint.sharepoint.com/sites/DaniandEthan" `
        -ClientId "your-app-client-id" -Thumbprint "your-cert-thumbprint" -Tenant "octaveint.onmicrosoft.com"
#>

param(
    [Parameter(Mandatory)]
    [string]$SiteUrl = "https://octaveint.sharepoint.com/sites/DaniandEthan",

    [string]$ClientId,
    [string]$Thumbprint,
    [string]$Tenant
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Connect ──────────────────────────────────────────────────────────────────

if ($ClientId) {
    Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Thumbprint $Thumbprint -Tenant $Tenant
} else {
    Connect-PnPOnline -Url $SiteUrl -Interactive
}

Write-Host "Connected to $SiteUrl" -ForegroundColor Green

# ── 1. Site Columns ───────────────────────────────────────────────────────────

Write-Host "`n[1/5] Creating site columns..." -ForegroundColor Cyan

$groupName = "KM Metadata"

# Objective
Add-PnPField -DisplayName "Objective" -InternalName "KMObjective" -Type Choice -Group $groupName -AddToDefaultView $false -Choices @(
    "Increase Revenue",
    "Improve Operational Efficiency",
    "Accelerate Product Innovation",
    "Improve Customer Success"
) -ErrorAction SilentlyContinue

# KeyResult
Add-PnPField -DisplayName "Key Result" -InternalName "KMKeyResult" -Type Text -Group $groupName -AddToDefaultView $false -ErrorAction SilentlyContinue

# Project
Add-PnPField -DisplayName "Project" -InternalName "KMProject" -Type Text -Group $groupName -AddToDefaultView $false -ErrorAction SilentlyContinue

# ContentTypeLabel
Add-PnPField -DisplayName "Content Type Label" -InternalName "KMContentTypeLabel" -Type Choice -Group $groupName -AddToDefaultView $false -Choices @(
    "Email", "Attachment", "Meeting Transcript", "Spreadsheet",
    "Presentation", "Report", "Contract", "SOP", "Other"
) -ErrorAction SilentlyContinue

# ConfidenceScore
Add-PnPField -DisplayName "Confidence Score" -InternalName "KMConfidenceScore" -Type Number -Group $groupName -AddToDefaultView $false -ErrorAction SilentlyContinue

# Source
Add-PnPField -DisplayName "Source" -InternalName "KMSource" -Type Choice -Group $groupName -AddToDefaultView $false -Choices @(
    "Email", "Teams", "Upload", "Power BI", "SharePoint Sync", "API"
) -ErrorAction SilentlyContinue

# Owner (Person)
Add-PnPField -DisplayName "KM Owner" -InternalName "KMOwner" -Type User -Group $groupName -AddToDefaultView $false -ErrorAction SilentlyContinue

# ClassifiedDate
Add-PnPField -DisplayName "Classified Date" -InternalName "KMClassifiedDate" -Type DateTime -Group $groupName -AddToDefaultView $false -ErrorAction SilentlyContinue

# ReviewedBy
Add-PnPField -DisplayName "Reviewed By" -InternalName "KMReviewedBy" -Type User -Group $groupName -AddToDefaultView $false -ErrorAction SilentlyContinue

# ReviewedDate
Add-PnPField -DisplayName "Reviewed Date" -InternalName "KMReviewedDate" -Type DateTime -Group $groupName -AddToDefaultView $false -ErrorAction SilentlyContinue

# OverrideReason
Add-PnPField -DisplayName "Override Reason" -InternalName "KMOverrideReason" -Type Note -Group $groupName -AddToDefaultView $false -ErrorAction SilentlyContinue

# MeetingDate
Add-PnPField -DisplayName "Meeting Date" -InternalName "KMMeetingDate" -Type DateTime -Group $groupName -AddToDefaultView $false -ErrorAction SilentlyContinue

# EmailSentDate
Add-PnPField -DisplayName "Email Sent Date" -InternalName "KMEmailSentDate" -Type DateTime -Group $groupName -AddToDefaultView $false -ErrorAction SilentlyContinue

# RetentionLabel
Add-PnPField -DisplayName "Retention Label" -InternalName "KMRetentionLabel" -Type Choice -Group $groupName -AddToDefaultView $false -Choices @(
    "Transient-30d", "Standard-3yr", "Financial-7yr", "Legal-Hold", "Permanent"
) -ErrorAction SilentlyContinue

Write-Host "  Site columns created." -ForegroundColor Green

# ── 2. Document Libraries ─────────────────────────────────────────────────────

Write-Host "`n[2/5] Creating document libraries..." -ForegroundColor Cyan

$libraries = @(
    @{ Title = "AI Inbox";               Url = "ai-inbox";              Description = "Staging library for AI-classified documents pending review" },
    @{ Title = "Classified Documents";   Url = "classified-documents";  Description = "Primary library for reviewed, AI-classified content" },
    @{ Title = "Email Archives";         Url = "email-archives";        Description = "Raw email exports auto-ingested from Exchange" },
    @{ Title = "Meeting Transcripts";    Url = "meeting-transcripts";   Description = "Teams meeting transcripts auto-ingested from recordings" },
    @{ Title = "Spreadsheets";           Url = "spreadsheets";          Description = "Excel workbooks: pricebooks, SKU catalogs, reports" },
    @{ Title = "Pricebooks";             Url = "pricebooks";            Description = "Master pricebook Excel files - checkout required" },
    @{ Title = "SKU Catalog";            Url = "sku-catalog";           Description = "SKU definition spreadsheets" },
    @{ Title = "Quotes";                 Url = "quotes";                Description = "Quote PDFs and Word documents" }
)

foreach ($lib in $libraries) {
    $existing = Get-PnPList -Identity $lib.Url -ErrorAction SilentlyContinue
    if (-not $existing) {
        New-PnPList -Title $lib.Title -Url $lib.Url -Template DocumentLibrary -EnableVersioning $true
        Set-PnPList -Identity $lib.Url -Description $lib.Description
        Write-Host "  Created library: $($lib.Title)" -ForegroundColor Gray
    } else {
        Write-Host "  Library already exists (skipped): $($lib.Title)" -ForegroundColor Yellow
    }
}

Write-Host "  Libraries created." -ForegroundColor Green

# ── 3. Add Metadata Columns to Libraries ─────────────────────────────────────

Write-Host "`n[3/5] Adding metadata columns to libraries..." -ForegroundColor Cyan

$metadataColumns = @(
    "KMObjective", "KMKeyResult", "KMProject", "KMContentTypeLabel",
    "KMConfidenceScore", "KMSource", "KMOwner", "KMClassifiedDate",
    "KMReviewedBy", "KMReviewedDate", "KMOverrideReason", "KMRetentionLabel"
)

$meetingColumns   = @("KMMeetingDate")
$emailColumns     = @("KMEmailSentDate")

foreach ($lib in $libraries) {
    foreach ($col in $metadataColumns) {
        Add-PnPFieldToContentType -Field $col -ContentType "Document" -ErrorAction SilentlyContinue
        try {
            Add-PnPField -List $lib.Url -Field $col -ErrorAction SilentlyContinue
        } catch { }
    }
}

# Add Meeting Date only to Meeting Transcripts
foreach ($col in $meetingColumns) {
    try { Add-PnPField -List "meeting-transcripts" -Field $col -ErrorAction SilentlyContinue } catch { }
}

# Add Email Sent Date only to Email Archives
foreach ($col in $emailColumns) {
    try { Add-PnPField -List "email-archives" -Field $col -ErrorAction SilentlyContinue } catch { }
}

Write-Host "  Metadata columns added." -ForegroundColor Green

# ── 4. Versioning Settings ────────────────────────────────────────────────────

Write-Host "`n[4/5] Configuring versioning..." -ForegroundColor Cyan

# Major + minor, keep 20 majors
Set-PnPList -Identity "classified-documents" -EnableVersioning $true -EnableMinorVersions $true -MajorVersions 20
Set-PnPList -Identity "spreadsheets"         -EnableVersioning $true -EnableMinorVersions $true -MajorVersions 50
Set-PnPList -Identity "pricebooks"           -EnableVersioning $true -EnableMinorVersions $true

# Major only
Set-PnPList -Identity "ai-inbox"             -EnableVersioning $true -EnableMinorVersions $false -MajorVersions 5
Set-PnPList -Identity "email-archives"       -EnableVersioning $true -EnableMinorVersions $false
Set-PnPList -Identity "meeting-transcripts"  -EnableVersioning $true -EnableMinorVersions $false
Set-PnPList -Identity "quotes"               -EnableVersioning $true -EnableMinorVersions $true -MajorVersions 20
Set-PnPList -Identity "sku-catalog"          -EnableVersioning $true -EnableMinorVersions $true -MajorVersions 20

Write-Host "  Versioning configured." -ForegroundColor Green

# ── 5. Tracking & Correction SharePoint Lists ─────────────────────────────────

Write-Host "`n[5/5] Creating tracking lists..." -ForegroundColor Cyan

# KM-Classification-Log
$logList = Get-PnPList -Identity "KM-Classification-Log" -ErrorAction SilentlyContinue
if (-not $logList) {
    New-PnPList -Title "KM Classification Log" -Url "KM-Classification-Log" -Template GenericList
    Add-PnPField -List "KM-Classification-Log" -DisplayName "Run ID"          -InternalName "RunId"          -Type Text    -AddToDefaultView $true
    Add-PnPField -List "KM-Classification-Log" -DisplayName "Source"          -InternalName "LogSource"      -Type Choice  -AddToDefaultView $true  -Choices @("Email","Teams","Upload","Power BI","API")
    Add-PnPField -List "KM-Classification-Log" -DisplayName "Original Name"   -InternalName "OriginalName"   -Type Text    -AddToDefaultView $true
    Add-PnPField -List "KM-Classification-Log" -DisplayName "AI Objective"    -InternalName "AIObjective"    -Type Choice  -AddToDefaultView $true  -Choices @("Increase Revenue","Improve Operational Efficiency","Accelerate Product Innovation","Improve Customer Success")
    Add-PnPField -List "KM-Classification-Log" -DisplayName "AI Key Result"   -InternalName "AIKeyResult"    -Type Text    -AddToDefaultView $true
    Add-PnPField -List "KM-Classification-Log" -DisplayName "Confidence Score" -InternalName "ConfScore"     -Type Number  -AddToDefaultView $true
    Add-PnPField -List "KM-Classification-Log" -DisplayName "Was Overridden"  -InternalName "WasOverridden"  -Type Boolean -AddToDefaultView $true
    Add-PnPField -List "KM-Classification-Log" -DisplayName "Final Objective" -InternalName "FinalObjective" -Type Text    -AddToDefaultView $false
    Add-PnPField -List "KM-Classification-Log" -DisplayName "SP File URL"     -InternalName "SPFileUrl"      -Type URL     -AddToDefaultView $false
    Add-PnPField -List "KM-Classification-Log" -DisplayName "Processed Date"  -InternalName "ProcessedDate"  -Type DateTime -AddToDefaultView $true
    Write-Host "  Created: KM Classification Log" -ForegroundColor Gray
}

# KM-Correction-Log
$corrList = Get-PnPList -Identity "KM-Correction-Log" -ErrorAction SilentlyContinue
if (-not $corrList) {
    New-PnPList -Title "KM Correction Log" -Url "KM-Correction-Log" -Template GenericList
    Add-PnPField -List "KM-Correction-Log" -DisplayName "Run ID"                -InternalName "RunId"               -Type Text    -AddToDefaultView $true
    Add-PnPField -List "KM-Correction-Log" -DisplayName "Correction Date"       -InternalName "CorrectionDate"      -Type DateTime -AddToDefaultView $true
    Add-PnPField -List "KM-Correction-Log" -DisplayName "Corrected By"          -InternalName "CorrectedBy"         -Type User    -AddToDefaultView $true
    Add-PnPField -List "KM-Correction-Log" -DisplayName "Original Objective"    -InternalName "OriginalObjective"   -Type Text    -AddToDefaultView $true
    Add-PnPField -List "KM-Correction-Log" -DisplayName "Original Key Result"   -InternalName "OriginalKeyResult"   -Type Text    -AddToDefaultView $false
    Add-PnPField -List "KM-Correction-Log" -DisplayName "Original Confidence"   -InternalName "OriginalConfidence"  -Type Number  -AddToDefaultView $false
    Add-PnPField -List "KM-Correction-Log" -DisplayName "Corrected Objective"   -InternalName "CorrectedObjective"  -Type Text    -AddToDefaultView $true
    Add-PnPField -List "KM-Correction-Log" -DisplayName "Corrected Key Result"  -InternalName "CorrectedKeyResult"  -Type Text    -AddToDefaultView $false
    Add-PnPField -List "KM-Correction-Log" -DisplayName "Correction Type"       -InternalName "CorrectionType"      -Type Choice  -AddToDefaultView $true  -Choices @("Objective Change","KeyResult Change","Both","Confirmed Correct")
    Add-PnPField -List "KM-Correction-Log" -DisplayName "Override Reason"       -InternalName "OverrideReason"      -Type Note    -AddToDefaultView $false
    Add-PnPField -List "KM-Correction-Log" -DisplayName "Document Keywords"     -InternalName "DocKeywords"         -Type Note    -AddToDefaultView $false
    Add-PnPField -List "KM-Correction-Log" -DisplayName "Content Type"          -InternalName "DocContentType"      -Type Text    -AddToDefaultView $false
    Add-PnPField -List "KM-Correction-Log" -DisplayName "SP File URL"           -InternalName "SPFileUrl"           -Type URL     -AddToDefaultView $true
    Add-PnPField -List "KM-Correction-Log" -DisplayName "Used In Training"      -InternalName "UsedInTraining"      -Type Boolean -AddToDefaultView $true
    Add-PnPField -List "KM-Correction-Log" -DisplayName "Training Batch ID"     -InternalName "TrainingBatchId"     -Type Text    -AddToDefaultView $false
    Write-Host "  Created: KM Correction Log" -ForegroundColor Gray
}

# KM-Prompt-Config (stores the active brain prompt)
$promptList = Get-PnPList -Identity "KM-Prompt-Config" -ErrorAction SilentlyContinue
if (-not $promptList) {
    New-PnPList -Title "KM Prompt Config" -Url "KM-Prompt-Config" -Template GenericList
    Add-PnPField -List "KM-Prompt-Config" -DisplayName "Prompt Version"   -InternalName "PromptVersion"   -Type Text  -AddToDefaultView $true
    Add-PnPField -List "KM-Prompt-Config" -DisplayName "System Prompt"    -InternalName "SystemPrompt"    -Type Note  -AddToDefaultView $false
    Add-PnPField -List "KM-Prompt-Config" -DisplayName "User Prompt"      -InternalName "UserPrompt"      -Type Note  -AddToDefaultView $false
    Add-PnPField -List "KM-Prompt-Config" -DisplayName "Few Shot Examples" -InternalName "FewShotExamples" -Type Note  -AddToDefaultView $false
    Add-PnPField -List "KM-Prompt-Config" -DisplayName "Is Active"        -InternalName "IsActive"        -Type Boolean -AddToDefaultView $true
    Add-PnPField -List "KM-Prompt-Config" -DisplayName "Effective Date"   -InternalName "EffectiveDate"   -Type DateTime -AddToDefaultView $true
    Write-Host "  Created: KM Prompt Config" -ForegroundColor Gray
}

# KM-Metrics-Daily
$metricslist = Get-PnPList -Identity "KM-Metrics-Daily" -ErrorAction SilentlyContinue
if (-not $metricslist) {
    New-PnPList -Title "KM Metrics Daily" -Url "KM-Metrics-Daily" -Template GenericList
    Add-PnPField -List "KM-Metrics-Daily" -DisplayName "Report Date"       -InternalName "ReportDate"      -Type DateTime -AddToDefaultView $true
    Add-PnPField -List "KM-Metrics-Daily" -DisplayName "Total Classified"  -InternalName "TotalClassified" -Type Number   -AddToDefaultView $true
    Add-PnPField -List "KM-Metrics-Daily" -DisplayName "Auto Approved"     -InternalName "AutoApproved"    -Type Number   -AddToDefaultView $true
    Add-PnPField -List "KM-Metrics-Daily" -DisplayName "Sent For Review"   -InternalName "SentForReview"   -Type Number   -AddToDefaultView $true
    Add-PnPField -List "KM-Metrics-Daily" -DisplayName "Overridden"        -InternalName "OverriddenCount" -Type Number   -AddToDefaultView $true
    Add-PnPField -List "KM-Metrics-Daily" -DisplayName "Avg Confidence"    -InternalName "AvgConfidence"   -Type Number   -AddToDefaultView $true
    Add-PnPField -List "KM-Metrics-Daily" -DisplayName "By Objective JSON" -InternalName "ByObjectiveJson" -Type Note     -AddToDefaultView $false
    Add-PnPField -List "KM-Metrics-Daily" -DisplayName "By Source JSON"    -InternalName "BySourceJson"    -Type Note     -AddToDefaultView $false
    Write-Host "  Created: KM Metrics Daily" -ForegroundColor Gray
}

Write-Host "  Tracking lists created." -ForegroundColor Green

# ── Done ──────────────────────────────────────────────────────────────────────

Write-Host "`n✅ Provisioning complete!" -ForegroundColor Green
Write-Host "Site: $SiteUrl" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Go to $SiteUrl and verify all libraries and lists were created"
Write-Host "  2. Configure the KM-Prompt-Config list with the brain prompt from step3-brain-prompt.json"
Write-Host "  3. Create Power Automate flows using the step2 and step4 flow guides"
Write-Host "  4. Store your Anthropic API key in Azure Key Vault and reference it from flows"
Write-Host "  5. Set up the KM dashboard page at $SiteUrl/SitePages/KM-Dashboard.aspx"

Disconnect-PnPOnline
