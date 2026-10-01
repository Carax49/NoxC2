import os
import base64


def handle_download_file(remote_path):
    """
    Read a file from agent's filesystem and return base64-encoded data.

    Args:
        remote_path: Path to file on agent machine

    Returns:
        dict: {status, message, file_data?, file_size?, file_name?}
    """
    try:
        # Normalize path
        remote_path = os.path.normpath(remote_path)

        # Check if file exists
        if not os.path.exists(remote_path):
            return {
                "status": "error",
                "message": f"File not found: {remote_path}"
            }

        # Check if it's a file (not directory)
        if not os.path.isfile(remote_path):
            return {
                "status": "error",
                "message": f"Not a file: {remote_path}"
            }

        # Get file size
        file_size = os.path.getsize(remote_path)

        # Size limit: 50MB (to avoid memory issues)
        MAX_SIZE = 50 * 1024 * 1024
        if file_size > MAX_SIZE:
            return {
                "status": "error",
                "message": f"File too large: {file_size} bytes (max {MAX_SIZE})"
            }

        # Read file
        with open(remote_path, 'rb') as f:
            file_data = f.read()

        # Base64 encode
        encoded_data = base64.b64encode(file_data).decode('utf-8')

        # Get filename
        file_name = os.path.basename(remote_path)

        return {
            "status": "success",
            "message": f"File read successfully: {remote_path}",
            "file_name": file_name,
            "file_path": remote_path,
            "file_size": file_size,
            "file_data": encoded_data
        }

    except PermissionError:
        return {
            "status": "error",
            "message": f"Permission denied: {remote_path}"
        }
    except OSError as e:
        return {
            "status": "error",
            "message": f"OS error reading file: {e}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Download failed: {type(e).__name__}: {e}"
        }
