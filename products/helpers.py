import subprocess


def convert_to_mp4(input_file, output_file):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-vcodec', 'libx264',
        '-crf', '28',  # 0 = best quality, 51 = worst
        output_file
    ]
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as exc:
        # pragma: no cover - external dependency
        return False, exc.stderr

    return True, result.stdout


def convert_to_thumbnail(input_file, output_file, time_position='00:00:01'):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-ss', time_position,
        '-vframes', '1',
        output_file
    ]
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as exc:
        # pragma: no cover - external dependency
        return False, exc.stderr

    return True, result.stdout
