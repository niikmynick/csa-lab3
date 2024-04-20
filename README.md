csa lab 3
========================

- Кобик Никита Алекссевич 
- P3224
- ```asm | stack | harv | hw | instr | binary -> struct | trap -> stream | mem | cstr | prob1 | spi```
- Базовый вариант

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

Операции:

- `push` -- положить значение на вершину стека
- `pop` -- переместить stack pointer на одну ячейку вниз
- `save` -- сохранить значение с вершины стека в память по адресу, указанному в переменной
- `read` -- считать значение с клавиатуры и положить его на вершину стека
- `write` -- вывести значение с вершины стека на экран
- `compare` -- сравнить два значения со стека
- `jmp` -- безусловный переход на метку
- `jeq` -- переход на метку, если результат последнего сравнения a == b
- `jne` -- переход на метку, если результат последнего сравнения a != b
- `jla` -- переход на метку, если результат последнего сравнения a > b
- `jle` -- переход на метку, если результат последнего сравнения a < b
- `add` -- сложить два значения со стека
- `sub` -- вычесть два значения со стека (нижнее минус верхнее)
- `mul` -- умножить два значения со стека
- `div` -- разделить два значения со стека (нижнее делить на верхнее)
- `inc` -- увеличить значение на вершине стека на 1
- `dec` -- уменьшить значение на вершине стека на 1
- `halt` -- завершить выполнение программы

Примечания:

- В программе не может быть меток, переменных и команд с одинаковыми именами
- Все переменные должны быть объявлены до использования
- Метки могут быть объявлены в любом месте программы


## Организация памяти

## Система команд

## Транслятор

## Модель процессора

## Тестирование
