# All methods related to a user's taste and preferences.


class Taste:
    """
    def __init__(self, user):
        self.user = user

    """

    # Getters
    # Getters get info about their activities and interactions with music/communities/etc.
    #These group of getters relate to information about Spotify users
    def getUsersTopProfile(user, spotify_username):
        #return topuser_profile
        pass

    def getTopItem(user, spotify_username, top_item):
        #return topuser_item
        pass
    
    def getUserProfile(user, spotify_username):
        #return user_profile
        pass

    def getFollowedArtist(user, spotify_username, artist_name):
        #return followed_artist
        pass

    def getIfFollowedArtist(user, spotify_username, artist_name):
        #return if_followed_artist
        pass

    def getIfFollowedPlaylist(user, spotify_username, artist_name, playlist_name):
        #return if_followed_playlist
        pass


    #This group of getters relates to tracks on Spotify
    def getSeveralTracks(user, spotify_username, tracks):
        #return track_names
        pass

    def getUsersSavedTracks(user, spotify_username, spotify_username_saved_tracks):
        #return users_saved_tracks
        pass

    def getUserRecommendations(user, spotify_username, track_recommendations):
        #return user_recommendations
        pass

    def getCheckUsersTrack(user, spotify_username, check_spotify_username_tracks):
        #return check_users_track
        pass
    # Setters
    # Setters would update a user's profile with information about their taste and preferences.

    pass
