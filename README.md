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
string          ::=     "\"" { <any symbols except "\""> } "\""
                      | "\'" { <any symbols except "\'"> } "\'"

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

Данные и инструкции имеют разные места хранения, согласно Гарвардской архитектуре 

```
    data memory
+------------------+
| 00 : input port  |
| 01 : output port |
| 02 :     ...     |
+------------------+

 instruction memory 
+------------------+
| 00 :     ...     |
|          ...     |
| n  :     403     |
+------------------+
```

Исходный код транслируется в бинарный файл, содержащий две секции - данные и инструкции
- В секции данных размер машинного слова не определен
- В секции инструкций размер машинного слова - 8 байт, содержащих тип инструкции (1 байт), тип операнда (1 байт) и сам операнд (6 байт)

У программиста нет доступа к памяти инструкций

В системе поддерживаются целые числа (integer), символы (char), строки (string)

Порты ввода-вывода отображаются в память. Для доступа к ним используются обращения к определенным заранее ячейкам в памяти данных

Адресация - прямая, с использованием переменных (подставляется адрес ячейки в памяти данных) и меток (адрес ячейки в памяти инструкций)

## Транслятор

```
python assemble_unit.py <source_filepath> <target_filepath>
```

Трансляция реализуется в несколько этапов:
- Очистка исходного кода от пустых строк и комментариев
- Проверка синтаксиса программы
- Парсинг переменных и лейблов
- Парсинг инструкций
- Подстановка адресов переменных и лейблов
- Генерация бинарного кода

## Модель процессора

```
python machine.py <bin_filepath> <input_filepath> <output_filepath> <log_filepath>
```

```text
Control Unit

+---------------------+
|      Data Path      |
+---------------------+
    |  |       ^  ^
    v  v       |  |                                                                    -1   sel
+---------------------+       +----------------------+       +----------------------+ --- > +---------------------+
| Instruction Handler | --- > |  Interruption Stack  | < --- |          SP          | < --- |         MUX         |
+---------------------+       +----------------------+       +----------------------+ --- > +---------------------+
           ^                  latch sp  |                                              +1
           |                            v
           |                  +----------------------+
           +----------------- | Interruption Handler |
                              +----------------------+
```

```text
Data Path
                                                                                            +---+    +---+
                                                                                            | N |    | Z |            sel
                                                           +--------------------+       +---+---+----+---+----+       +---------------------+        +---------------------+
                                                           |    I/O  Devices    |       |         ALU         | < --- |         MUX         | < ---  |          1          |
                                                           +--------------------+       +---------------------+       +---------------------+        +---------------------+
                                                                |         ^                  |     ^                   tos + 1   ^
                                                                |         |                  |     |     +-----------------------+              
                                                                v         |                  v     |     |                                        -1   sel
                                                           +--------------------+       +---------------------+       +----------------------+ --- > +---------------------+
                                                           |  I/O  Controllers  |       |     Data  Stack     | < --- |          SP          | < --- |         MUX         |
                                                           +--------------------+       +---------------------+       +----------------------+ --- > +---------------------+
                                                                |         |                  |          ^                                       +1      
                                                                v         v                  v          |      
                                                           +--------------------+ < --- +---------------------+
                                                       +-> |     Data Memory    |       |    Control  Unit    |
                                                       |   +--------------------+ --- > +---------------------+
+--------------------+       +--------------------+    |                                           ^
|     Translator     | --- > |       Loader       | ---+                                           |                                                            
+--------------------+       +--------------------+    |                                           |                                            -1   sel
                                                       |   +--------------------+       +---------------------+       +----------------------+ --- > +---------------------+
                                                       +-> | Instruction Memory | --- > |  Instruction Stack  | < --- |          SP          | < --- |         MUX         |
                                                           +--------------------+       +---------------------+       +----------------------+ --- > +---------------------+
                                                                                                                                                +1
                                                                                                                                                
```

[//]: # (![DP.svg]&#40;schemes/DP.svg&#41;)
[//]: # (![CU.svg]&#40;schemes/CU.svg&#41;)

Описание реализации:
- Процесс моделирования отслеживается по инструкциям
- Программа выполняется последовательно
- Остановка программы происходит:
  - при выполнении команды `halt`
  - при обращении к несуществующей ячейке памяти
  - при возникновении ошибки во время выполнения
- Переполнение стека или памяти в данной реализации не предусмотрено
- Перед выполнением инструкции происходит проверка на вызов прерывания

Флаги:
- `zero` -- устанавливается, если результат последнего сравнения a == b или результат последней арифметической операции равен 0
- `negative` -- устанавливается, если результат последнего сравнения a < b или результат последней арифметической операции отрицателен

Набор инструкций:

| Инструкция | Количество тактов |
|:----------:|:-----------------:|
|    push    |         2         |
|    pop     |         2         |
|    read    |         1         |
|   write    |         2         |
|  compare   |         3         |
|    jump    |         3         |
|    jla     |      1 или 2      |
|    jle     |      1 или 2      |
|    jeq     |      1 или 2      |
|    jne     |      1 или 2      |
|    add     |         4         |
|    sub     |         4         |
|    mul     |         4         |
|    div     |      3 или 4      |
|    inc     |         3         |
|    dec     |         3         |
|    save    |      2 или 3      |
|    halt    |         1         |

## Тестирование

```
pytest test.py
```

Тестирование выполняется при помощи golden тестов

CI для Github Actions разделен на две задачи

Lint:
```yaml
name: Python Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install mypy pytest
    - name: Run mypy linter
      run: |
        mypy .
```

Test:
```yaml
name: Python Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest
          pip install pytest-golden
      - name: Run golden tests
        run: |
           pytest test.py
```

Пример проверки исходного кода
```text
pytest test.py
============================= test session starts ==============================
collecting ... collected 5 items

test.py::test_translator_asm_and_machine[golden/test/prob1.yml] 
test.py::test_translator_asm_and_machine[golden/test/cat.yml] 
test.py::test_translator_asm_and_machine[golden/test/prob5.yml] 
test.py::test_translator_asm_and_machine[golden/test/hello_user.yml] 
test.py::test_translator_asm_and_machine[golden/test/hello_world.yml] 

============================== 5 passed in 4.04s ===============================
```

## Статистика

|    Тест     | Инструкций | Исполнено |  Такт  |
|:-----------:|:----------:|:---------:|:------:|
| hello world |     3      |     3     |   47   | 
|    prob1    |     43     |   28918   | 279074 |
|    prob5    |     55     |   2221    | 21661  |
|     cat     |     3      |     3     |   40   |
