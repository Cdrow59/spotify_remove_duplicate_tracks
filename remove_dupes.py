import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth


# Define your Spotify client credentials
client_id = "799ad76dc8b84d36aafe716062c193f3"
client_secret = "551d48ca50a046d880c56f0cb9ac4b8e"
redirect_uri = 'http://localhost:8000/callback'

filename = (os.path.splitext(os.path.basename(__file__))[0])
cache_path = ("C:\\Users\\Clayton\\AppData\\Local\\Temp\\vscode\\" +filename+ ".cache")

# Create a Spotify client instance with authorization and custom cache
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, cache_path=cache_path, scope='playlist-modify-public'))

def remove_duplicates(playlist_id):
    # Get the playlist tracks
    playlist_tracks = []
    results = sp.playlist_tracks(playlist_id)
    playlist_tracks.extend(results['items'])

    # Iterate through additional pages if available
    while results['next']:
        results = sp.next(results)
        playlist_tracks.extend(results['items'])

    # Create a set to store unique track pairs
    unique_track_pairs = set()

    # Create a set to store unique track ids
    unique_ids = set()

    # Create a list to store duplicate track positions
    duplicate_positions = []

    # Create a list to store duplicate track ids
    duplicate_ids = []
    # Iterate over the tracks in the playlist
    for i, track in enumerate(playlist_tracks):
        track_artist = track['track']['artists'][0]['name']
        track_name = track['track']['name']
        track_pair = (track_artist, track_name)
        track_id = track['track']['id']
        id_tuple = (track_pair, track_id)
        if track_pair in unique_track_pairs:
            # Add the duplicate track position to the list
            duplicate_positions.append(i)
            duplicate_ids.append(id_tuple)
        else:
            # Add the track pair to the set
            unique_track_pairs.add(track_pair)
            unique_ids.add(id_tuple)

    # Remove the duplicate tracks from the playlist in batches
    if duplicate_positions:
        batch_size = 100  # Number of tracks to remove per request
        total_duplicates = len(duplicate_positions)
        num_batches = (total_duplicates + batch_size - 1) // batch_size  # Round up to the nearest integer

        for i in range(num_batches):
            start_idx = i * batch_size
            end_idx = (i + 1) * batch_size
            batch_positions = duplicate_positions[start_idx:end_idx]
            

            # Remove the duplicate tracks in the current batch
            batch_track_ids = [playlist_tracks[position]['track']['id'] for position in batch_positions]
            sp.playlist_remove_all_occurrences_of_items(playlist_id, batch_track_ids)

        print("Duplicates removed successfully.")
    else:
        print("No duplicates found in the playlist.")


    return playlist_tracks, unique_ids, duplicate_ids



def check_dupes(duplicate_ids, unique_ids):
# Create a new list to store non-duplicate items
    filtered_list = []

    # Iterate over the duplicate_ids list with index using enumerate
    for t, d in enumerate(duplicate_ids):
        if d in unique_ids:
            # Add non-duplicate items to the filtered list
            if d not in filtered_list:
                filtered_list.append(d)

    if filtered_list:
        # Separate the list into two lists
        pairs_list, id_list = zip(*filtered_list)

        print(pairs_list)
        print(id_list)

        tracks_to_add = id_list
    else:
        tracks_to_add = []

    return tracks_to_add









# Playlist Input
playlist_uri = input("This is remove dupes Input a Spotify Playlist URI Like this \"spotify:playlist:3z97WMRi731dCvKklIf2X6\"")
print()
playlist_id = playlist_uri.split(':')[-1]

# Say script is starting
print("Starting ...")

# Remove duplicates from the playlist

playlist_tracks, unique_ids, duplicate_ids= remove_duplicates(playlist_id)


tracks_to_add = check_dupes(duplicate_ids,unique_ids)


# Add the tracks back to the playlist

if tracks_to_add:
    batch_size = 100  # Number of tracks to add per request
    num_batches = (len(tracks_to_add) + batch_size - 1) // batch_size  # Round up to the nearest integer

    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = (i + 1) * batch_size
        batch_tracks = tracks_to_add[start_idx:end_idx]

        sp.playlist_add_items(playlist_id, batch_tracks)

    print("Duplicate tracks added back to the playlist.")
else:
    print("No duplicate tracks fadd back to the playlist.")