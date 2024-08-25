from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from os import path as ospath, replace as osreplace

from bot import user_data


async def add_attachment(user_id, file_path):
    """Advanced Metadata(Attachment Url) Add
    Basic Code - https://github.com/5hojib/Aeon
    Edit By - https://github.com/SonGoku1972"""
    if not file_path.lower().endswith(('.mp4', '.mkv')):
        return

    user_dict = user_data.get(user_id, {})
    if user_dict.get("attachmenturl", False):
        attachment_url = user_dict["attachmenturl"]
    else:
        return

    file_name = ospath.basename(file_path)
    directory = ospath.dirname(file_path)
    temp_file = f"{file_name}.temp.mkv"
    temp_file_path = ospath.join(directory, temp_file)
    
    attachment_ext = attachment_url.split('.')[-1].lower()
    if attachment_ext in ['jpg', 'jpeg']:
        mime_type = 'image/jpeg'
    elif attachment_ext == 'png':
        mime_type = 'image/png'
    else:
        mime_type = 'application/octet-stream'

    cmd = [
        'ffmpeg', '-y', '-i', file_path,
        '-attach', attachment_url,
        '-metadata:s:t', f'mimetype={mime_type}',
        '-c', 'copy', '-map', '0', temp_file_path
    ]

    process = await create_subprocess_exec(*cmd, stderr=PIPE, stdout=PIPE)
    _, stderr = await process.communicate()

    if process.returncode != 0:
        err = stderr.decode().strip()
        print(err)
        print(f"Error adding photo attachment to file: {file_name}")
        return

    osreplace(temp_file_path, file_path)
    print(f"Photo attachment added successfully to file: {file_name}")
