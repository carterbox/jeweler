from jeweler.bracelet import bracelet_fc

def test_bracelet_fc():

    help(bracelet_fc)
    result = bracelet_fc(6, 3, [1, 2, 3])
    print(type(result))
    for i in result:
        print(i)
    print()
    del result[2:]
    for i in result:
        print(i)


if __name__ == "__main__":
    test_bracelet_fc()
