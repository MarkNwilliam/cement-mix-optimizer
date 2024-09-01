import unittest
from optimiser import optimise, feasible, blend_quality


class TestOptimiser(unittest.TestCase):
    def test_result_is_feasible(self):
        best = optimise()
        self.assertIsNotNone(best)
        cost, frac = best
        self.assertAlmostEqual(sum(frac.values()), 1.0, places=6)
        self.assertTrue(feasible(frac))

    def test_quality_within_targets(self):
        _, frac = optimise()
        C3S, C3A, SO3, LOI, _ = blend_quality(frac)
        self.assertGreaterEqual(C3S, 55.0)
        self.assertLessEqual(C3A, 9.0)
        self.assertGreaterEqual(SO3, 2.0)
        self.assertLessEqual(SO3, 3.5)
        self.assertLessEqual(LOI, 5.0)

    def test_cheaper_than_pure_clinker(self):
        cost, frac = optimise()
        self.assertLess(cost, 60.0)  # blended mix beats 100% clinker price


if __name__ == "__main__":
    unittest.main()
