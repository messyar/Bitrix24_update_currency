"""
If ADD_NEW_CURRENCY = True currency, that not found in Bitrix24 will be added
else it'll be ignoring
"""
ADD_NEW_CURRENCY = True
"""
This constant sets format for currency locales, for now only 'ru' supports
"""
LOCALES = {
    'ru':
        {
            'DEC_POINT': '.',
            'DECIMALS': 2,
            'HIDE_ZERO': "Y"
        },
}
