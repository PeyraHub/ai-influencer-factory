import numpy as np
from PIL import Image

from engine.identity.qa_checklist import check_resolution, run_automated_qa, sharpness_score


def _write_image(tmp_path, array: np.ndarray, name: str) -> str:
    path = tmp_path / name
    Image.fromarray(array).save(path)
    return str(path)


def test_sharpness_score_ranks_sharp_above_blurry(tmp_path):
    rng = np.random.default_rng(42)
    sharp = rng.integers(0, 256, size=(256, 256, 3), dtype=np.uint8)
    sharp_path = _write_image(tmp_path, sharp, "sharp.png")

    blurry = np.full((256, 256, 3), 128, dtype=np.uint8)
    blurry_path = _write_image(tmp_path, blurry, "blurry.png")

    assert sharpness_score(sharp_path) > sharpness_score(blurry_path)


def test_check_resolution_pass_and_fail(tmp_path):
    big = np.zeros((1024, 1024, 3), dtype=np.uint8)
    big_path = _write_image(tmp_path, big, "big.png")
    assert check_resolution(big_path, 1024, 1024) is True

    small = np.zeros((512, 512, 3), dtype=np.uint8)
    small_path = _write_image(tmp_path, small, "small.png")
    assert check_resolution(small_path, 1024, 1024) is False


def test_run_automated_qa_auto_pass_flag(tmp_path):
    rng = np.random.default_rng(7)
    noisy_hires = rng.integers(0, 256, size=(1024, 1024, 3), dtype=np.uint8)
    path = _write_image(tmp_path, noisy_hires, "noisy.png")

    result = run_automated_qa(path)
    assert result.resolution_ok is True
    assert result.auto_pass is True

    flat_lowres = np.full((256, 256, 3), 200, dtype=np.uint8)
    path2 = _write_image(tmp_path, flat_lowres, "flat.png")
    result2 = run_automated_qa(path2)
    assert result2.auto_pass is False
