import os
import hashlib
import shutil
from datetime import datetime

def get_file_hash(filepath):
    """Generate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None

def cleanup_old_files(directory, max_age_hours=24):
    """Clean up files older than specified hours"""
    if not os.path.exists(directory):
        return 0
    
    current_time = datetime.now()
    files_deleted = 0
    
    for filename in os.listdir(directory):
        if filename.startswith('.'):  # Skip hidden files
            continue
            
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            age_hours = (current_time - file_time).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                try:
                    os.remove(filepath)
                    files_deleted += 1
                except OSError:
                    pass
    
    return files_deleted

def cleanup_old_sessions(generated_folder, max_age_hours=24):
    """Clean up old session folders"""
    if not os.path.exists(generated_folder):
        return 0
    
    current_time = datetime.now()
    sessions_deleted = 0
    
    for session_id in os.listdir(generated_folder):
        session_path = os.path.join(generated_folder, session_id)
        
        # Skip if not a directory or is a hidden file
        if not os.path.isdir(session_path) or session_id.startswith('.'):
            continue
        
        # Check if session folder is old
        try:
            # Use the oldest file in the session folder as the session age
            oldest_time = None
            for filename in os.listdir(session_path):
                filepath = os.path.join(session_path, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if oldest_time is None or file_time < oldest_time:
                        oldest_time = file_time
            
            if oldest_time:
                age_hours = (current_time - oldest_time).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    try:
                        shutil.rmtree(session_path)
                        sessions_deleted += 1
                    except OSError:
                        pass
        except Exception:
            # If we can't determine age, skip this session
            pass
    
    return sessions_deleted

def get_directory_size(directory):
    """Get total size of directory in bytes"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    except Exception:
        pass
    return total_size

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}" 