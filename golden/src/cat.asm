.code
    loop:
        jump loop

    end:
        halt

    on_input:
        read INPUT
        duplicate

        push 0
        compare

        jeq end

        save OUTPUT

        return
