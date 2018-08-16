#!/usr/bin/env python3
# coding: utf-8
import cv2

import imageio
import numpy as np
from multiprocessing import Pool
import argparse

from img_to_ascii import _convert_img_to_ascii
from ascii_to_img import _convert_ascii_to_img


def _get_suffix(filename):
    """a.jpg -> jpg"""
    pos = filename.rfind('.')
    if pos == -1:
        return ''
    return filename[pos + 1:]


def _convert(frames, normal_size=None, sampling_step='auto'):
    imgs = []
    for frame in frames:
        ascii_str = _convert_img_to_ascii(frame, sampling_step=sampling_step)
        img = _convert_ascii_to_img(ascii_str)
        img = np.array(img)
        if normal_size is not None:
            img = cv2.resize(img, dsize=normal_size)
        imgs.append(img)
    return imgs


def convert(video_fp, wfp, start_frame=-1, end_frame=-1):
    """Convert using single-process

    arguments:
    video_fp - input video path
    wfp - output video path
    """
    reader = imageio.get_reader(video_fp)
    fps = reader.get_meta_data()['fps']

    # 1. collect all frames
    src_frames = []
    try:
        for i, frame in enumerate(reader):
            if 1 < start_frame < end_frame and end_frame > 1:
                if start_frame <= i <= end_frame:
                    src_frames.append(frame)
            else:
                src_frames.append(frame)
    except:
        pass

    shape = src_frames[0].shape
    normal_size = (shape[1], shape[0])  # for opencv resize
    print('Total frames: {}'.format(len(src_frames)))

    res_frames = _convert(src_frames, normal_size)
    imageio.mimwrite(wfp, res_frames, fps=fps, macro_block_size=None)


def chunk(n, m, frames):
    """Divide the n frames by n parts"""
    if n % m == 0:
        idx = list(range(0, n, n // m))
        idx.append(n)
    else:
        d = n // m
        r = n % m
        idx = list(range(0, n - r, d))

        # distribute the remainder value to
        offset = 1
        for j in range(m - r, m):
            idx[j] += offset
            offset += 1

        idx.append(n)

    res = []
    for i in range(len(idx) - 1):
        res.append(frames[idx[i]: idx[i + 1]])
    return res


def convert_mul(video_fp, wfp, processes=32, start_frame=-1, end_frame=-1, scale=-1, step=-1, sampling_step=4):
    """Convert using multi-process

    arguments:
    video_fp - input video path
    wfp - output video path
    processes - process number
    """
    reader = imageio.get_reader(video_fp)
    fps = reader.get_meta_data()['fps']

    # 1. collect all frames
    src_frames = []
    try:
        for i, frame in enumerate(reader):
            if 0 <= start_frame < end_frame and end_frame > 1:
                if start_frame <= i <= end_frame:
                    if step == -1:
                        src_frames.append(frame)
                    elif (i - start_frame) % step == 0:
                        src_frames.append(frame)
                if i > end_frame:
                    break
            else:
                src_frames.append(frame)
    except:
        pass
    # src_frames = src_frames[:100]

    shape = src_frames[0].shape
    if int(scale) != -1:
        normal_size = (int(scale * shape[1]), int(scale * shape[0]))  # for opencv resize
    else:
        normal_size = (shape[1], shape[0])
    print('Total frames: {}'.format(len(src_frames)))

    # 2. divide all frames equally
    frames_parts = chunk(len(src_frames), processes, src_frames)

    # 3. run using multi-process
    if sampling_step == -1:
        sampling_step == 'auto'
    pool = Pool(processes=processes)

    res_dict = {}
    for i in range(processes):
        res_dict[i] = pool.apply_async(func=_convert, args=(frames_parts[i], normal_size, sampling_step))

    pool.close()
    pool.join()

    # 4.
    res_frames = []
    for i in range(processes):
        res_frames.extend(res_dict[i].get())
    # 3
    # for i in range(0, len(res_frames)):
    # frames_res[i] = cv2.resize(frames_res[i], dsize=(1792, 1078))
    # print(res_frames[i].shape)

    if _get_suffix(wfp) in ['gif']:
        imageio.mimwrite(wfp, res_frames, fps=fps // 3)
    else:
        imageio.mimwrite(wfp, res_frames, fps=fps, macro_block_size=None)


def parse_args():
    parser = argparse.ArgumentParser(description='Ascii to image tool')
    parser.add_argument('-f', '--file', default='', type=str, help='Video file path')
    parser.add_argument('-w', '--write-file', default='', type=str, help='Generated video file write path')
    parser.add_argument('-p', '--processes', default=8, type=int, help='Process number')
    parser.add_argument('-s', '--start-frame', default=-1, type=int)
    parser.add_argument('-e', '--end-frame', default=-1, type=int)
    parser.add_argument('--step', default=-1, type=int)
    parser.add_argument('--scale', default=-1, type=float)
    parser.add_argument('--sampling-step', default=-1, type=int)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    convert_mul(video_fp=args.file, wfp=args.write_file, processes=args.processes,
                start_frame=args.start_frame, end_frame=args.end_frame, scale=args.scale, step=args.step,
                sampling_step=args.sampling_step)


if __name__ == '__main__':
    main()
