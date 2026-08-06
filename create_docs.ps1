# ============================
# Create Documentation Folders
# ============================

$folders = @(
    "docs\adr",
    "docs\api",
    "docs\architecture",
    "docs\database",
    "docs\design",
    "docs\diagrams",
    "docs\guides",
    "docs\templates"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Force -Path $folder | Out-Null
}

# ============================
# Design Documents
# ============================

$designFiles = @(
    "docs\README.md",
    "docs\design\00_Project_Charter.md",
    "docs\design\01_Product_Requirements_Document.md",
    "docs\design\02_Product_Vision.md",
    "docs\design\03_Product_Roadmap.md",
    "docs\design\04_UI_Design.md",
    "docs\design\05_User_Personas.md",
    "docs\design\99_Implementation_Roadmap.md"
)

# ============================
# Architecture Documents
# ============================

$architectureFiles = @(
    "docs\architecture\01_Software_Architecture.md",
    "docs\architecture\02_High_Level_Design.md",
    "docs\architecture\03_Low_Level_Design.md",
    "docs\architecture\04_Plugin_Architecture.md",
    "docs\architecture\05_Configuration_Framework.md",
    "docs\architecture\06_Security_Architecture.md",
    "docs\architecture\07_Deployment_Architecture.md",
    "docs\architecture\08_Observability_Architecture.md"
)

# ============================
# ADR Documents
# ============================

$adrFiles = @(
    "docs\adr\ADR-0001-Architecture-Principles.md",
    "docs\adr\ADR-0002-Plugin-Framework.md",
    "docs\adr\ADR-0003-Provider-Abstraction.md",
    "docs\adr\ADR-0004-Multi-Tenant-Architecture.md"
)

# ============================
# API Documents
# ============================

$apiFiles = @(
    "docs\api\REST_API.md",
    "docs\api\SDK_API.md",
    "docs\api\Authentication_API.md",
    "docs\api\Plugin_API.md"
)

# ============================
# Database Documents
# ============================

$databaseFiles = @(
    "docs\database\Database_Design.md",
    "docs\database\Metadata_Model.md",
    "docs\database\Vector_Index_Model.md"
)

# ============================
# Guide Documents
# ============================

$guideFiles = @(
    "docs\guides\Installation_Guide.md",
    "docs\guides\Developer_Guide.md",
    "docs\guides\Administrator_Guide.md",
    "docs\guides\Coding_Standards.md",
    "docs\guides\Contribution_Guide.md",
    "docs\guides\Development_Commands.md"
)

# ============================
# Template Documents
# ============================

$templateFiles = @(
    "docs\templates\architecture_template.md",
    "docs\templates\design_template.md",
    "docs\templates\adr_template.md",
    "docs\templates\api_template.md",
    "docs\templates\database_template.md",
    "docs\templates\guide_template.md"
)

# ============================
# Diagram Files
# ============================

$diagramFiles = @(
    "docs\diagrams\01_System_Architecture.drawio",
    "docs\diagrams\01_System_Architecture.mmd",
    "docs\diagrams\02_Component_Interaction.drawio",
    "docs\diagrams\02_Component_Interaction.mmd",
    "docs\diagrams\03_Document_Ingestion_Flow.drawio",
    "docs\diagrams\03_Document_Ingestion_Flow.mmd",
    "docs\diagrams\04_Query_Processing_Flow.drawio",
    "docs\diagrams\04_Query_Processing_Flow.mmd",
    "docs\diagrams\05_Plugin_Architecture.drawio",
    "docs\diagrams\05_Plugin_Architecture.mmd",
    "docs\diagrams\06_Deployment_Architecture.drawio",
    "docs\diagrams\06_Deployment_Architecture.mmd",
    "docs\diagrams\07_Database_ER_Diagram.drawio",
    "docs\diagrams\07_Database_ER_Diagram.mmd",
    "docs\diagrams\08_Class_Diagram.drawio",
    "docs\diagrams\08_Class_Diagram.mmd",
    "docs\diagrams\09_Sequence_Document_Ingestion.drawio",
    "docs\diagrams\09_Sequence_Document_Ingestion.mmd",
    "docs\diagrams\10_Sequence_Query_Execution.drawio",
    "docs\diagrams\10_Sequence_Query_Execution.mmd",
    "docs\diagrams\11_Authentication_Flow.drawio",
    "docs\diagrams\11_Authentication_Flow.mmd",
    "docs\diagrams\12_Workspace_Architecture.drawio",
    "docs\diagrams\12_Workspace_Architecture.mmd",
    "docs\diagrams\13_Knowledge_Pipeline.drawio",
    "docs\diagrams\13_Knowledge_Pipeline.mmd",
    "docs\diagrams\14_Provider_Architecture.drawio",
    "docs\diagrams\14_Provider_Architecture.mmd",
    "docs\diagrams\15_Configuration_Framework.drawio",
    "docs\diagrams\15_Configuration_Framework.mmd"
)

# ============================
# Create All Files
# ============================

$allFiles = $designFiles + `
            $architectureFiles + `
            $adrFiles + `
            $apiFiles + `
            $databaseFiles + `
            $guideFiles + `
            $templateFiles + `
            $diagramFiles

foreach ($file in $allFiles) {
    if (!(Test-Path $file)) {
        New-Item -ItemType File -Path $file | Out-Null
    }
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host " RAGOps Documentation Structure Ready " -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Folders Created : $($folders.Count)"
Write-Host "Files Created   : $($allFiles.Count)"
