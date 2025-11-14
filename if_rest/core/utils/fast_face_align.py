"""
Based on https://github.com/deepinsight/insightface/tree/master/python-package/insightface/utils/face_align.py
Improvements:
 - Removed SciPy dependency
 - Removed parts of code not used for ArcFace alignment
 - Added Numba NJIT to speed up computations
 - Added batch processing support
"""

import cv2
import numba as nb
import numpy as np

arcface_src = np.array([
    [38.2946, 51.6963],
    [73.5318, 51.5014],
    [56.0252, 71.7366],
    [41.5493, 92.3655],
    [70.7299, 92.2041]
], dtype=np.float32)

arcface_src = np.expand_dims(arcface_src, axis=0)


@nb.njit(cache=True, fastmath=True)
def np_mean(array, axis):
    """
    Compute mean of a 2D array along axis 0 or 1.
    Returns a 1D array of means for the other axis.
    """
    assert array.ndim == 2
    assert axis in (0, 1)
    if axis == 0:
        out = np.empty(array.shape[1], dtype=np.double)
        n = array.shape[0]
        for j in range(array.shape[1]):
            s = 0.0
            for i in range(n):
                s += array[i, j]
            out[j] = s / n
        return out
    else:
        out = np.empty(array.shape[0], dtype=np.double)
        n = array.shape[1]
        for i in range(array.shape[0]):
            s = 0.0
            for j in range(n):
                s += array[i, j]
            out[i] = s / n
        return out


@nb.njit(cache=True, fastmath=True)
def np_var(array, axis):
    """
    Compute variance of a 2D array along axis 0 or 1.
    """
    assert array.ndim == 2
    assert axis in (0, 1)
    if axis == 0:
        mean = np_mean(array, 0)
        out = np.empty(array.shape[1], dtype=np.double)
        n = array.shape[0]
        for j in range(array.shape[1]):
            s = 0.0
            m = mean[j]
            for i in range(n):
                d = array[i, j] - m
                s += d * d
            out[j] = s / n
        return out
    else:
        mean = np_mean(array, 1)
        out = np.empty(array.shape[0], dtype=np.double)
        n = array.shape[1]
        for i in range(array.shape[0]):
            s = 0.0
            m = mean[i]
            for j in range(n):
                d = array[i, j] - m
                s += d * d
            out[i] = s / n
        return out


@nb.njit(cache=True, fastmath=True)
def np_std(array, axis):
    """
    Compute standard deviation of a 2D array along axis 0 or 1.
    """
    v = np_var(array, axis)
    out = np.empty(v.shape[0], dtype=np.double)
    for i in range(v.shape[0]):
        out[i] = np.sqrt(v[i])
    return out


@nb.njit(fastmath=True, cache=True)
def _umeyama(src, dst, estimate_scale):
    """
    Estimates the transformation matrix using the Umeyama algorithm.

    Args:
        src: The source points.
        dst: The destination points.
        estimate_scale: Whether to estimate the scale factor.

    Returns:
        A 3x3 transformation matrix.
    """
    num = src.shape[0]
    dim = src.shape[1]

    # Compute mean of src and dst.
    src_mean = np_mean(src, 0)
    dst_mean = np_mean(dst, 0)

    # Subtract mean from src and dst.
    src_demean = src - src_mean
    dst_demean = dst - dst_mean

    # Eq. (38).
    A = dst_demean.T @ src_demean / num

    # Eq. (39).
    d = np.ones((dim,), dtype=np.double)
    if np.linalg.det(A) < 0:
        d[dim - 1] = -1

    T = np.eye(dim + 1, dtype=np.double)

    U, S, V = np.linalg.svd(A)

    # Eq. (40) and (43).
    rank = np.linalg.matrix_rank(A)
    if rank == 0:
        return np.nan * T
    elif rank == dim - 1:
        if np.linalg.det(U) * np.linalg.det(V) > 0:
            T[:dim, :dim] = U @ V
        else:
            s = d[dim - 1]
            d[dim - 1] = -1
            T[:dim, :dim] = U @ np.diag(d) @ V
            d[dim - 1] = s
    else:
        T[:dim, :dim] = U @ np.diag(d) @ V

    scale = 1.0
    if estimate_scale:
        # Eq. (41) and (42).
        div = np_var(src_demean, 0)
        div = np.sum(div)
        scale = scale / div * (S @ d)

    T[:dim, dim] = dst_mean - scale * (np.ascontiguousarray(T[:dim, :dim]) @ np.ascontiguousarray(src_mean.T))
    T[:dim, :dim] *= scale

    return T


@nb.njit(cache=True, fastmath=True)
def estimate_norm(lmk, image_size=112, mode='arcface'):
    """
    Estimates the norm of a given landmarks.

    Args:
        lmk: The landmark points.
        image_size: The size of the output image (default is 112).
        mode: The alignment mode (default is 'arcface').

    Returns:
        A 2x3 transformation matrix representing the estimated norm.
    """
    assert lmk.shape == (5, 2)

    lmk_tran = np.ones((5, 3))
    lmk_tran[:, :2] = lmk

    assert image_size == 112
    src = arcface_src

    params = _umeyama(lmk, src[0], True)
    M = params[0:2, :]
    return M


@nb.njit(cache=True, fastmath=True)
def estimate_norm_batch(lmks, image_size=112, mode='arcface'):
    """
    Estimates the norms of multiple landmarks in batch mode.

    Args:
        lmks: A list of landmark points.
        image_size: The size of the output images (default is 112).
        mode: The alignment mode (default is 'arcface').

    Returns:
        A list of 2x3 transformation matrices representing the estimated norms.
    """
    Ms = []
    for lmk in lmks:
        Ms.append(estimate_norm(lmk, image_size, mode))
    return Ms


def norm_crop(img, landmark, image_size=112, mode='arcface'):
    """
    Crops an image to a specified size using the estimated norm.

    Args:
        img: The input image.
        landmark: The landmark points.
        image_size: The size of the output image (default is 112).
        mode: The alignment mode (default is 'arcface').

    Returns:
        A cropped image.
    """
    M = estimate_norm(landmark, image_size, mode)
    warped = cv2.warpAffine(img, M, (image_size, image_size), borderValue=0.0)
    return warped


def norm_crop_batched(img, landmarks, image_size=112, mode='arcface'):
    """
    Crops multiple images to a specified size using the estimated norms.

    Args:
        img: The input image.
        landmarks: A list of landmark points.
        image_size: The size of the output images (default is 112).
        mode: The alignment mode (default is 'arcface').

    Returns:
        A list of cropped images.
    """
    Ms = estimate_norm_batch(landmarks, image_size, mode)
    crops = []
    for M in Ms:
        warped = cv2.warpAffine(img, M, (image_size, image_size), borderValue=0.0)
        crops.append(warped)
    return crops
