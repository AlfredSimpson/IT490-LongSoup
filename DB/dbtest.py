import LongDB


def test_LongDB():
    db = LongDB.LongDB("localhost", "example", "exampl3!", "tester")
    # assert db.mydb is not None
    # assert db.mycursor is not None

    # answer = db.validate_user("test", "test")
    # print(answer)

    tryadding = db.add_user(
        table="users", useremail="test@example.com", password="test"
    )
    print(tryadding)


def runTest():
    db = LongDB.LongDB("localhost", "example", "exampl3!", "tester")
    ans = db.auth_user(table="users", useremail="test@example.com", password="test")
    return ans
