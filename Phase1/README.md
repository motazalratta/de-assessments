todo

sudo docker build -t phase1:v1 .

sudo docker run \
  -e GOOGLE_CLOUD_PROJECT="analog-patrol-311615" \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/key/googlecloud.key.file.json \
  -v $(pwd)/key/:/app/key/ \
  -v $(pwd)/input/:/input/ \
  -v $(pwd)/archive/:/archive/ \
  phase1:v1
  
