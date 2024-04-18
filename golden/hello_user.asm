.data
    name_request "What is your name?"
    welcome_beginning "Hello, "
    exclamation_point "!"

.code
    push name_request
    write
    pop

    read

    push welcome_beginning
    write
    pop

    write
    pop

    push exclamation_point
    write
    pop

    halt
