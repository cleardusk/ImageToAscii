#!/usr/bin/env python3
# coding: utf-8
import cv2

import imageio
from PIL import Image
import numpy as np
from img_to_ascii import _convert_img_to_ascii
from ascii_to_img import _convert_ascii_to_img

from multiprocessing import Pool


def test_read_video():
    video_dp = 'videos/dula.mp4'
    reader = imageio.get_reader(video_dp)

    # collect all frames
    src_imgs = []
    try:
        for i, frame in enumerate(reader):
            src_imgs.append(frame)
    except:
        pass
    print(len(src_imgs))


def convert(frames):
    imgs = []
    for frame in frames:
        ascii_str = _convert_img_to_ascii(frame)
        lines = ascii_str.strip().split('\n')
        img = _convert_ascii_to_img(lines)
        img = np.array(img)
        # img = img[:, 300:-500]
        imgs.append(img)
    return imgs


def main2():
    video_dp = 'videos/dula.mp4'
    reader = imageio.get_reader(video_dp)

    # collect all frames
    src_frames = []
    try:
        for i, frame in enumerate(reader):
            src_frames.append(frame)
    except:
        pass
    # src_frames = src_frames[:100]
    print(len(src_frames))

    # 2.1
    def chunk(n, m, frames):
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

    processes = 32
    frames_parts = chunk(len(src_frames), processes, src_frames)

    # imgs = convert(frames_parts[0])

    pool = Pool(processes=processes)
    # res = pool.map(convert, src_imgs)

    res_dict = {}
    for i in range(processes):
        res_dict[i] = pool.apply_async(func=convert, args=(frames_parts[i],))

    pool.close()
    pool.join()

    print(len(res_dict))

    frames_res = []
    for i in range(processes):
        frames_res.extend(res_dict[i].get())
    # 3
    for i in range(0, len(frames_res)):
        frames_res[i] = cv2.resize(frames_res[i], dsize=(1792, 1078))
        print(frames_res[i].shape)
    imageio.mimwrite('res/dula2.mp4', frames_res, fps=30, macro_block_size=None)


def main():
    video_dp = 'videos/dula.mp4'
    reader = imageio.get_reader(video_dp)
    imgs = []
    cnt = 0
    for i, frame in enumerate(reader):
        cnt += 1
        print('Frame: {}'.format(cnt))
        ascii_str = _convert_img_to_ascii(frame)
        lines = ascii_str.strip().split('\n')
        img = _convert_ascii_to_img(lines)
        # img.show()
        img = np.array(img)
        img = img[:, 300:-500]

        # img = img[:, :, ::-1]
        imgs.append(img)

    for i in range(1, len(imgs)):
        imgs[i] = imgs[i].resize(dsize=imgs[0].shape)

    imageio.mimwrite('res/dula2.mp4', imgs, fps=30)


if __name__ == '__main__':
    # main()
    # test_read_video()
    main2()
