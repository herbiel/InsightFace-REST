#!/bin/bash
set -e
source ../compose/cpu.env
echo Preparing models...
python -m api_trt.prepare_models

echo Starting InsightFace-REST using $NUM_WORKERS workers.

exec gunicorn --log-level $LOG_LEVEL\
     -w $NUM_WORKERS\
     -k uvicorn.workers.UvicornWorker\
     --keep-alive 60\
     --timeout 60\
     api_trt.app:app -b 0.0.0.0:18081