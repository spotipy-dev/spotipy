## Contribuir

Si le gustaría contribuir a Spotipy, siga los próximos pasos:

### Exporte las variables de entorno necesarias

```bash
export SPOTIPY_CLIENT_ID=client_id_aqui
export SPOTIPY_CLIENT_SECRET=client_secret_aqui
export SPOTIPY_CLIENT_USERNAME=client_username_aqui # De hecho esto es un ID, no el
                                                    # nombre de usuario de Spotify

export SPOTIPY_REDIRECT_URI=http://localhost:8080 # Asegúrese de que el url esté
                                                  # establecido dentro de la aplicación
                                                  # que usted creo para recibir su ID y SECRET
```

### Cree un entorno virtual, instale dependencias, corra pruebas:

```bash
$ virtualenv --python=python3.7 env
(env) $ pip install --user -e .
(env) $ python -m unittest discover -v tests
```

### Basura de codigo informático

Para automáticamente arreglar el estilo del código informático:

    pip install autopep8
    autopep8 --in-place --aggressive --recursive .

Para verificar el estilo del código informático:

    pip install flake8
    flake8 .

Para asegurarse que las listas de importe esten almacenadas correctamente:

    pip install isort
    isort . -c -v

### Publicación (por el mantenedor)

 - Incrementar versión en setup.py
 - Incrementar y poner fecha en changelog
 - Añadir a changelog:

       ## Inedito

       // Añadir sus cambios aqui, despues borrar esta linea

 - Cometer cambios
 - Empaquetar a pypi:

       python setup.py sdist bdist_wheel
       python3 setup.py sdist bdist_wheel
       twine check dist/*
       twine upload --repository-url https://upload.pypi.org/legacy/ --skip-existing dist/*.(whl|gz|zip)~dist/*linux*.whl

 - Crear un lanzamiento de github https://github.com/plamere/spotipy/releases con el contenido de changelog
   para la version, al igual que una breve descripcion de la adición principal

 - Verifique que el documento utilize el más reciente https://readthedocs.org/projects/spotipy/
### Changelog

No se olvide de añadir una breve descripcion de sus cambios en [CHANGELOG](CHANGELOG.md)
