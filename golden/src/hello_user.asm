.data
    name_request "What is your name?\n"
    welcome_beginning "Hello, "
    exclamation_point "!\n"
    name_ptr 1

.code
    read EXTRA
    save name_ptr

    ask:
        push name_request
        jump loop

    await_name:
        jump await_name

    hello:
        push welcome_beginning
        jump loop2

    name:
        read EXTRA
        duplicate
        jump loop3

    excl:
        push exclamation_point
        jump loop4

    end:
        halt

    loop:
        duplicate
        read

        duplicate
        push 0
        compare
        jeq await_name

        save OUTPUT
        inc

        jump loop

    loop2:
        duplicate
        read

        duplicate
        push 0
        compare
        jeq name

        save OUTPUT
        inc

        jump loop2

    loop3:
        duplicate
        read

        duplicate
        push 0
        compare
        jeq excl

        save OUTPUT
        inc

        jump loop3


    loop4:
        duplicate
        read

        duplicate
        push 0
        compare
        jeq end

        save OUTPUT
        inc

        jump loop4

    on_input:
        read INPUT
        duplicate

        read name_ptr
        save

        push 0
        compare

        jeq hello

        read name_ptr
        inc
        save name_ptr

        return
