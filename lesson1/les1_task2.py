# Каждое из слов «class», «function», «method» записать в байтовом типе без
# преобразования в последовательность кодов (не используя методы encode
# и decode) и определить тип, содержимое и длину соответствующих переменных.

words = [b'class', b'function', b'method']

for word in words:
    print(f'Тип: {type(word)} Длина: {len(word)} Содержимое: |{word}|')

# Output:
# Тип: <class 'bytes'> Длина: 5 Содержимое: |b'class'|
# Тип: <class 'bytes'> Длина: 8 Содержимое: |b'function'|
# Тип: <class 'bytes'> Длина: 6 Содержимое: |b'method'|
