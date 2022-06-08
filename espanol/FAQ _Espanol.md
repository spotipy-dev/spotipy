## Preguntas Frecuentes

### Existe alguna manera de recibir informacion adicional del API?

Spotipy solamente recibe información que se encuentra documentada en el API oficial de [Spotify](https://developer.spotify.com/documentation/web-api/reference/)

### ¿Como utilizo Spotipy en un API?

Ver [este ejemplo en la app de Flask](https://github.com/plamere/spotipy/blob/master/examples/app.py)

### ¿Como puedo almacenar fichas en una base de datos, y no en el sistema de archivos?

Ver https://spotipy.readthedocs.io/en/latest/#customized-token-caching

### Usuario Incorrecto

Error:

 - Obtiene `You cannot create a playlist for another user`
 - Obtiene `You cannot remove tracks from a playlist you don't own`

Solución:

 - Verifique que esté registrado con la cuenta correcta en https://spotify.com
 - Remueva su ficha actual: `rm .cache-{userid}`
 - Solicite una nueva ficha, añadiendo `show_dialog=True` a `spotipy.Spotify(auth_manager=SpotifyOAuth(show_dialog=True))`
 - Verifique que `spotipy.me()` muestre la ID del usuario correcto

### ¿Por qué recibo 401 Unauthorized?

Error:

    spotipy.exceptions.SpotifyException: http status: 401, code:-1 - https://api.spotify.com/v1/
    Unauthorized.

Solución:

- Probablemente ha perdido un ámbito solicitando el resultado, revise
https://developer.spotify.com/web-api/using-scopes/

### Búsqueda (search) no encuentra algunas canciónes

Problema: puede ver una canción en la app de Spotify, pero buscandola usando el API no se encuentra.

Solución: por defecto, el método de búsqueda `search("abba")` solo funciona en el sector estadounidense.
Para utilizar el método de búsqueda en su país actual, el [código de país](https://es.wikipedia.org/wiki/ISO_3166-1_alfa-2)
debe de ser especificado. Por ejemplo: `search("abba", market="MX")`, donde 'MX' es el codigo de Mexico.

### ¿Como obtengo autorización en un entorno sin navegador de internet?

Si no se puede abrir un navegador de internet, establezca `open_browser=False` durante el proceso de instanciar
SpotifyOAuth o SpotifyPKCE. Se le pedira que abra la autorización del URI manualmente

Ver [ejemplo sin navegador de internet](https://github.com/plamere/spotipy/blob/master/examples/headless.py).
