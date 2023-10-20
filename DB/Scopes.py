class Scopes:
    """
    # Class Scopes
    ### Version: 0.0.1
    #### Author: [AlfredSimpson](https://github.com/AlfredSimpson)
    #### Created: 2023-10-14
    #### Updated: 2023-10-14
    #### Status: Complete

    ## Definition
    Scopes holds read and write privileges for the Spotify API, and must be passed to the Spotify API when making requests. There are no methods. Simply call the objecta and get the scope you need.

    The following scopes are available:

    ## Attributes

    ### Read Privileges
    - :attr:`Scopes.read_collab_playlist`: Include collaborative playlists when requesting a user's playlists
    - :attr:`Scopes.read_currently_playing`: Read access to a user currently playing content
    - :attr:`Scopes.read_email`: Read access to user's email address
    - :attr:`Scopes.read_following`: Read access to the list of artists and other users that the user follows
    - :attr:`Scopes.read_library`: Read access to a user's library
    - :attr:`Scopes.read_playback_state`: Read access to  user player state
    - :attr:`Scopes.read_private_playlists`: Read access to user's private playlists
    - :attr:`Scopes.read_recent`: Read access to a user's recently played tracks
    - :attr:`Scopes.read_subscription`: Read access to user's subscription details
    - :attr:`Scopes.read_top`: Read access to a user's top artists and tracks

    ### Write Privileges
    - :attr:`Scopes.upload_img`: Upload images to Spotify
    - :attr:`Scopes.mod_following`: Write/delete access to the list of artists and other users that the user follows
    - :attr:`Scopes.mod_library`: Write/delete access to a user's library
    - :attr:`Scopes.mod_playback_state`: Write access to  user player state
    - :attr:`Scopes.mod_priv_playlist`: Write access to a user's private playlists
    - :attr:`Scopes.mod_pub_playlist`: Write access to a user's public playlists
    - :attr:`Scopes.mod_user_entitlements`: Modify entitlements of a Spotify user
    - :attr:`Scopes.mod_user_soa`: Link a partner user account to a Spotify user account
    - :attr:`Scopes.mod_user_soa_unlink`: Unlink a partner user account from a Spotify user account
    """

    # Write privileges
    upload_img = "ugc-image-upload"
    mod_following = "user-follow-modify"
    mod_library = "user-library-modify"
    mod_playback_state = "user-modify-playback-state"
    mod_priv_playlist = "playlist-modify-private"
    mod_pub_playlist = "playlist-modify-public"
    mod_user_entitlements = "user-manage-entitlements"
    mod_user_soa = "user-soa-link"
    mod_user_soa_unlink = "user-soa-unlink"
    # Read privileges
    read_collab_playlist = "playlist-read-collaborative"
    read_currently_playing = "user-read-currently-playing"
    read_email = "user-read-email"
    read_following = "user-follow-read"
    read_library = "user-library-read"
    read_playback_state = "user-read-playback-state"
    read_private_playlists = "playlist-read-private"
    read_recent = "user-read-recently-played"
    read_subscription = "user-read-private"  # private subscription details
    read_top = "user-top-read"

    def __init__(self):
        # Write privileges
        self.upload_img = "ugc-image-upload"
        self.mod_following = "user-follow-modify"
        self.mod_library = "user-library-modify"
        self.mod_playback_state = "user-modify-playback-state"
        self.mod_priv_playlist = "playlist-modify-private"
        self.mod_pub_playlist = "playlist-modify-public"
        self.mod_user_entitlements = "user-manage-entitlements"
        self.mod_user_soa = "user-soa-link"
        self.mod_user_soa_unlink = "user-soa-unlink"
        # Read privileges
        self.read_collab_playlist = "playlist-read-collaborative"
        self.read_currently_playing = "user-read-currently-playing"
        self.read_email = "user-read-email"
        self.read_following = "user-follow-read"
        self.read_library = "user-library-read"
        self.read_playback_state = "user-read-playback-state"
        self.read_private_playlists = "playlist-read-private"
        self.read_recent = "user-read-recently-played"
        self.read_subscription = "user-read-private"  # private subscription details
        self.read_top = "user-top-read"

    def get_all_scopes():
        pass
