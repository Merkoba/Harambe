#!/usr/bin/env python3

import zipfile
import tempfile
from pathlib import Path
from utils import read_archive

def test_read_archive():
    """Test the read_archive function with a simple zip file"""

    # Create a temporary zip file for testing
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
        temp_zip_path = Path(temp_zip.name)

    try:
        # Create a test zip file with some content
        with zipfile.ZipFile(temp_zip_path, 'w') as zf:
            zf.writestr('test1.txt', b'Hello World 1')
            zf.writestr('folder/test2.txt', b'Hello World 2')
            zf.writestr('folder/subfolder/test3.txt', b'Hello World 3')

        # Test reading the archive
        result = read_archive(temp_zip_path)

        if result is None:
            print("ERROR: read_archive returned None")
            return False

        print(f"Found {len(result)} files in archive:")
        for filename, content, size in result:
            print(f"  {filename} ({size} bytes): {content.decode('utf-8', errors='ignore')}")

        # Test with bytes input
        with open(temp_zip_path, 'rb') as f:
            zip_bytes = f.read()

        result_bytes = read_archive(zip_bytes, '.zip')

        if result_bytes is None:
            print("ERROR: read_archive with bytes returned None")
            return False

        print(f"\nBytes input found {len(result_bytes)} files")

        # Test with non-archive file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_txt:
            temp_txt.write(b'This is not an archive')
            temp_txt_path = Path(temp_txt.name)

        result_txt = read_archive(temp_txt_path)
        print(f"\nNon-archive file result: {result_txt}")

        # Clean up
        temp_txt_path.unlink()

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        # Clean up
        if temp_zip_path.exists():
            temp_zip_path.unlink()

if __name__ == '__main__':
    if test_read_archive():
        print("\nTest passed!")
    else:
        print("\nTest failed!")
