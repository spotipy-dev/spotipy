class FreshObject:
    """Base Object for Spotipy Objects
    All spotify objects will inherit this

    """

    def __init__(self, client):
        self.client = client

    def __str__(self) -> str:
        try:
            return self.name
        except Exception as e:
            raise e

    def __repr__(self) -> str:
        """
        Example
        -------
        ObjectType
            Name: objectName
            ID: objectID
            URI: objectURI
        """
        try:
            return(f"{self.__class__}\n\tName: {self.name}\n\tID: {self.id}\n\tURI: {self.uri}")
        except Exception as e:
            raise e

    def __eq__(self, other) -> bool:
        """Checks if the artists are the same"""
        try:
            return self.id == other.id if (other.type == other.type) else False
        except Exception as e:
            raise e

    def __ne__(self, other) -> bool:
        """Checks if they're NOT the same artist"""
        try:
            return not self.__eq__(other)
        except Exception as e:
            raise e

class User(FreshObject):
    """User class object
    Turns user json data into an object User

    Parameters
    ----------
    client : spotipy.Spotify
        client used for the api
    user : dict
        json data given from api

    Attributes
    ----------
    client : spotipy.Spotify
        client used for the api
    name : str
        user's display name
    id : str
        user's unique user id
    uri : stri
        user's spotify uri
    url : str
        user's spotify url
    all_urls : dict[str, str]
        all external URLs for the user
    followers : int
        user's total amount of followers
    images : list[str]
        list of image urls associated with the user
    type : str
        type of object (should always be 'user')
    """
    def __init__(self, client, user):
        """Inits User"""
        self.client = client
        self.name = user['display_name']
        self.id = user['id']
        self.uri = user['uri']
        self.url = user['external_urls']['spotify']
        self.all_urls = user['external_urls']
        self.followers = user['followers']['total']
        images = []
        for image in user['images']:
            images.append(image['url'])
        self.images = images
        self.type = user['type'] # should always be 'user'

    # add some functions like user_playlists()


class Artist(FreshObject):
    """Artist class object
    Turns artist json data into an object Artist

    Parameters
    ----------
    client : spotipy.Spotify
        client used for the api
    artist : dict
        json data given from api

    Attributes
    ----------
        client : spotipy.Spotify
            client used for the api
        name : str
            artist's username on spotify
        id : str
            artist's unique id
        uri : str
            artist's spotify uri
        url : string
            artist's spotify url
        all_urls : dict[str, str]
            all external URLs for the artist
        followers : int
            artist's total amount of followers
        genres : list[str]
            list of genre's associated with the artist
        popularity : int
            artist's popularity score
        images : list[str]
            list of image urls associated with the artist
        type : str
            type of object (should always be 'artist')

    """
    def __init__(self, client, artist: dict):
        """Inits Artist"""
        self.client = client
        self.name = artist['name']
        self.id = artist['id']
        self.uri = artist['uri']
        self.url = artist['external_urls']['spotify']
        self.all_urls = artist['external_urls']
        self.followers = artist['followers']['total']
        self.genres = artist['genres']
        self.popularity = artist['popularity']
        images = []
        for image in artist['images']:
            images.append(image['url'])
        self.images = images
        self.type = artist['type'] # should always be 'artist'
        super().__init__(client)

    # add some methods like artist_albums()


class Album(FreshObject):
    """Album class object
    Turns album json data into an object Album

    Parameters
    ----------
    client : spotipy.Spotify
        client used for the api
    album : dict
        json data given from api

    Attributes
    ----------
        client : spotipy.Spotify
            client used for the api
        name : str
            artist's username on spotify
        id : str
            artist's unique id
        uri : str
            artist's spotify uri
        url : string
            artist's spotify url
        all_urls : dict[str, str]
            all external URLs for the artist
        album_type : str
            the type of album
        artists : list[dict[str, str]]
            lists of artists (name, uri, id)
        release_date : str
            date of release (year-month-day)
        total_tracks : int
            total amount of tracks on the album
        images : list[str]
            list of image urls associated with the artist
        type : str
            type of object (should always be 'artist')

    """
    def __init__(self, client, album):
        """Inits Album"""
        self.client = client
        self.name = album['name']
        self.id = album['id']
        self.uri = album['uri']
        self.url = album['external_urls']['spotify']
        self.all_urls = album['external_urls']
        self.album_type = album['album_type']
        artists = album['artists']
        all_artists = []
        for artist in artists:
            all_artists.append({
                "name": artist['name'],
                "uri": artist['uri'],
                "id": artist['id'],
            })
        self.artists = all_artists
        self.release_date = album['release_date']
        self.total_tracks = album['total_tracks']
        images = []
        for image in album['images']:
            images.append(image['url'])
        self.images = images
        self.type = album['type'] # should always be 'album'
        super().__init__(client)

    def __len__(self):
        return self.total_tracks

    # add some methods like get_artists() and get_tracks()


class Track(FreshObject):
    """Track class object
    Turns album json data into an object Album

    Parameters
    ----------
    client : spotipy.Spotify
        client used for the api
    track : dict
        json data given from api

    Attributes
    ----------
        client : spotipy.Spotify
            client used for the api
        name : str
            artist's username on spotify
        id : str
            artist's unique id
        uri : str
            artist's spotify uri
        url : string
            artist's spotify url
        all_urls : dict[str, str]
            all external URLs for the artist
        popularity : int
            artist's popularity score
        track_number : int
            tracks position on the album
        explicit : bool
            is the track explicit
        duration : int
            duration of the track in ms
        is_local : bool
            is the track local
        album : dict[str, str]
            name, id, and uri of the album
        artists : list[dict[str, str]]
            list of artists on the track (name, id, uri)
        type : str
            type of object (should always be 'artist')

    """
    def __init__(self, client, track):
        """Inits Track"""
        self.client = client
        self.name = track['name']
        self.id = track['id']
        self.uri = track['uri']
        self.url = track['external_urls']['spotify']
        self.all_urls = track['external_urls']
        self.popularity = track['popularity']
        self.track_number = track['track_number']
        self.explicit = track['explicit']
        self.duration = track['duration_ms']
        self.is_local = track['is_local']
        album = track['album']
        self.album = {
            "name": album['name'],
            "uri": album['uri'],
            "id": album['id'],
        }
        artists = track['artists']
        all_artists = []
        for artist in artists:
            all_artists.append({
                "name": artist['name'],
                "uri": artist['uri'],
                "id": artist['id'],
            })
        self.artists = all_artists
        self.type = track['type'] # should always be 'track'
        super().__init__(client)

    def __len__(self):
        """
        Returns
        -------
        self.duration : int
        """
        return self.duration
