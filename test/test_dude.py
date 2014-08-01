import unittest
import pprint
import sys
import pyclbr
import inspect

from roamer import dude
from roamer import util
from roamer.mock.webagent import webagent as mock_webagent
from roamer.mock.webagent import page
from roamer.mock.webagent import element

class BasicDudeTest(unittest.TestCase):

    def setUp(self):
        self.denovali_page_url = 'http://denovali_fake_url'

        wa = mock_webagent.WebAgent()

        # Denovali followers page
        el1 = element.Element(
            {'href': 'https://soundcloud.com/mumustudio',
             'text': 'J Ferley Cancino\n133 followers\n133',
        })

        el2 = element.Element(
            {'href': 'https://soundcloud.com/cody34',
             'text': 'RobertHelbig\n32 followers\n32',
        })

        el3 = element.Element(
            {'href': 'https://soundcloud.com/sasha-raven',
             'text': 'Sasha\n40 followers\n40',
        })

        el4 = element.Element(
            {'href': 'https://soundcloud.com/djmycro',
             'text': 'Alexander\n4000 followers\n4000',
        })

        el5 = element.Element(
            {'href': 'https://soundcloud.com/lovecraft65',
             'text': 'Sam\n77 followers\n77',
        })

        el6 = element.Element(
            {'href': 'https://soundcloud.com/nulix',
             'text': 'Sam\n7 followers\n7',
        })

        el7 = element.Element(
            {'href': 'https://soundcloud.com/gus-menezes',
             'text': '-Shinkiro-\n4 followers\n4',
        })

        denovali_followers_page = page.Page()
        denovali_followers_page.add_element('users_badge', el1)
        denovali_followers_page.add_element('users_badge', el2)
        denovali_followers_page.add_element('users_badge', el3)
        denovali_followers_page.add_element('users_badge', el4)
        denovali_followers_page.add_element('users_badge', el5)
        denovali_followers_page.add_element('users_badge', el6)
        denovali_followers_page.add_element('users_badge', el7)

        denovali_followers_page.add_element('follower_number_on_avatar', el1)
        denovali_followers_page.add_element('follower_number_on_avatar', el2)
        denovali_followers_page.add_element('follower_number_on_avatar', el3)
        denovali_followers_page.add_element('follower_number_on_avatar', el4)
        denovali_followers_page.add_element('follower_number_on_avatar', el5)
        denovali_followers_page.add_element('follower_number_on_avatar', el7)

        wa.add_page_for_url(self.denovali_page_url, denovali_followers_page)

        # user pages

        # user1
        user1_page = page.Page()
        user1_page.add_element('follow_button',
            element.Element({'text': 'Follow'}))
        user1_page.add_element('tracks_in_playlist', element.Element())
        user1_page.add_element('artist_name_in_playlist',
            element.Element({'href': 'https://soundcloud.com/mumustudio'}))
        user1_page.add_element('play_button', element.Element())
        user1_page.add_element('like_button', element.Element())
        wa.add_page_for_url('https://soundcloud.com/mumustudio', user1_page)

        # user2 - already following him
        user2_page = page.Page()
        user2_page.add_element('follow_button',
            element.Element({'text': 'Following'}))
        user2_page.add_element('tracks_in_playlist', element.Element())
        user2_page.add_element('artist_name_in_playlist',
            element.Element({'href': 'https://soundcloud.com/cody34'}))
        wa.add_page_for_url('https://soundcloud.com/cody34', user2_page)

        # user3 - blank user
        user3_page = page.Page()
        user3_page.add_element('follow_button',
            element.Element({'text': 'Follow'}))
        user3_page.add_element('artist_name_in_playlist',
            element.Element({'href': 'https://soundcloud.com/sasha-raven'}))
        wa.add_page_for_url('https://soundcloud.com/sasha-raven', user3_page)

        # user4 - spammer
        user4_page = page.Page()
        user4_page.add_element('follow_button',
            element.Element({'text': 'Follow'}))
        user4_page.add_element('tracks_in_playlist', element.Element())
        user4_page.add_element('artist_name_in_playlist',
            element.Element({'href': 'https://soundcloud.com/djmycro'}))
        user4_page.add_element('sidebar_header',
            element.Element({'text': '4000 following'}))
        wa.add_page_for_url('https://soundcloud.com/djmycro', user4_page)

        # user5 - has one my like
        user5_page = page.Page()
        user5_page.add_element('follow_button',
            element.Element({'text': 'Follow'}))
        user5_page.add_element('tracks_in_playlist', element.Element())
        user5_page.add_element('like', element.Element({'title': 'Like me'}))
        user5_page.add_element('like', element.Element({'title': 'Liked'}))
        wa.add_page_for_url('https://soundcloud.com/lovecraft65', user5_page)

        # user6 - reposter
        user6_page = page.Page()
        user6_page.add_element('follow_button',
            element.Element({'text': 'Follow'}))
        user6_page.add_element('tracks_in_playlist', element.Element())
        user6_page.add_element('artist_name_in_playlist', element.Element({'href': 'http://music.com'}))
        wa.add_page_for_url('https://soundcloud.com/nulix', user6_page)

        self.dude = dude.Dude(webagent = wa)

    def testFollowAndLikeAndPlay(self):
        users = self.dude.follow_and_like_and_play(self.denovali_page_url, 20)

        followed_by_me = [ 'https://soundcloud.com/mumustudio',
                           'https://soundcloud.com/cody34']
        self.assertEqual(set(users['followed_by_me']), set(followed_by_me),
            'Followed by me users are found correctly')

        ever_liked_by_me = [ 'https://soundcloud.com/lovecraft65' ]
        self.assertEqual(set(users['ever_liked_by_me']), set(ever_liked_by_me),
            'Ever liked by me users are found correctly')

        spammer = [ 'https://soundcloud.com/djmycro' ]
        self.assertEqual(set(users['spammer']), set(spammer),
            'Spammer users are found correctly')

        blank = [ 'https://soundcloud.com/sasha-raven' ]
        self.assertEqual(set(users['blank']), set(blank),
            'Blank users are found correctly')

        util.debug_log_json(users)

if __name__ == '__main__':
    unittest.main()
