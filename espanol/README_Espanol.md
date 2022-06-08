# Spotipy
##### Un archivo ligero para el API de Spotify

![Pruebas](https://github.com/plamere/spotipy/workflows/Tests/badge.svg?branch=master) [![Documentation Status](https://readthedocs.org/projects/spotipy/badge/?version=latest)](https://spotipy.readthedocs.io/en/latest/?badge=latest)

## Documentación

La documentacion completa de Spotify puede ser encontrada en [Documentación de Spotipy](http://spotipy.readthedocs.org/).

## Instalación

```bash
pip install spotipy
```

o actualizar una instalacion existente

```bash
pip install spotipy --upgrade
```

## Comienzo Rápido

Un set completo de ejemplos puede ser encontrado en la [documentacion](http://spotipy.readthedocs.org/) y en el [directorio de ejemplos de Spotipy](https://github.com/plamere/spotipy/tree/master/examples).

Para comenzar, se necesita instalar Spotipy y crear un app en https://developers.spotify.com/.
Añada su nueva ID y SECRET a su entorno:

### Sin autenticación de usuario

```python
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="SU_APP_CLIENT_ID",
                                                           client_secret="SU_APP_CLIENT_SECRET"))

results = sp.search(q='weezer', limit=20)
for idx, track in enumerate(results['tracks']['items']):
    print(idx, track['name'])
```

### Con autenticación de usuario

```python
import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="SU_APP_CLIENT_ID",
                                               client_secret="SU_APP_CLIENT_SECRET",
                                               redirect_uri="SU_APP_REDIRECT_URI",
                                               scope="user-library-read"))

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])
```

## Reportar Problemas

Para preguntas comunes, favor de checar [FAQ](FAQ.md).

Puede hacer preguntas acerca de Spotipy en
[Stack Overflow](http://stackoverflow.com/questions/ask).
No se olvide de añadir la etiqueta *Spotipy*, al igual de cualquier otras etiquetas pertinentes.

Si tiene sugerencias, encontro errores u otros problemas especificos a este archivo de Spotipy,
presentelos [aqui](https://github.com/plamere/spotipy/issues).
O simplemente mande un pull request.
