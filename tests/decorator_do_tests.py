import unittest

from pyposto.decorators import do


def hello():
    print('helloz')


@do(hello)
def world():
    print('world')


class MyTestCase(unittest.TestCase):
    def test_something(self):
        world()
        # self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
