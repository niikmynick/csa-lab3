.data
    number 1
    i 2
    j 2
    max 20

.code
    i_loop:
        read i
        read max
        compare
        jla finish

        read number

        read number
        read i
        div

        read i
        mul

        sub

        push 0
        compare

        jne j_loop
        jump i_next

    j_loop:
        read j
        read i
        compare

        jla i_next

        read number
        read j
        mul

        read number
        read j
        mul
        read i
        div

        read i
        mul

        sub

        push 0
        compare

        jeq number_update

        jump j_next

    number_update:
        read number
        read j
        mul
        save number

        jump i_next

    i_next:
        read i
        inc
        save i

        push 2
        save j

        jump i_loop

    j_next:
        read j
        inc
        save j

        jump j_loop


    finish:
        push -1
        read number
        jump prepare_num

    # i - (i // 3) * 3
    # i 3 i 3 // * -
    prepare_num:
        duplicate
        push 10
        read number
        push 10
        div
        mul
        sub

        push 48
        add
        swap

        push 10
        div
        duplicate
        SAVE number

        duplicate
        inc
        push 1
        compare
        jeq then

        jump prepare_num

    then:
        pop
        jump print_num

    print_num:
        duplicate
        push -1
        compare
        jeq end

        SAVE OUTPUT
        jump print_num

    end:
        halt
