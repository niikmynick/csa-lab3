.data
    i 3
    limit 1000
    sum 0

.code
    loop:
    # actual number to check
        push i

    # check if the number below limit
        push limit
        compare

    # break loop3 and start loop5
        jeq finish


    # check if i is divisible by 3
        push i

    # calculate i // 3
        push i
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
        push i

        push i
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
        push sum
        push i
        add
        save sum

    # remove sum from stack
        pop

    # increment the i value (get next number)
        push i
        inc
        save i

    # remove i from stack
        pop

    # continue
        jump loop


    bad:
        push i
        inc
        save i

        pop

        jump loop


    finish:
        push sum
        write

        halt
