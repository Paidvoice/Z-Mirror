from json import loads
from asyncio.subprocess import PIPE
from asyncio import create_subprocess_exec
from os import path as ospath, replace as osreplace

from bot import LOGGER


async def edit_video_metadata(data, dir):
    if not dir.lower().endswith(('.mp4', '.mkv')):
        return dir

    file_name = ospath.basename(dir)
    directory = ospath.dirname(dir)
    temp_file = f"{file_name}.temp.mkv"
    temp_file_path = ospath.join(directory, temp_file)

    cmd = ['ffprobe', '-hide_banner', '-loglevel', 'error', '-print_format', 'json', '-show_streams', dir]
    LOGGER.info(f"Getting stream info for file: {file_name}")
    process = await create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        LOGGER.error(f"Error getting stream info: {stderr.decode().strip()}")
        return dir

    try:
        streams = loads(stdout)['streams']
    except:
        LOGGER.info(f"No streams found in the ffprobe output: {stdout.decode().strip()}")
        return dir

    cmd = [
        "ffmpeg", '-y', '-i', dir, '-c', 'copy',
        '-metadata:s:v:0', f'title={data}',
        '-metadata', f'title={data}',
        '-metadata', 'copyright=',
        '-metadata', 'description=',
        '-metadata', 'license=',
        '-metadata', 'LICENSE=',
        '-metadata', 'author=',
        '-metadata', 'summary=',
        '-metadata', 'comment=',
        '-metadata', 'artist=',
        '-metadata', 'album=',
        '-metadata', 'genre=',
        '-metadata', 'date=',
        '-metadata', 'creation_time=',
        '-metadata', 'language=',
        '-metadata', 'publisher=',
        '-metadata', 'encoder=',
        '-metadata', 'SUMMARY=',
        '-metadata', 'AUTHOR=',
        '-metadata', 'WEBSITE=',
        '-metadata', 'COMMENT=',
        '-metadata', 'ENCODER=',
        '-metadata', 'FILENAME=',
        '-metadata', 'MIMETYPE=',
        '-metadata', 'PURL=',
        '-metadata', 'ALBUM='
    ]

    audio_index = 0
    subtitle_index = 0
    first_video = False

    for stream in streams:
        stream_index = stream['index']
        stream_type = stream['codec_type']

        if stream_type == 'video':
            if not first_video:
                cmd.extend(['-map', f'0:{stream_index}'])
                first_video = True
            cmd.extend([f'-metadata:s:v:{stream_index}', f'title={data}'])
        elif stream_type == 'audio':
            cmd.extend(['-map', f'0:{stream_index}', f'-metadata:s:a:{audio_index}', f'title={data}'])
            audio_index += 1
        elif stream_type == 'subtitle':
            codec_name = stream.get('codec_name', 'unknown')
            if codec_name in ['webvtt', 'unknown']:
                LOGGER.info(f"Skipping unsupported subtitle metadata modification: {codec_name} for stream {stream_index}")
            else:
                cmd.extend(['-map', f'0:{stream_index}', f'-metadata:s:s:{subtitle_index}', f'title={data}'])
                subtitle_index += 1
        else:
            cmd.extend(['-map', f'0:{stream_index}'])

    cmd.append(temp_file_path)
    LOGGER.info(f"Modifying metadata for file: {file_name}")
    process = await create_subprocess_exec(*cmd, stderr=PIPE, stdout=PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        err = stderr.decode().strip()
        LOGGER.error(err)
        LOGGER.error(f"Error modifying metadata for file: {file_name}")
        return dir

    osreplace(temp_file_path, dir)
    LOGGER.info(f"Metadata modified successfully for file: {file_name}")
