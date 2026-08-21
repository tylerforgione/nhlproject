from nhlpy import NHLClient

client = NHLClient()

print(client.game_center.boxscore(1917020001))
