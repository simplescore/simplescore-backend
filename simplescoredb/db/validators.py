from django.core.validators import RegexValidator
import re

SHA3SUM_LENGTH = 128
SHA3_REGEX = re.compile(f'[0-9a-f]{SHA3SUM_LENGTH}')

class SHA3SumValidator(RegexValidator):
    def __init__(self):
        super().__init__(regex=SHA3_REGEX)
