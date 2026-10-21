$ErrorActionPreference = 'Stop'

$project = Split-Path -Parent $PSScriptRoot
$wazuh = Join-Path $project 'security\wazuh'
$upstream = Join-Path $wazuh 'upstream'
$overrides = Join-Path $wazuh 'overrides'

if (Test-Path -LiteralPath $upstream) {
    throw "Ya existe $upstream. Revisa su estado antes de sustituirlo."
}

git clone --branch v4.14.9 --depth 1 https://github.com/wazuh/wazuh-docker.git $upstream
if ($LASTEXITCODE -ne 0) {
    throw 'No se pudo clonar Wazuh v4.14.9.'
}

$relativeFiles = @(
    '.gitignore',
    'single-node\docker-compose.yml',
    'single-node\config\wazuh_cluster\wazuh_manager.conf',
    'single-node\config\wazuh_cluster\uts_portal_rules.xml'
)
foreach ($relative in $relativeFiles) {
    Copy-Item -LiteralPath (Join-Path $overrides $relative) -Destination (Join-Path $upstream $relative) -Force
}
Write-Host 'Wazuh v4.14.9 y ajustes locales preparados. Genera certificados y contraseñas locales antes de arrancarlo.'
