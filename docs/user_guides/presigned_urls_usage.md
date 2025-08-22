# MinIO Presigned URLs Usage Guide

This guide explains how to use the MinIO presigned URL functionality in the object store.

## Overview

Presigned URLs provide temporary, secure access to MinIO objects without requiring permanent credentials. They are ideal for:

- Client-side file uploads/downloads
- Temporary sharing of private files
- Web applications that need direct access to MinIO objects
- Mobile applications that need to upload/download files

## Basic Usage

### Generating a Presigned Download URL

```python
from data_store.object_store import ObjectStore

# Initialize the object store
store = ObjectStore()

# Generate a presigned URL for downloading a file
download_url = store.get_presigned_url("path/to/file.txt")

print(f"Download URL: {download_url}")
```

### Generating a Presigned Upload URL

```python
from data_store.object_store import ObjectStore

# Initialize the object store
store = ObjectStore()

# Generate a presigned URL for uploading a file
upload_url = store.get_presigned_upload_url("path/to/upload.txt")

print(f"Upload URL: {upload_url}")
```

## Advanced Usage

### Custom Expiration Time

```python
# Generate a presigned URL that expires in 1 hour (3600 seconds)
download_url = store.get_presigned_url("file.txt", expires=3600)

# Generate a presigned upload URL that expires in 30 minutes (1800 seconds)
upload_url = store.get_presigned_upload_url("upload.txt", expires=1800)
```

### Using Different Buckets

```python
# Generate URLs for a specific bucket (not the default root bucket)
download_url = store.get_presigned_url("file.txt", bucket="my-bucket")
upload_url = store.get_presigned_upload_url("upload.txt", bucket="my-bucket")
```

### Additional Parameters

```python
# Generate URLs with additional MinIO parameters
download_url = store.get_presigned_url(
    "file.txt", 
    expires=7200,
    # Additional parameters passed to MinIO SDK
    response_headers={"Content-Type": "application/octet-stream"}
)
```

## Client-Side Usage

### JavaScript/HTML Upload

```html
<!DOCTYPE html>
<html>
<head>
    <title>File Upload</title>
</head>
<body>
    <input type="file" id="fileInput">
    <button onclick="uploadFile()">Upload</button>
    <script>
        async function uploadFile() {
            const file = document.getElementById('fileInput').files[0];
            const response = await fetch('/api/upload-url'); // Get upload URL from your backend
            const { uploadUrl } = await response.json();
            
            const uploadResponse = await fetch(uploadUrl, {
                method: 'PUT',
                body: file,
                headers: {
                    'Content-Type': file.type
                }
            });
            
            if (uploadResponse.ok) {
                alert('File uploaded successfully!');
            } else {
                alert('Upload failed');
            }
        }
    </script>
</body>
</html>
```

### JavaScript/HTML Download

```html
<!DOCTYPE html>
<html>
<head>
    <title>File Download</title>
</head>
<body>
    <button onclick="downloadFile()">Download File</button>
    <script>
        async function downloadFile() {
            const response = await fetch('/api/download-url'); // Get download URL from your backend
            const { downloadUrl } = await response.json();
            
            window.open(downloadUrl, '_blank');
        }
    </script>
</body>
</html>
```

## Python Client Usage

```python
import requests
import io

# Upload file using presigned URL
def upload_file_with_presigned_url(upload_url, file_content, content_type="application/octet-stream"):
    headers = {
        'Content-Type': content_type
    }
    response = requests.put(upload_url, data=file_content, headers=headers)
    response.raise_for_status()
    return response

# Download file using presigned URL
def download_file_with_presigned_url(download_url):
    response = requests.get(download_url)
    response.raise_for_status()
    return response.content

# Example usage
upload_url = store.get_presigned_upload_url("my-upload.txt")
download_url = store.get_presigned_url("my-upload.txt")

# Upload
with open("local-file.txt", "rb") as f:
    upload_file_with_presigned_url(upload_url, f.read())

# Download
file_content = download_file_with_presigned_url(download_url)
print(f"Downloaded {len(file_content)} bytes")
```

## Security Considerations

1. **Expiration Time**: Always set appropriate expiration times for presigned URLs
2. **Object Scope**: URLs are limited to specific objects and cannot be used for other objects
3. **Method Scope**: Download URLs only work with GET requests, upload URLs only work with PUT requests
4. **No Credential Exposure**: Presigned URLs do not expose your MinIO credentials
5. **IP Restrictions**: Consider adding IP restrictions if your MinIO server supports it

## Best Practices

1. **Short Expiration Times**: Use short expiration times (e.g., 15 minutes to 1 hour) for sensitive files
2. **Validate File Types**: Validate file types on the server side when accepting uploads
3. **Rate Limiting**: Implement rate limiting for presigned URL generation
4. **Logging**: Log presigned URL usage for monitoring and auditing
5. **Error Handling**: Handle expired URLs gracefully in your client applications

## Error Handling

```python
try:
    download_url = store.get_presigned_url("nonexistent-file.txt")
    # Use the URL...
except Exception as e:
    print(f"Error generating presigned URL: {e}")
    # Handle the error appropriately
```

## Testing

The presigned URL functionality includes comprehensive tests. You can run them with:

```bash
# Run all object store tests
pytest tests/object_store/

# Run specific presigned URL tests
pytest tests/object_store/test_presigned_urls.py

# Run with verbose output
pytest tests/object_store/test_presigned_urls.py -v
```

## API Reference

### ObjectStore.get_presigned_url(key, bucket=None, expires=None, *args, **kwargs)

Generate a presigned URL for downloading objects (GET method).

**Parameters:**
- `key` (str): Object key name
- `bucket` (str, optional): Bucket name. Defaults to root_bucket
- `expires` (int, optional): Expiration time in seconds. Defaults to None
- `*args, **kwargs`: Additional arguments passed to MinIO SDK

**Returns:**
- `str`: Presigned download URL

### ObjectStore.get_presigned_upload_url(key, bucket=None, expires=None, *args, **kwargs)
 
Generate a presigned URL for uploading objects (PUT method).

**Parameters:**
- `key` (str): Object key name
- `bucket` (str, optional): Bucket name. Defaults to root_bucket
- `expires` (int, optional): Expiration time in seconds. Defaults to None
- `*args, **kwargs`: Additional arguments passed to MinIO SDK

**Returns:**
- `str`: Presigned upload URL