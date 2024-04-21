.data
    name_request "What is your name?\n"
    welcome_beginning "Hello, "
    exclamation_point "!\n"

.code
    push name_request
    write

    read

    push welcome_beginning
    write

    write

    push exclamation_point
    write

    halt
