import sys
from typing import Any, Generic, List, Mapping, TypeVar, overload

if sys.version_info >= (3, 8):
    from typing import Literal, TypedDict
else:
    from typing_extensions import Literal, TypedDict

_T = TypeVar("_T", covariant=True)


TokenInfo = TypedDict("Token", {
    "access_token": str,
    "token_type": str,
    "scope": str,
    "expires_in": int,
    "refresh_token": str,
    "expires_at": int
})


# Paging objects
class Page(Generic[_T], Mapping[str, Any]):
    # autopep8: off
    @overload
    def __getitem__(self, k: Literal["href"]) -> str: ...
    @overload
    def __getitem__(self, k: Literal["items"]) -> List[_T]: ...
    @overload
    def __getitem__(self, k: Literal["limit"]) -> int: ...
    @overload
    def __getitem__(self, k: Literal["next"]) -> str: ...
    @overload
    def __getitem__(self, k: Literal["offset"]) -> int: ...
    @overload
    def __getitem__(self, k: Literal["previous"]) -> str: ...
    @overload
    def __getitem__(self, k: Literal["total"]) -> int: ...

    def __getitem__(self, k: str) -> Any: ...
    # autopep8: on


class CursorPage(Generic[_T], Mapping[str, Any]):
    # autopep8: off
    @overload
    def __getitem__(self, k: Literal["cursors"]) -> "Cursor": ...
    @overload
    def __getitem__(self, k: Literal["href"]) -> str: ...
    @overload
    def __getitem__(self, k: Literal["items"]) -> List[_T]: ...
    @overload
    def __getitem__(self, k: Literal["limit"]) -> int: ...
    @overload
    def __getitem__(self, k: Literal["next"]) -> str: ...
    @overload
    def __getitem__(self, k: Literal["total"]) -> int: ...

    def __getitem__(self, k: str) -> Any: ...
    # autopep8: on


# Response objects
TracksResponse = TypedDict("TracksResponse", tracks=List["Track"])
ArtistsResponse = TypedDict("ArtistsResponse", artists=List["Artist"])
AlbumsResponse = TypedDict("AlbumsResponse", albums=List["Album"])
ShowsResponse = TypedDict("ShowsResponse", albums=List["SimplifiedShow"])
EpisodesResponse = TypedDict("EpisodesResponse", albums=List["Episode"])
SearchResponse = TypedDict("SearchResponse",
                           artists=Page["Artist"],
                           albums=Page["SimplifiedAlbum"],
                           tracks=Page["Track"],
                           playlists=Page["SimplifiedPlaylist"],
                           shows=Page["SimplifiedShow"],
                           episodes=Page["SimplifiedEpisode"],
                           )
SnapshotId = TypedDict("SnapshotId", snapshot_id=str)
FollowedArtistsResponse = TypedDict("FollowedArtistsResponse", artists=CursorPage["Artist"])
FeaturedPlaylistsResponse = TypedDict("FeaturedPlaylistsResponse",
                                      message=str,
                                      playlists=Page["SimplifiedPlaylist"],
                                      )
NewReleasesResponse = TypedDict("NewReleasesResponse",
                                message=str,
                                albums=Page["SimplifiedAlbum"],
                                )
RecommendationGenresResponse = TypedDict("RecommendationGenresResponse", genres=List[str])
DevicesResponse = TypedDict("DevicesResponse", devices=List["Device"])
AvailableMarketsResponse = TypedDict("AvailableMarketsResponse", markets=List[str])


# JSON objects
# TODO: Missing AudioAnalysisObject, not documented
# TODO: Some of these List[T] are actually Page[T], it is not well-documented and should be checked
#       one by one
# TODO: Some calls can return Episodes or Tracks, but right now they are
# only typed as returning Tracks
class _Album(TypedDict):
    # Required keys
    album_type: str
    artists: List["Artist"]
    available_markets: List[str]
    copyrights: List["Copyright"]
    external_ids: "ExternalId"
    external_urls: "ExternalUrl"
    genres: List[str]
    href: str
    id: str
    images: List["Image"]
    label: str
    name: str
    popularity: int
    release_date: str
    release_date_precision: str
    restrictions: "AlbumRestriction"
    total_tracks: int
    tracks: 'Page[SimplifiedTrack]'
    type: str
    uri: str


class Album(_Album, total=False):
    # Possibly missing keys
    ...


class _AlbumRestriction(TypedDict):
    # Required keys
    reason: str


