import unittest, math
from catalog import LABS
from modules import design, structures, robotics
class Models(unittest.TestCase):
    def test_defaults(self):
        for department,labs in LABS.items():
            for name,(fn,params) in labs.items():
                with self.subTest(name=name):
                    r=fn(*[p[3] for p in params])
                    self.assertTrue(all(math.isfinite(v) for v in r["metrics"].values()))
                    r["fig"].to_json()
                    r["chart"].to_json()
    def test_reference(self):
        self.assertAlmostEqual(design.spring(100,25)["metrics"]["Deflection (mm)"],4)
        self.assertAlmostEqual(design.gears(20,40,1000,20,0)["metrics"]["Output rpm"],500)
        self.assertAlmostEqual(robotics.arm(1,1,0,90)["metrics"]["End Y (m)"],1)
if __name__=="__main__": unittest.main()
