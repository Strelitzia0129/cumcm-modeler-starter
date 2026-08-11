import unittest

from cumcm_starter.sensitivity import one_at_a_time_sensitivity


class SensitivityTests(unittest.TestCase):
    def test_two_rows_per_parameter(self) -> None:
        def model(parameters: dict[str, float]) -> float:
            return parameters["a"] + 2.0 * parameters["b"]

        result = one_at_a_time_sensitivity(model, {"a": 1.0, "b": 3.0}, 0.1)
        self.assertEqual(len(result), 4)
        self.assertEqual(set(result["parameter"]), {"a", "b"})
        self.assertEqual(set(result["parameter_change"]), {-0.1, 0.1})

    def test_invalid_change_raises(self) -> None:
        with self.assertRaises(ValueError):
            one_at_a_time_sensitivity(lambda values: values["x"], {"x": 1.0}, 1.0)


if __name__ == "__main__":
    unittest.main()