class AlbumRestriction(_AlbumRestriction, total=False):
    # Possibly missing keys
    ...


class _Artist(TypedDict):
    # Required keys
    external_urls: "ExternalUrl"
    followers: "Followers"
    genres: List[str]
    href: str
    id: str
    images: List["Image"]
    name: str
    popularity: int
    type: str
    uri: str


class Artist(_Artist, total=False):
    # Possibly missing keys
    ...


class _AudioFeatures(TypedDict):
    # Required keys
    acousticness: float
    analysis_url: str
    danceability: float
    duration_ms: int
    energy: float
    id: str
    instrumentalness: float
    key: int
    liveness: float
    loudness: float
    mode: int
    speechiness: float
    tempo: float
    time_signature: int
    track_href: str
    type: str
    uri: str
    valence: float


class AudioFeatures(_AudioFeatures, total=False):
    # Possibly missing keys
    ...


class _Category(TypedDict):
    # Required keys
    href: str
    icons: List["Image"]
    id: str
    name: str


class Category(_Category, total=False):
    # Possibly missing keys
    ...


class _Context(TypedDict):
    # Required keys
    external_urls: "ExternalUrl"
    href: str
    type: str
    uri: str


class Context(_Context, total=False):
    # Possibly missing keys
    ...


class _Copyright(TypedDict):
    # Required keys
    text: str
    type: str


class Copyright(_Copyright, total=False):
    # Possibly missing keys
    ...


class _CurrentlyPlayingContext(TypedDict):
    # Required keys
    actions: "Disallows"
    context: "Context"
    currently_playing_type: str
    device: "Device"
    is_playing: bool
    item: "Track"
    progress_ms: int
    repeat_state: str
    shuffle_state: str
    timestamp: int


class CurrentlyPlayingContext(_CurrentlyPlayingContext, total=False):
    # Possibly missing keys
    ...


class _CurrentlyPlaying(TypedDict):
    # Required keys
    context: "Context"
    currently_playing_type: str
    is_playing: bool
    item: "Track"
    progress_ms: int
    timestamp: int


class CurrentlyPlaying(_CurrentlyPlaying, total=False):
    # Possibly missing keys
    ...


class _Cursor(TypedDict):
    # Required keys
    after: str
    before: str


class Cursor(_Cursor, total=False):
    # Possibly missing keys
    ...


class _Device(TypedDict):
    # Required keys
    id: str
    is_active: bool
    is_private_session: bool
    is_restricted: bool
    name: str
    type: str
    volume_percent: int


class Device(_Device, total=False):
    # Possibly missing keys
    ...


class _Devices(TypedDict):
    # Required keys
    devices: List["Device"]


class Devices(_Devices, total=False):
    # Possibly missing keys
    ...


class _Disallows(TypedDict):
    # Required keys
    interrupting_playback: bool
    pausing: bool
    resuming: bool
    seeking: bool
    skipping_next: bool
    skipping_prev: bool
    toggling_repeat_context: bool
    toggling_repeat_track: bool
    toggling_shuffle: bool
    transferring_playback: bool


class Disallows(_Disallows, total=False):
    # Possibly missing keys
    ...


class _Episode(TypedDict):
    # Required keys
    audio_preview_url: str
    description: str
    duration_ms: int
    explicit: bool
    external_urls: "ExternalUrl"
    href: str
    html_description: str
    id: str
    images: List["Image"]
    is_externally_hosted: bool
    is_playable: bool
    language: str
    languages: List[str]
    name: str
    release_date: str
    release_date_precision: str
    restrictions: "EpisodeRestriction"
    resume_point: "ResumePoint"
    show: "SimplifiedShow"
    type: str
    uri: str


class Episode(_Episode, total=False):
    # Possibly missing keys
    ...


class _EpisodeRestriction(TypedDict):
    # Required keys
    reason: str


class EpisodeRestriction(_EpisodeRestriction, total=False):
    # Possibly missing keys
    ...


class _Error(TypedDict):
    # Required keys
    message: str
    status: int


class Error(_Error, total=False):
    # Possibly missing keys
    ...


class _ExplicitContentSettings(TypedDict):
    # Required keys
    filter_enabled: bool
    filter_locked: bool


class ExplicitContentSettings(_ExplicitContentSettings, total=False):
    # Possibly missing keys
    ...


class _ExternalId(TypedDict):
    # Required keys
    ean: str
    isrc: str
    upc: str


class ExternalId(_ExternalId, total=False):
    # Possibly missing keys
    ...


