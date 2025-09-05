# Presigned URLs User Guide

This guide explains how to use the presigned URL functionality in the object store for secure, temporary access to objects.

## Overview

Presigned URLs provide temporary, secure access to objects without requiring permanent credentials. They are ideal for:

- Client-side file uploads/downloads
- Temporary sharing of private files
- Web applications that need direct access to objects
- Mobile applications that need to upload/download files

## Basic Usage

### Generating a Presigned Download URL

```python
from data_store import ObjectStore

# Initialize the object store
store = ObjectStore()

# Generate a presigned URL for downloading a file
download_url = store.get_presigned_url("path/to/file.txt")

print(f"Download URL: {download_url}")
```

### Generating a Presigned Upload URL

```python
from data_store import ObjectStore

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
# Generate URLs with additional storage parameters
download_url = store.get_presigned_url(
    "file.txt", 
    expires=7200,
    # Additional parameters passed to storage SDK
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
4. **No Credential Exposure**: Presigned URLs do not expose your storage credentials
5. **IP Restrictions**: Consider adding IP restrictions if your storage server supports it

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
- `*args, **kwargs`: Additional arguments passed to storage SDK

**Returns:**
- `str`: Presigned download URL

### ObjectStore.get_presigned_upload_url(key, bucket=None, expires=None, *args, **kwargs)
 
Generate a presigned URL for uploading objects (PUT method).

**Parameters:**
- `key` (str): Object key name
- `bucket` (str, optional): Bucket name. Defaults to root_bucket
- `expires` (int, optional): Expiration time in seconds. Defaults to None
- `*args, **kwargs`: Additional arguments passed to storage SDK

**Returns:**
- `str`: Presigned upload URL

## Implementation Details

### How Presigned URLs Work

Presigned URLs work by adding authentication information to a URL that allows temporary access to a specific object. The storage service validates this information and grants access if it's valid and hasn't expired.

### Security Model

1. **Signature Verification**: The storage service verifies the signature in the URL
2. **Expiration Check**: The service checks if the URL has expired
3. **Access Control**: The URL grants access only to the specified object and operation
4. **No Credential Exposure**: The original credentials are never exposed to the client

### Storage-Specific Considerations

#### MinIO

- Uses HMAC-SHA256 for signature verification
- Supports custom expiration times
- Allows additional headers to be included in the signature

#### AWS S3

- Uses AWS Signature Version 4
- Supports custom expiration times
- Allows additional headers and conditions to be included in the signature

## Common Use Cases

### 1. Direct File Upload from Web Applications

```python
# Backend: Generate upload URL
@app.route('/api/upload-url', methods=['POST'])
def get_upload_url():
    file_info = request.json
    upload_url = store.get_presigned_upload_url(
        key=file_info['key'],
        expires=1800  # 30 minutes
    )
    return jsonify({'uploadUrl': upload_url})

# Frontend: Use the URL to upload directly to storage
async function uploadFile(file) {
    const response = await fetch('/api/upload-url', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            key: `uploads/${file.name}`,
            contentType: file.type
        })
    });
    
    const { uploadUrl } = await response.json();
    
    const uploadResponse = await fetch(uploadUrl, {
        method: 'PUT',
        body: file,
        headers: {'Content-Type': file.type}
    });
    
    return uploadResponse.ok;
}
```

### 2. Secure File Sharing

```python
# Generate secure download link for file sharing
def create_share_link(store, key, expires=3600):
    """Create a secure share link for a file."""
    download_url = store.get_presigned_url(
        key=key,
        expires=expires
    )
    
    # Store the share link in your database with metadata
    share_link = {
        'url': download_url,
        'key': key,
        'expires_at': datetime.now() + timedelta(seconds=expires),
        'created_at': datetime.now()
    }
    
    # Save to database
    db.share_links.insert_one(share_link)
    
    return download_url

# Usage
share_link = create_share_link(store, "documents/important.pdf", expires=7200)
print(f"Share link: {share_link}")
```

### 3. Mobile App File Operations

```python
# Mobile app can use presigned URLs for direct file operations
def upload_file_from_mobile(store, file_data, key):
    """Upload file from mobile app using presigned URL."""
    # Generate upload URL
    upload_url = store.get_presigned_upload_url(key, expires=3600)
    
    # Upload file directly to storage
    response = requests.put(upload_url, data=file_data)
    response.raise_for_status()
    
    return response.status_code == 200

def download_file_to_mobile(store, key):
    """Download file to mobile app using presigned URL."""
    # Generate download URL
    download_url = store.get_presigned_url(key, expires=3600)
    
    # Download file directly from storage
    response = requests.get(download_url)
    response.raise_for_status()
    
    return response.content
```

## Troubleshooting

### Common Issues

1. **URL Expired**: Generate a new URL with a longer expiration time
2. **Invalid Signature**: Check that the URL was generated correctly
3. **Permission Denied**: Ensure the object exists and you have access
4. **Connection Errors**: Check network connectivity and storage service status

### Debugging Tips

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test URL generation
try:
    url = store.get_presigned_url("test.txt", expires=60)
    print(f"Generated URL: {url}")
    
    # Test URL access
    response = requests.get(url)
    print(f"URL response status: {response.status_code}")
    
except Exception as e:
    print(f"Error: {e}")
    # Check logs for detailed error information
```

## Performance Considerations

### URL Generation

- URL generation is fast and doesn't require significant resources
- Cache frequently used URLs when appropriate
- Consider rate limiting for public applications

### URL Usage

- URLs can be used multiple times until they expire
- Each URL use is independent and doesn't require server-side state
- Consider using CDN caching for frequently accessed objects

## Next Steps

- **Object Store**: Learn about general object store functionality in {doc}`object_store`
- **Configuration**: Understand configuration options in {doc}`../configuration_classes`
- **Architecture**: Learn about the underlying architecture in {doc}`../abstract_base_classes`
- **Adapters**: Explore adapter implementations in {doc}`../adapters`

For API reference documentation, see the {doc}`../api_reference/index` section.