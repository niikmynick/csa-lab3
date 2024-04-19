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
                      | "je" 
                      | "jne" 
                      | "jla" 
                      | "jle"

operand         ::=     value | variable_name

comment         ::=     "#" <any symbols except "\n">
```