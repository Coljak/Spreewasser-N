# # Celery tasks
# from celery import shared_task
# import ftplib
# from datetime import datetime

# @shared_task
# def check_ftp_for_new_files():
#     ftp = ftplib.FTP('hydrospace.czechglobe.cz')  
#     ftp.login('zalf', 'blabla2423432AS::')    # TODO: Make this secure!!!!

#     today = datetime.now().strftime('%Y-%m-%d')
#     folder_name = f"/data/{today}/Data/"  

#     try:
#         ftp.cwd(folder_name)
#         # List files in the directory
#         files = ftp.nlst()

#         for file in files:
#             with open(f'./ftp_download/{file}', 'wb') as local_file:
#                 ftp.retrbinary(f'RETR {file}', local_file.write)
#         ftp.quit()
#     except ftplib.error_perm as e:
#         print(f"Error: {e}")
#         # Handle folder not found or other errors
