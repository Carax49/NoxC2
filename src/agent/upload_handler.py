import os
import base64


def handle_upload_file(file_path, file_data, file_size):

    tmp_path = None
    try:

        if isinstance(file_data, (bytes, bytearray)):
            data = bytes(file_data)
        else:

            data = base64.b64decode(file_data)

        if file_size is not None and len(data) != file_size:
            return {
                "status": "error",
                "message": f"Size mismatch: expected {file_size}, got {len(data)}"
            }

        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)


        tmp_path = file_path + ".tmp"
        with open(tmp_path, 'wb') as f:
            f.write(data)
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                pass


        os.replace(tmp_path, file_path)

        final_size = os.path.getsize(file_path)
        if file_size is not None and final_size != file_size:
            return {
                "status": "error",
                "message": f"Final size mismatch after write: expected {file_size}, got {final_size}",
                "file_size": final_size,
            }

        return {
            "status": "success",
            "message": f"File uploaded to {file_path}",
            "file_path": file_path,
            "file_size": final_size,
        }

    except Exception as e:
        # Cleanup temp file if present
        try:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        return {
            "status": "error",
            "message": f"Upload failed: {str(e)}"
        }