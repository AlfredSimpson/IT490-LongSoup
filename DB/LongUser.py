# This will be another class to keep the code clean and organized. It will serve to give more functionality to the user.


class LongUser:
    # Initialize the user
    def __init__(self, db, userid):
        # get the user info and store it as a class object
        pass

    # Getters
    def getProfile(self, userid):
        """
        getProfile is a function that gets the profile of a user.
        It requires the following parameters:
        userid: the id of the user to get the profile of
        """
        # Should return username, interests, and bio, location, f_name, l_name

        # return all table info for user

        pass

    def getGenre(self, songGenre):
        """
        get genere will function where it 
        will get the genre of said song
        """
        pass

    def getCommunity(self, userid, username, artist, song):
        """
        creates a community of users based upon
        artist and song
        """
        pass

    def getEvent(self, userid, username, zipcode, artist):
        """
        gets events related to an artist
        within the area of a zipcode
        """
        pass
    

    # Setters - what should we set for the user
    # Examples: new password, first name, last name, city, etc.
    def set_user_zip(self, userid, zipcode):
        """
        Adds the user's zip code
        """
        #return user_zipcode
        pass
    
    def set_user_songlist(self, songs):
        """
        Adds the user's songlist/playlist
        """
        #return user_songlist
        pass

    def set_user_fname(self, userid, fname):
        """
        Adds the user's first name in the DB
        """
        #return user_fname
        pass

    def set_user_lname(self, userid, lname):
        """
        Adds the user's last name in the DB
        """
        #return user_lname
        pass

    def set_user_username(self, userid, username):
        """
        Adds the user's username to the DB
        """
        #return user_username
        pass

    def set_user_bio(self, userid, bio):
        #return user_bio
        pass

    def set_user_liked_songs(self, userid, songs, likes):
        #return user_likes
        pass

    def set_user_dislike_songs(self, userid, songs, dislikes):
        #return user_dislikes
        pass

    def set_song_rank(self, sRank):
        #return songRank
        pass

    def set_artist_rank(self, artRank):
        #return artistRank
        pass


    pass
