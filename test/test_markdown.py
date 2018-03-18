import unittest
import markdownconverter

class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        md = markdownconverter.hangoutschat_markdown_converter()
        md.convert
        self.assertEqual(md.convert('**test**'), '*test*')
        self.assertEqual(md.convert('This is [a link](http://www.errbot.io).'), 'This is <http://www.errbot.io|a link>.')

if __name__ == '__main__':
    unittest.main()