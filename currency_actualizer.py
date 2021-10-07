from bitrix24 import Bitrix24, BitrixError
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from os import environ

try:
    from currency_actualizer_config import CURRENCY_TO_UPDATE, ADD_NEW_CURRENCY, LOCALES
except ImportError as import_error:
    print("""Config file import error. Possible, you need to create currency_actualizer_config.py
          with list constant, named CURRENCY_TO_UPDATE
          For example \n
          CURRENCY_TO_UPDATE=["USD", "EUR"]\n
          ADD_NEW_CURRENCY=True\n
          LOCALES = [{
                        'ru':
                                {
                                    'DEC_POINT': '.',
                                    'DECIMALS': 2,
                                    'HIDE_ZERO': 'Y'
                                },
          }]""")


def parse_exchange_rates(currency_to_update: list) -> dict:
    """
    This function parses the exchange rates from the Central bank of Russia website
    :return: list of dicts with exchange information from cbr.ru
    """

    result = []
    day = datetime.now().day
    month = datetime.now().month
    year = datetime.now().year

    if int(day) < 10:
        day = '0%s' % day

    if int(month) < 10:
        month = '0%s' % month

    try:
        # Request to API of cbr.
        get_xml = requests.get(
            'http://www.cbr.ru/scripts/XML_daily.asp?date_req=%s/%s/%s' % (day, month, year)
        )

        # parse XML using ElementTree
        structure = ''
        if get_xml.ok:
            structure = ET.fromstring(get_xml.content)
        else:
            print(get_xml)
            return result

    except requests.exceptions.RequestException as req_exc:
        print(req_exc)
        return result

    try:
        # Finding exchange rates
        currency_list = structure.findall("./Valute")
        for curr_currency in currency_list:
            curr_currency_text = curr_currency.find('CharCode').text

            if curr_currency_text in currency_to_update:

                currency_info = {}
                for curr_tag in curr_currency:
                    if curr_tag.tag == 'Value':
                        currency_info[curr_tag.tag] = curr_tag.text.replace(',', '.')
                    else:
                        currency_info[curr_tag.tag] = curr_tag.text
                result.append(currency_info)

    except ET.ParseError as PE:
        print(PE)
        result = False

    return result


def update_currency() -> None:
    """
    Main function, check if base currency is RUB, if not stop execute, else update exchenge
     rate in Bitrix24
    :return: None
    """
    try:
        url_to_api = environ['URL_TO_BITRIX24']
    except Exception as name_error:
        print("Can't find Environment variable %s" % name_error)
        return

    bx24 = Bitrix24(url_to_api)

    try:
        base_currency = bx24.callMethod('crm.currency.base.get')

    except BitrixError as message:
        print(message)

    if base_currency != 'RUB':
        print('Base currency not RUB, this script work only if base currency in Bitrix24 is RUB')
        return

    currency_to_update = CURRENCY_TO_UPDATE
    if not CURRENCY_TO_UPDATE:
        print('Please, specify the currencies to update the exchange rate in the currency_actualizer_file.py'
              ' as a list constant named CURRENCY_TO_UPDATE. For example CURRENCY_TO_UPDATE=["USD", "EUR"]')
        return

    currency_pairs = parse_exchange_rates(currency_to_update)
    if not currency_pairs:
        print("Error! Exchange rate parse from cbr.ru failed.")
        return

    not_added_currency = []
    for curr_element in currency_pairs:
        try:
            bx24.callMethod('crm.currency.update', id=curr_element['CharCode'],
                            fields={'AMOUNT_CNT': curr_element['Nominal'],
                                    'AMOUNT': curr_element['Value']})

        except BitrixError as message:

            if message.args[0] == 'Currency is not found':
                if ADD_NEW_CURRENCY:
                    print('Missed currency ', curr_element['CharCode'])

                    fields = {'CURRENCY': curr_element['CharCode'], 'AMOUNT_CNT': curr_element['Nominal'],
                              'AMOUNT': curr_element['Value'], 'SORT': 1000}
                    locale = {}

                    for key, value in LOCALES.items():
                        locale[key] = value

                        if key == 'ru':
                            locale[key]['FORMAT_STRING'] = '%23' + ' ' + curr_element['Name'].split()[1]
                            locale[key]['FULL_NAME'] = curr_element['Name']
                            locale[key]['THOUSANDS_VARIANT'] = "C"
                            locale[key]['THOUSANDS_SEP'] = "'"

                    fields['LANG'] = locale
                    bx24.callMethod('crm.currency.add', fields=fields)

                    print('Currency {} was added'.format(curr_element['CharCode']))
                else:
                    not_added_currency.append(curr_element['CharCode'])
            else:
                print(message)

    if not ADD_NEW_CURRENCY:
        print("""In config file constant ADD_NEW_CURRENCY={}. Because of that currency {} just 
        pass and don't be added in yours Bitrix24""".format(ADD_NEW_CURRENCY, not_added_currency))


if __name__ == '__main__':
    update_currency()
