import unittest

import numpy as np

from cumcm_starter.evaluation import entropy_topsis


class EntropyTopsisTests(unittest.TestCase):
    def test_weights_and_scores_have_expected_shape(self) -> None:
        matrix = np.array(
            [
                [90.0, 10.0, 0.80],
                [80.0, 8.0, 0.90],
                [70.0, 12.0, 0.85],
            ]
        )
        weights, scores = entropy_topsis(matrix, [True, False, True])
        self.assertEqual(weights.shape, (3,))
        self.assertEqual(scores.shape, (3,))
        self.assertAlmostEqual(float(weights.sum()), 1.0)
        self.assertTrue(np.all((0.0 <= scores) & (scores <= 1.0)))

    def test_cost_indicator_is_reversed(self) -> None:
        matrix = np.array([[100.0, 4.0], [100.0, 8.0], [100.0, 12.0]])
        _, scores = entropy_topsis(matrix, [True, False])
        self.assertGreater(scores[0], scores[-1])

    def test_invalid_shape_raises(self) -> None:
        with self.assertRaises(ValueError):
            entropy_topsis([[1.0, 2.0]], [True, False])


if __name__ == "__main__":
    unittest.main()