class _ExternalUrl(TypedDict):
    # Required keys
    spotify: str


class ExternalUrl(_ExternalUrl, total=False):
    # Possibly missing keys
    ...


class _Followers(TypedDict):
    # Required keys
    href: str
    total: int


class Followers(_Followers, total=False):
    # Possibly missing keys
    ...


class _Image(TypedDict):
    # Required keys
    height: int
    url: str
    width: int


class Image(_Image, total=False):
    # Possibly missing keys
    ...


class _LinkedTrack(TypedDict):
    # Required keys
    external_urls: "ExternalUrl"
    href: str
    id: str
    type: str
    uri: str


class LinkedTrack(_LinkedTrack, total=False):
    # Possibly missing keys
    ...


class _PlayHistory(TypedDict):
    # Required keys
    context: "Context"
    played_at: str
    track: "SimplifiedTrack"


class PlayHistory(_PlayHistory, total=False):
    # Possibly missing keys
    ...


class _PlayerError(TypedDict):
    # Required keys
    message: str
    reason: str
    status: int


class PlayerError(_PlayerError, total=False):
    # Possibly missing keys
    ...


class _Playlist(TypedDict):
    # Required keys
    collaborative: bool
    description: str
    external_urls: "ExternalUrl"
    followers: "Followers"
    href: str
    id: str
    images: List["Image"]
    name: str
    owner: "PublicUser"
    public: bool
    snapshot_id: str
    tracks: List["PlaylistTrack"]
    type: str
    uri: str


class Playlist(_Playlist, total=False):
    # Possibly missing keys
    ...


class _PlaylistTrack(TypedDict):
    # Required keys
    added_at: str
    added_by: "PublicUser"
    is_local: bool
    track: "Track"


class PlaylistTrack(_PlaylistTrack, total=False):
    # Possibly missing keys
    ...


class _PlaylistTracksRef(TypedDict):
    # Required keys
    href: str
    total: int


class PlaylistTracksRef(_PlaylistTracksRef, total=False):
    # Possibly missing keys
    ...


class _PrivateUser(TypedDict):
    # Required keys
    country: str
    display_name: str
    email: str
    explicit_content: "ExplicitContentSettings"
    external_urls: "ExternalUrl"
    followers: "Followers"
    href: str
    id: str
    images: List["Image"]
    product: str
    type: str
    uri: str


class PrivateUser(_PrivateUser, total=False):
    # Possibly missing keys
    ...


class _PublicUser(TypedDict):
    # Required keys
    display_name: str
    external_urls: "ExternalUrl"
    followers: "Followers"
    href: str
    id: str
    images: List["Image"]
    type: str
    uri: str


class PublicUser(_PublicUser, total=False):
    # Possibly missing keys
    ...


class _RecommendationSeed(TypedDict):
    # Required keys
    afterFilteringSize: int
    afterRelinkingSize: int
    href: str
    id: str
    initialPoolSize: int
    type: str


class RecommendationSeed(_RecommendationSeed, total=False):
    # Possibly missing keys
    ...


class _Recommendations(TypedDict):
    # Required keys
    seeds: List["RecommendationSeed"]
    tracks: List["SimplifiedTrack"]


class Recommendations(_Recommendations, total=False):
    # Possibly missing keys
    ...


class _ResumePoint(TypedDict):
    # Required keys
    fully_played: bool
    resume_position_ms: int


class ResumePoint(_ResumePoint, total=False):
    # Possibly missing keys
    ...


class _SavedAlbum(TypedDict):
    # Required keys
    added_at: str
    album: "Album"


class SavedAlbum(_SavedAlbum, total=False):
    # Possibly missing keys
    ...


class _SavedEpisode(TypedDict):
    # Required keys
    added_at: str
    episode: "Episode"


class SavedEpisode(_SavedEpisode, total=False):
    # Possibly missing keys
    ...


class _SavedShow(TypedDict):
    # Required keys
    added_at: str
    show: "SimplifiedShow"


class SavedShow(_SavedShow, total=False):
    # Possibly missing keys
    ...


class _SavedTrack(TypedDict):
    # Required keys
    added_at: str
    track: "Track"


class SavedTrack(_SavedTrack, total=False):
    # Possibly missing keys
    ...


