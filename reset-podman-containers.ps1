# Podman container reset script
Write-Host "Stopping and removing all Podman containers..." -ForegroundColor Cyan

$containers = podman ps -a --format "{{.ID}}"
foreach ($container in $containers) {
    Write-Host "Stopping container $container..." -ForegroundColor Yellow
    podman stop $container 2>$null
    Write-Host "Removing container $container..." -ForegroundColor Yellow
    podman rm $container 2>$null
}

Write-Host "Removing all Podman images..." -ForegroundColor Cyan
$images = podman images --format "{{.ID}}"
foreach ($image in $images) {
    Write-Host "Removing image $image..." -ForegroundColor Yellow
    podman rmi -f $image 2>$null
}

Write-Host "Cleaning up Podman volumes..." -ForegroundColor Cyan
podman volume prune -f

Write-Host "Podman environment has been reset." -ForegroundColor Green
Write-Host "To rebuild with the timestamp fix, run fix-podman-timestamp.bat" -ForegroundColor Green
