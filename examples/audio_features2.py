# shows acoustic features for tracks for the given artist

from __future__ import print_function    # (at top of module)
from spotipy.oauth2 import SpotifyClientCredentials
import json
import spotipy
import time
import sys

460V2cUWccVmYeTd4TLabO,01N7pbYH5f9TpLxmqosmUe,2Rrkgr8Kd0XGNbilwip6r8,3iJacHlEpRhG8CIStLXYbs,3D0stCwnqbPRkbXnUp28PR,5f1E93e9HPSRs24QM4WZsa,3BxHcg8PCUVK3m7gESNFg9,6chhc8QbIYUW9eROLwzTt7,6cIqoP7oV1H5NjmX4rxLie,4u10VvC4AV75eQ0boApzkq,%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C5nsikUg2MZkmb1nxvcFl5J%2C5PukeF41F4XNCyltPrjtfO%2C2JCpgkECOJyD7yUokQZDrs%2C7dwXipvdDxipgRu47xH98K%2C4IK53QTieazWuWUYm5fkP8%2C5dcQ2uEhO0hXdvcWFQShV9%2C3KpmsYSzgeummZ4leRtjbM%2C3kFuIYz4jYu1Wgq5HuFnid%2C5uEsEDcw8D30AmksKuavMh%2C6HjVlvOUu8zaLlNLCAELrd%2C4zrJmEMmQKxC5desjEgadB%2C41wBEIqFyttEGmbQcRHu13%2C5ATVpeENGTukudcWso7WeE%2C6qs7nmfAvHTIIpFLFsDTVc%2C4KSx0OmRJpT8EvTNnzZw2V%2C7eyhxafr2Q09JcqkSRSkOX%2C6JP7TRXXgTcuoDyotNR5Bu%2C2LwXZozk3SAWgqunHZq5pV%2C1lE88zONI0LR9hAi14F9tJ%2C3VxJ96B20xnFfxCrBCgjh0%2C2kEDlDyDht2OnN3eUD6AKy%2C59jyWHNXkL6R2rWsz2hnuH%2C2Brivg4Hjx6nqmUXJCkrDQ%2C1C0mAIhKJ5luyb2TNE7n7E%2C0y2nkKDa3VMaUx9rvzERJv%2C3AJK9D8d5AMxx0cgLbsL5W

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
sp.trace=True

if len(sys.argv) > 1:
    artist_name = ' '.join(sys.argv[1:])
    results = sp.search(q=artist_name, limit=50)
    tids = []
    for i, t in enumerate(results['tracks']['items']):
        print(' ', i, t['name'])
        tids.append(t['uri'])

    print(tids)

    start = time.time()
    features = sp.audio_features(tids)
    delta = time.time() - start
    print ("features", features)
    print(json.dumps(features, indent=4))

    print ("features retrieved in %.2f seconds" % (delta,))
