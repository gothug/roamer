import sys
import pprint
from optparse import OptionParser

import webagent
import dude

parser = OptionParser()
parser.add_option("-d", "--debug", action="store_true", dest="debug",
    help="enable debug mode")
(options, args) = parser.parse_args()

def p(thing):
    pprint.pprint(thing)

if __name__ == '__main__':
    wa = webagent.WebAgent()

    dude = dude.Dude(webagent = wa, debug_mode = options.debug)

    wa.login_to_soundcloud()

    account_followers_url = 'https://soundcloud.com/rtyke/followers'
    followers = dude.get_followers(account_followers_url)
    p(followers)

    account_url = 'https://soundcloud.com/rtyke'
    tracks = dude.get_tracks(account_url)
    p(tracks)

    tracks_info = dude.process_tracks(tracks)
    p(tracks_info)

    denovali_url = 'https://soundcloud.com/denovali/followers'
    users = dude.follow_and_like_and_play(denovali_url, 1)
    p(users)
