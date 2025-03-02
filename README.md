# data-store

## Connecting to Amazon S3
Config to connect to Amazon S3

```yaml
data_store:
  framework: minio
  root_bucket: ...
  connection:
    endpoint: "s3.amazonaws.com"
    access_key: AWS_ACCESS_KEY_ID
    secret_key: AWS_SECRET_ACCESS_KEY
    secure: true
```

## Connecting to local minio server
Config to connect to local minio server

```yaml
data_store:
  framework: minio
  root_bucket: ...
  connection:
    endpoint: 127.0.0.1:9000
    access_key: MINIO_ROOT_USER
    secret_key: MINIO_ROOT_PASSWORD
    secure: false
```