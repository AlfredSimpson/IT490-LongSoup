def test_LongDB(p1, p2):
    result = p1 + p2
    print(result)


def runTest():
    p1 = 5
    p2 = 10
    return test_LongDB(p1, p2)


print(runTest())