class _Show(TypedDict):
    # Required keys
    available_markets: List[str]
    copyrights: List["Copyright"]
    description: str
    episodes: List["SimplifiedEpisode"]
    explicit: bool
    external_urls: "ExternalUrl"
    href: str
    html_description: str
    id: str
    images: List["Image"]
    is_externally_hosted: bool
    languages: List[str]
    media_type: str
    name: str
    publisher: str
    type: str
    uri: str


class Show(_Show, total=False):
    # Possibly missing keys
    ...


class _SimplifiedAlbum(TypedDict):
    # Required keys
    album_group: str
    album_type: str
    artists: List["SimplifiedArtist"]
    available_markets: List[str]
    external_urls: "ExternalUrl"
    href: str
    id: str
    images: List["Image"]
    name: str
    release_date: str
    release_date_precision: str
    restrictions: "AlbumRestriction"
    total_tracks: int
    type: str
    uri: str


class SimplifiedAlbum(_SimplifiedAlbum, total=False):
    # Possibly missing keys
    ...


class _SimplifiedArtist(TypedDict):
    # Required keys
    external_urls: "ExternalUrl"
    href: str
    id: str
    name: str
    type: str
    uri: str


class SimplifiedArtist(_SimplifiedArtist, total=False):
    # Possibly missing keys
    ...


class _SimplifiedEpisode(TypedDict):
    # Required keys
    audio_preview_url: str
    description: str
    duration_ms: int
    explicit: bool
    external_urls: "ExternalUrl"
    href: str
    html_description: str
    id: str
    images: List["Image"]
    is_externally_hosted: bool
    is_playable: bool
    language: str
    languages: List[str]
    name: str
    release_date: str
    release_date_precision: str
    restrictions: "EpisodeRestriction"
    resume_point: "ResumePoint"
    type: str
    uri: str


class SimplifiedEpisode(_SimplifiedEpisode, total=False):
    # Possibly missing keys
    ...


class _SimplifiedPlaylist(TypedDict):
    # Required keys
    collaborative: bool
    description: str
    external_urls: "ExternalUrl"
    href: str
    id: str
    images: List["Image"]
    name: str
    owner: "PublicUser"
    public: bool
    snapshot_id: str
    tracks: "PlaylistTracksRef"
    type: str
    uri: str


class SimplifiedPlaylist(_SimplifiedPlaylist, total=False):
    # Possibly missing keys
    ...


class _SimplifiedShow(TypedDict):
    # Required keys
    available_markets: List[str]
    copyrights: List["Copyright"]
    description: str
    explicit: bool
    external_urls: "ExternalUrl"
    href: str
    html_description: str
    id: str
    images: List["Image"]
    is_externally_hosted: bool
    languages: List[str]
    media_type: str
    name: str
    publisher: str
    type: str
    uri: str


class SimplifiedShow(_SimplifiedShow, total=False):
    # Possibly missing keys
    ...


class _SimplifiedTrack(TypedDict):
    # Required keys
    artists: List["SimplifiedArtist"]
    available_markets: List[str]
    disc_number: int
    duration_ms: int
    explicit: bool
    external_urls: "ExternalUrl"
    href: str
    id: str
    is_local: bool
    is_playable: bool
    linked_from: "LinkedTrack"
    name: str
    preview_url: str
    restrictions: "TrackRestriction"
    track_number: int
    type: str
    uri: str


class SimplifiedTrack(_SimplifiedTrack, total=False):
    # Possibly missing keys
    ...


class _Track(TypedDict):
    # Required keys
    album: "SimplifiedAlbum"
    artists: List["Artist"]
    available_markets: List[str]
    disc_number: int
    duration_ms: int
    explicit: bool
    external_ids: "ExternalId"
    external_urls: "ExternalUrl"
    href: str
    id: str
    is_local: bool
    is_playable: bool
    linked_from: "LinkedTrack"
    name: str
    popularity: int
    preview_url: str
    restrictions: "TrackRestriction"
    track_number: int
    type: str
    uri: str


class Track(_Track, total=False):
    # Possibly missing keys
    ...


class _TrackRestriction(TypedDict):
    # Required keys
    reason: str


class TrackRestriction(_TrackRestriction, total=False):
    # Possibly missing keys
    ...


class _TuneableTrack(TypedDict):
    # Required keys
    acousticness: float
    danceability: float
    duration_ms: int
    energy: float
    instrumentalness: float
    key: int
    liveness: float
    loudness: float
    mode: int
    popularity: float
    speechiness: float
    tempo: float
    time_signature: int
    valence: float


class TuneableTrack(_TuneableTrack, total=False):
    # Possibly missing keys
    ...
