$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $projectRoot
try {
    Write-Output '=== UTS CWPP: estado de contenedores ==='
    docker compose ps -a

    Write-Output '=== Salud HTTP y PostgreSQL ==='
    $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8080/health' -TimeoutSec 10
    Write-Output "portal=$($health.status) database=$($health.database)"
    docker compose exec -T database psql -U uts_user -d uts_academico -At -c 'SELECT (SELECT count(*) FROM estudiantes) AS estudiantes, (SELECT count(*) FROM cursos) AS cursos, (SELECT count(*) FROM matriculas) AS matriculas;'

    Write-Output '=== Redes y volumen ==='
    docker network inspect uts-cwpp_uts_internal --format 'red={{.Name}} internal={{.Internal}} contenedores={{len .Containers}}'
    docker network inspect uts-cwpp_portal_access --format 'red={{.Name}} internal={{.Internal}} contenedores={{len .Containers}}'
    docker volume ls --filter name=uts-cwpp_postgres_data --format 'volumen={{.Name}}'

    Write-Output '=== Auditoria preparada para Wazuh ==='
    docker volume ls --filter name=uts-cwpp_audit_logs --format 'volumen={{.Name}}'
    docker compose exec -T portal python -c "import pathlib,json; p=pathlib.Path('/var/log/uts/audit.jsonl'); rows=p.read_text(encoding='utf-8').splitlines(); print('eventos='+str(len(rows))+' tipos='+','.join(sorted({json.loads(x)['event'] for x in rows})))"

    Write-Output '=== Restricciones del portal ==='
    docker inspect uts-portal --format 'usuario={{.Config.User}} raiz_solo_lectura={{.HostConfig.ReadonlyRootfs}} privilegiado={{.HostConfig.Privileged}} capacidades_eliminadas={{json .HostConfig.CapDrop}} limite_pids={{.HostConfig.PidsLimit}} limite_memoria_bytes={{.HostConfig.Memory}} salud={{.State.Health.Status}}'

    Write-Output '=== Consumo actual ==='
    docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'
} finally {
    Pop-Location
}
