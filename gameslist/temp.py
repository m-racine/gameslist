# boston cream pie
# boston: cream pie
# boston: cream: pie
# boston cream: pie
# boston - cream pie
# boston - cream - pie
# boston cream - pie
# boston: cream - pie
# boston - cream: pie
FILLS = [' - ',': ']
def gen_splits(input_array):
    array = []
    for x in range(1, len(input_array)):
        for fill in FILLS:
            array.append(" ".join(input_array[0:x])+fill+" ".join(input_array[x:]))
    return array

test = "boston cream pie toast"
test_array = test.split(' ')
array = []
deep_array = []
array = gen_splits(test_array)
for i in range(0, len(FILLS)):
    for x in range(1, len(test_array)):
        front_array = gen_splits(test_array[0:x])
        print front_array
        sub_array = test_array[x:]
        print sub_array
        for arr in front_array:
            for temp in gen_splits(sub_array):
                #print array[i]
                deep_array.append(arr + FILLS[i] + temp)
            print "deep"
            print deep_array
        print "end for"

print len(array+deep_array)
print array+deep_array