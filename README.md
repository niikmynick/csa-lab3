csa lab 3
========================

- Кобик Никита Алекссевич 
- P3224
- ```asm | stack | harv | hw | instr | binary -> struct | trap -> stream | mem | cstr | prob1 | spi```
- Базовый вариант, без усложнения

## Язык программирования

```ebnf
program         ::=     { statement }

statement       ::=     section       [ comment ] "\n"
                      | declaration   [ comment ] "\n"
                      | label         [ comment ] "\n"
                      | instruction   [ comment ] "\n"
                      |               [ comment ] "\n"

section         ::=     "." section_name
section_name    ::=     "data" | "code"

declaration     ::=     variable_name value
variable_name   ::=     <any of "a-z A-Z _"> { <any of "a-z A-Z 0-9 _"> }
value           ::=     number | string
number          ::=     { <any of "0-9"> }
string          ::=     "\"" <any char except "\"">* "\""
                      | "\'" <any char except "\'">* "\'"

label           ::=     label_name ":"
label_name      ::=     <any of "a-z A-Z _"> { <any of "a-z A-Z 0-9 _"> }

instruction     ::=     opcode_0
                      | opcode_1 operand
                      | opcode_2 label_name
              
opcode_0        ::=     "pop" 
                      | "read" 
                      | "write" 
                      | "compare" 
                      | "add" 
                      | "sub" 
                      | "mul" 
                      | "div" 
                      | "inc" 
                      | "dec" 
                      | "halt"

opcode_1        ::=     "push" 
                      | "save"
                      
opcode_2        ::=     "jmp" 
                      | "jeq" 
                      | "jne" 
                      | "jla" 
                      | "jle"

operand         ::=     value | variable_name

comment         ::=     "#" <any symbols except "\n">
```

Примечания:
- Код выполняется последовательно
- Все переменные должны быть объявлены до использования
- В программе не может быть меток, переменных и команд с одинаковыми именами
- Метки могут быть объявлены в любом месте программы, на отдельной строке
- Использование метки означает переход к инструкции, перед которой она определена
- Первая указанная команда в сегменте инструкций считается началом программы

## Система команд

Набор инструкций:
- `push` -- положить значение на вершину стека
- `pop` -- переместить stack pointer на одну ячейку вниз
- `save` -- сохранить значение с вершины стека в память по адресу, указанному в переменной
- `read` -- считать значение с клавиатуры и положить его на вершину стека
- `write` -- вывести значение с вершины стека на экран
- `compare` -- сравнить два значения со стека
- `jump` -- безусловный переход на метку
- `jeq` -- переход на метку, если результат последнего сравнения a == b
- `jne` -- переход на метку, если результат последнего сравнения a != b
- `jla` -- переход на метку, если результат последнего сравнения a > b
- `jle` -- переход на метку, если результат последнего сравнения a < b
- `add` -- сложить два значения с вершины стека
- `sub` -- вычесть два значения с вершины стека (нижнее минус верхнее)
- `mul` -- умножить два значения с вершины стека
- `div` -- разделить два значения с вершины стека (нижнее делить на верхнее)
- `inc` -- увеличить значение на вершине стека на 1
- `dec` -- уменьшить значение на вершине стека на 1
- `halt` -- завершить выполнение программы

Использование операндов со стека подразумевает его изъятие

## Организация памяти

Исходный код транслируется в бинарный файл, содержащий две секции - данные и инструкции
- В секции данных размер машинного слова не определен
- В секции инструкций размер машинного слова - 8 байт, содержащих тип инструкции (1 байт), тип операнда (1 байт) и сам операнд (6 байт)

Данные и инструкции имеют разные места хранения, согласно Гарвардской архитектуре 

У программиста нет доступа к памяти инструкций

В системе поддерживаются целые числа (integer), символы (char), строки (string)

Порты ввода-вывода отображаются в память. Для доступа к ним используются обращения к определенным заранее ячейкам в памяти данных

Адресация - прямая, с использованием переменных (подставляется адрес ячейки в памяти данных) и меток (адрес ячейки в памяти инструкций)

## Транслятор

Трансляция реализуется в несколько этапов:
- Проверка синтаксиса программы
- Парсинг переменных и лейблов
- Парсинг инструкций
- Подстановка адресов переменных и лейблов
- Генерация бинарного кода

```
python assemble_unit.py <source_filepath> <target_filepath>
```

## Модель процессора

Описание реализации:
- Процесс моделирования отслеживается по инструкциям
- Программа выполняется последовательно
- Остановка программы происходит:
  - при выполнении команды `halt`
  - при обращении к несуществующей ячейке памяти
  - при возникновении ошибки во время выполнения
- Переполнение стека или памяти в данной реализации не предусмотрено

Флаги:
- `zero` -- устанавливается, если результат последнего сравнения a == b или результат последней арифметической операции равен 0
- `negative` -- устанавливается, если результат последнего сравнения a < b или результат последней арифметической операции отрицателен

```
python machine.py <bin_filepath> <input_filepath> <output_filepath> <log_filepath>
```

## Тестирование

Тестирование выполняется при помощи golden тестов

```
pytest test.py
```

## Статистика

```plain
|     Тест      | Инструкций | Исполнено |  Такт  |
|  hello world  |     3      |   3       |   47   | 
|  prob1        |     43     |   28918   | 279074 |
|  prob5        |     55     |   2221    | 21661  |
|  cat          |     3      |   3       |   40   |
```
