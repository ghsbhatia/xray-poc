# xray-poc

### Instructions:

Download, install and run Xray Daemon. https://docs.aws.amazon.com/xray/latest/devguide/xray-daemon.html

#### Run Message Server

python Source/message_server.py

#### Run Message Worker

python Source/message_worker.py

#### Send Command to Message Server

curl -H "Content-Type: application/json" -X POST http://localhost:8000/dispatch/m1 -d "{\"message\":\"m\",\"priority\":\"High\"}"

#### Log into AWS account and check service map under X-Ray service

