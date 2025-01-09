from datetime import datetime, timedelta
import stat
import os

def download_directory(sftp, remote_dir, local_dir):
    """
    The data on the ftp server is organized in directories in the /data folder.
    The directories are named with the iso dates. This function takes as input the sftp connection, 
    the remote directory (e.g. 'data/2024-06-30') and the local path where the data should be downloaded to ('./../../data/chech_globe_data/<ISO-date>).
    """

    print(f"Recursion: Downloading {remote_dir} to {local_dir}")
    for entry in sftp.listdir_attr(remote_dir):
        remote_path = f"{remote_dir}/{entry.filename}"
        local_path = os.path.join(local_dir, entry.filename)
        if stat.S_ISDIR(entry.st_mode):
            os.makedirs(local_path, exist_ok=True)
            download_directory(sftp, remote_path, local_path)
        else:
            sftp.get(remote_path, local_path)


def is_iso_date(filename):
    """
    Checks if a string is a valid ISO 8601 date
    """
    try:
        datetime.fromisoformat(filename)
        return True
    except ValueError:
        return False
    

def list_dates(sftp):
    """
    List all the dates in the 'data' directory on the sftp server
    """    
    file_paths = []
    dates = []
    sftp_list = sftp.listdir_attr('data')
    for file in sftp_list:
        if stat.S_ISDIR(file.st_mode) and is_iso_date(file.filename):
            dates.append(file.filename)
            
    latest_date = sorted(dates)[-1]

    return dates, latest_date