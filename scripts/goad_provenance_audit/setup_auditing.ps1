<#
.SYNOPSIS
    setup_auditing.ps1 — Automated Telemetry & SACL Configuration for GOAD
    Target Machines: DC03 (192.168.56.12) & SRV03 (192.168.56.23)
.DESCRIPTION
    Enables granular Directory Service Changes (Event 5136), Certification Services
    (Event 4886/4887), Kerberos PKINIT (Event 4768), and SACL attribute auditing
    required for the Cross-Layer Identity & PKI Provenance Graph (CIPG).
#>

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " [CIPG] Configuring Windows Security Audit Policies...   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Enable Advanced Audit Policies
$subcategories = @(
    "Directory Service Changes",
    "Certification Services",
    "Kerberos Authentication Service",
    "Kerberos Service Ticket Operations",
    "Logon",
    "Special Logon",
    "Audit Policy Change"
)

foreach ($sub in $subcategories) {
    Write-Host "[*] Enabling Subcategory: $sub" -ForegroundColor Yellow
    auditpol /set /subcategory:"$sub" /success:enable /failure:enable
}

# 2. Configure CA AuditFilter on Certificate Authority (SRV03)
if (Get-Service -Name "certsvc" -ErrorAction SilentlyContinue) {
    Write-Host "[+] Detected Active Directory Certificate Services (certsvc)." -ForegroundColor Green
    Write-Host "[*] Setting CA AuditFilter = 127 (Full Request/Issuance/Template Audit)..." -ForegroundColor Yellow
    certutil -setreg CA\AuditFilter 127
    certutil -setreg policy\EditFlags +EDITF_AUDITCERTTEMPLATELOAD
    certutil -setreg CA\LogLevel 4
    Write-Host "[*] Restarting certsvc..." -ForegroundColor Yellow
    Restart-Service certsvc
    Write-Host "[+] CA Auditing successfully initialized." -ForegroundColor Green
}

# 3. Apply SACL on Certificate Templates & User Containers (DC03)
Import-Module ActiveDirectory -ErrorAction SilentlyContinue
if (Get-Command Get-ADRootDSE -ErrorAction SilentlyContinue) {
    Write-Host "[+] Domain Controller detected. Configuring SACL on Configuration NC..." -ForegroundColor Green
    try {
        $rootDSE = Get-ADRootDSE
        $configNC = $rootDSE.configurationNamingContext

        # Target: CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration...
        $templatesPath = "AD:\CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"
        
        $everyone = New-Object System.Security.Principal.SecurityIdentifier("S-1-1-0")
        $auditRule = New-Object System.DirectoryServices.ActiveDirectoryAuditRule(
            $everyone,
            [System.DirectoryServices.ActiveDirectoryRights]::WriteProperty -bor [System.DirectoryServices.ActiveDirectoryRights]::WriteDacl,
            [System.Security.AccessControl.AuditFlags]::Success,
            [System.DirectoryServices.ActiveDirectorySecurityInheritance]::All
        )

        $acl = Get-Acl -Path $templatesPath -Audit
        $acl.AddAuditRule($auditRule)
        Set-Acl -Path $templatesPath -AclObject $acl
        Write-Host "[+] SACL successfully applied to Certificate Templates container." -ForegroundColor Green
    }
    catch {
        Write-Warning "Failed to set SACL via ActiveDirectory module: $_"
    }
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " [CIPG] Audit Configuration Complete!                     " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
