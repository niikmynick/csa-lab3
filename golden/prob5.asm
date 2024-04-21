.data
    number 1
    i 2
    j 2
    max 20

.code
    i_loop:
        push i
        push max
        compare
        jla finish

        push number

        push number
        push i
        div

        push i
        mul

        sub

        push 0
        compare

        jne j_loop
        jump i_next

    j_loop:
        push j
        push i
        compare

        jla i_next

        push number
        push j
        mul

        push number
        push j
        mul
        push i
        div

        push i
        mul

        sub

        push 0
        compare

        jeq number_update

        jump j_next

    number_update:
        push number
        push j
        mul
        save number

        jump i_next

    i_next:
        push i
        inc
        save i
        pop

        push 2
        save j
        pop

        jump i_loop

    j_next:
        push j
        inc
        save j
        pop

        jump j_loop


    finish:
        push number
        write

        halt
