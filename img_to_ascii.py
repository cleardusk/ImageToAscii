#!/usr/bin/env python
# coding: utf-8

from __future__ import division

import numpy as np
import cv2
import argparse

# intensity -> character map
ramp = '@@@@@@@######MMMBBHHHAAAA&&GGhh9933XXX222255SSSiiiissssrrrrrrr;;;;;;;;:::::::,,,,,,,........'
ramp_numpy = np.array(list(ramp))


def build_ascii(indices):
    res = ramp_numpy[indices]
    s = ''
    h = indices.shape[0]
    for i in range(h):
        s += res[i].tostring() + '\n'
    return s


def _convert_img_to_ascii(img, sampling_step='auto', aspect=2, norm_style='mean', eq_hist_flg=True):
    """
    :param img: ndarray of an image
    :param sampling_step: sampling ratio
    :param aspect: samping ratio of height/width
    :param norm_style: gray or mean
    :param eq_hist_flg:
    :return: ascii string
    """
    sampling_step = img.shape[0] // 128 if sampling_step == 'auto' else int(sampling_step)

    if img.ndim == 3:
        if norm_style == 'mean':
            img = np.mean(img, axis=2)
        elif norm_style == 'gray':
            img = .2126 * img[:, :, 0] + .7152 * img[:, :, 1] + .0722 * img[:, :, 2]
        else:
            raise Exception('Unknown norm style: {}'.format(norm_style))

    if eq_hist_flg:
        img = cv2.equalizeHist(img.astype(np.uint8))

    src_height, src_width = img.shape[:2]
    dst_height, dst_width = int(src_height / sampling_step / aspect), int(src_width / sampling_step)

    indices = np.zeros((dst_height, dst_width), dtype=np.float32)
    step_h, step_w = int(sampling_step * aspect), sampling_step
    for j in range(step_h):
        for k in range(step_w):
            indices += img[j:j + step_h * dst_height:step_h, k:k + step_w * dst_width: step_w]

    indices = (indices / (step_h * step_w) / 256 * len(ramp)).astype(np.uint32)
    return build_ascii(indices)


def convert_img_to_ascii(args):
    img = cv2.imread(args.file, cv2.IMREAD_UNCHANGED)
    ascii = _convert_img_to_ascii(img, sampling_step=args.sampling_step, aspect=args.aspect)
    if args.write_file in ['', None]:
        args.write_file = args.file.replace('.jpg', '.txt')

    open(args.write_file, 'w').write(ascii)


def parse_args():
    parser = argparse.ArgumentParser(description='Image to ascii txt tool')
    parser.add_argument('-f', '--file', default='', type=str, help='Image file path')
    parser.add_argument('-s', '--sampling-step', default='auto', type=str, help='Sampling step')
    parser.add_argument('-w', '--write-file', default='', type=str, help='Generated file write path')
    parser.add_argument('-a', '--aspect', default=2, type=float, help='Aspect of layout')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    convert_img_to_ascii(args)


if __name__ == '__main__':
    main()
