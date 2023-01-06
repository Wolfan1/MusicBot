import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

creds = SpotifyClientCredentials(client_id="", client_secret="")
creds.redirect_uri = ""

birdy_uri = 'spotify:artist:2WX2uTcsvV5OnS0inACecP'
spotify = spotipy.Spotify(client_credentials_manager=creds)

def getSongs(url: str) -> list:
  songs = []
  results = {"items": ["blank"]}
  while len(results["items"]) != 0:
    try:
      results = spotify.playlist_tracks(url, offset=len(songs))
    except Exception as exc:
      print(f"Error {str(exc)}")
      break

    for result in results["items"]:
      try:
        songs.append(result["track"]["name"] + ", " + result["track"]["artists"][0]["name"])
      except:
        pass
  return songs

if __name__ == "__main__":
  print("Trying playlist 1")
  ply = getSongs("https://open.spotify.com/playlist/5obOptE8YIa8ZY0NTG9sow?si=7b0359f5a7884136")
  print(ply)
  print(f"This had {len(ply)} songs.")
  print("")
  print("Trying playlist 2")
  ply = getSongs("https://open.spotify.com/playlist/4tRI7VO4klTyDHh5w8Y7A3?si=d3b84837d19a4ddd")
  print(ply)
  print(f"This had {len(ply)} songs.")