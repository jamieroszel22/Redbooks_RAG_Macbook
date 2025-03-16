#!/bin/bash
# Prepare data for Open WebUI

echo "Preparing data for Open WebUI..."
python /app/prepare_for_openwebui.py /data/processed_redbooks/chunks /data/openwebui
echo "Data preparation complete!"
