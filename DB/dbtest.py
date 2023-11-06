<<<<<<< HEAD
import LongDB
import spotipy
import LongSpotWorker


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


def test_LongSpotWorker():
    data = LongSpotWorker.LongDB("localhost", "example", "exampl3!", "tester")

    check_spotuser = data.add_user(
        table="spotusers", spot_username="spot_username"
    )
    print(check_spotuser)

def runSpotTest():
    data = LongSpotWorker.LongDB("localhost", "example", "exampl3!", "tester")
    user = data.auth_user(table="spotusers", spot_username="spot_username")
    return user
=======
def test_LongDB(p1, p2):
    result = p1 + p2
    print(result)


def runTest():
    p1 = 5
    p2 = 10
    return test_LongDB(p1, p2)


print(runTest())
>>>>>>> b94acf3cc51404f8735aaff54c27d259130057c1
