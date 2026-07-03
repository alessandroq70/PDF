"""Unit tests for the video merge logic.

Test clips are generated on the fly with the bundled FFmpeg, so no fixture
files are needed.
"""
import os
import subprocess

import pytest
import imageio_ffmpeg

from video_merger import MergeError, merge_videos, _probe

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def make_video(path, size="320x240", rate=30, duration=2, with_audio=True):
    cmd = [FFMPEG, "-y", "-f", "lavfi", "-i",
           f"testsrc=size={size}:rate={rate}:duration={duration}"]
    if with_audio:
        cmd += ["-f", "lavfi", "-i", f"sine=frequency=440:duration={duration}"]
    cmd += ["-c:v", "libx264"]
    if with_audio:
        cmd += ["-c:a", "aac", "-shortest"]
    cmd += ["-loglevel", "error", path]
    subprocess.run(cmd, check=True)
    return path


def test_merge_same_format_uses_fast_path(tmp_path):
    a = make_video(str(tmp_path / "a.mp4"), duration=2)
    b = make_video(str(tmp_path / "b.mp4"), duration=3)
    out = str(tmp_path / "out.mp4")
    merge_videos([a, b], out)

    info = _probe(out)
    assert info.width == 320 and info.height == 240
    assert 4.5 < info.duration < 5.6  # ~2 + 3 seconds
    assert info.has_audio


def test_merge_different_resolutions_reencodes(tmp_path):
    a = make_video(str(tmp_path / "a.mp4"), size="640x480", rate=25, duration=4, with_audio=False)
    b = make_video(str(tmp_path / "b.mp4"), size="320x240", rate=30, duration=2, with_audio=True)
    out = str(tmp_path / "out.mp4")
    merge_videos([a, b], out)

    info = _probe(out)
    # Canvas is the largest of the inputs.
    assert info.width == 640 and info.height == 480
    assert 5.5 < info.duration < 6.6  # ~4 + 2 seconds
    assert info.has_audio  # silent track added for the audio-less clip


def make_image(path, size="200x150"):
    subprocess.run(
        [FFMPEG, "-y", "-f", "lavfi", "-i", f"color=c=teal:s={size}",
         "-frames:v", "1", "-loglevel", "error", path],
        check=True,
    )
    return path


def test_merge_with_cover_prepends_duration(tmp_path):
    a = make_video(str(tmp_path / "a.mp4"), duration=2)
    b = make_video(str(tmp_path / "b.mp4"), duration=2)
    cover = make_image(str(tmp_path / "cover.jpg"))
    out = str(tmp_path / "out.mp4")
    merge_videos([a, b], out, cover_image=cover, cover_duration=3)

    info = _probe(out)
    # 3s cover + 2s + 2s = ~7s, canvas is the largest of cover/videos.
    assert 6.5 < info.duration < 7.6
    assert info.has_audio


def test_single_file_raises(tmp_path):
    a = make_video(str(tmp_path / "a.mp4"))
    with pytest.raises(MergeError):
        merge_videos([a], str(tmp_path / "out.mp4"))


def test_no_files_raises(tmp_path):
    with pytest.raises(MergeError):
        merge_videos([], str(tmp_path / "out.mp4"))


def test_invalid_input_raises(tmp_path):
    a = make_video(str(tmp_path / "a.mp4"))
    bad = str(tmp_path / "bad.mp4")
    with open(bad, "wb") as fh:
        fh.write(b"not a real video")
    with pytest.raises(MergeError):
        merge_videos([a, bad], str(tmp_path / "out.mp4"))
