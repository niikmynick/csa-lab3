.data
    text "Hello, World!\n"

.code
    push text

    loop:
        duplicate
        read
        duplicate

        push 0
        compare
        jeq end

        jump print

    print:
        save OUTPUT
        inc
        jump loop

    end:
        halt
