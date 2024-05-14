.data
    i 3
    limit 1000
    sum 0

.code
    loop:
    # actual number to check
        read i

    # check if the number below limit
        read limit
        compare

    # break loop3 and start loop5
        jeq finish


    # check if i is divisible by 3
        read i
        duplicate

    # calculate i // 3
        push 3
        div

    # (i // 3) * 3
        push 3
        mul

    # i - (i // 3) * 3
        sub

    # compare remainder of division with 0
        push 0
        compare

    # save if equals
        jeq good


    # also with 5
        read i
        duplicate

        push 5
        div

        push 5
        mul

        sub

        push 0
        compare

        jeq good

        jump bad


    good:
    # sum += i
        read sum
        read i
        add
        save sum

    # increment the i value (get next number)
        read i
        inc
        save i

    # continue
        jump loop


    bad:
        read i
        inc
        save i

        jump loop


    finish:
        push -1
        read sum
        jump prepare_num

    # i - (i // 3) * 3
    # i 3 i 3 // * -
    prepare_num:
        duplicate
        push 10
        read sum
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
        SAVE sum

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
