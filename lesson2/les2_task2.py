# Есть файл orders в формате JSON с информацией о заказах. Написать скрипт,
# автоматизирующий его заполнение данными.

# Для этого:
# * Создать функцию write_order_to_json(), в которую передается 5 параметров
# — товар (item), количество (quantity), цена (price), покупатель (buyer),
# дата (date). Функция должна предусматривать запись данных в виде словаря
# в файл orders.json. При записи данных указать величину отступа
# в 4 пробельных символа;
#
# * Проверить работу программы через вызов функции write_order_to_json()
# с передачей в нее значений каждого параметра.

import json

from chardet import detect

OUTPUT_FILE = 'orders.json'


def write_order_to_json(item, quantity, price, buyer, date):
    with open(OUTPUT_FILE, 'rb') as file:
        content = file.read()
    encoding = detect(content)['encoding']

    with open(OUTPUT_FILE, encoding=encoding) as f_n:
        obj = json.load(f_n)

    obj['orders'].append({
        'item': item,
        'quantity': quantity,
        'price': price,
        'buyer': buyer,
        'date': date,
    })

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f_n:
        json.dump(obj, f_n, sort_keys=True, indent=4)

    print(obj)


# Каждый вызов функции добавляет (не заменяет) данные в файл
write_order_to_json('Processor', 3, '50.30', 'TRY company', '07/19/2020')
