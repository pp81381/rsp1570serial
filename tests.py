import logging
import unittest

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    suite = unittest.defaultTestLoader.discover('rsp1570serial/tests')
    unittest.TextTestRunner(verbosity=2).run(suite)