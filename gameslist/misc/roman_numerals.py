'''
Helper class for working with Roman Numerals.
'''

class RomanNumeral:
    def __init__(self, roman):
        self.roman = RomanNumeral.valid_roman(roman)
        self.arabic = RomanNumeral.convert_to_arabic(roman)

    @staticmethod
    def convert_to_arabic(roman):

        pass

    @staticmethod
    def convert_to_roman(arabic):
        pass

    @staticmethod
    def valid_roman(roman):
        pass


# def roman_to_arabic_or_false(test_string):
#     #so anything outside of that, return false
#     #I V X L C D M
#     #1 5 10 50 100 500 1000
#     return False