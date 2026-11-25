"""Tests for reconstructing counts from yesterday's count and a predicted delta."""
import numpy as np

from src.experiment import reconstruct_counts


def test_reconstruct_counts_adds_predicted_deltas():
    yesterday_counts = np.array([10, 20, 30, 40])
    predicted_delta = np.array([3, -5, 0, -45])

    reconstructed = reconstruct_counts(yesterday_counts, predicted_delta)

    np.testing.assert_array_equal(reconstructed, [13, 15, 30, -5])
