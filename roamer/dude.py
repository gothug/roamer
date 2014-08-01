import util
import pprint
import json
import time
import random
import logging
import os

class Dude:
    def __init__(self, webagent, debug_mode = False):
        self.debug_mode = debug_mode

        self.__init_logger()

        self.webagent = webagent

    def __init_logger(self):
        # create logger
        logger = logging.getLogger('dude_logger')
        if self.debug_mode:
            logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)

        self.logger = logger

    def get_followers(self, url):
        wa = self.webagent

        wa.open_url(url)
        wa.scroll_page_to_the_end(xpath_name = 'users_badge')
        my_followers = wa.get_elements_by_xpath_name('users_badge')

        return list(set(self.__get_hrefs(my_followers)))

    def get_tracks(self, url):
        wa = self.webagent

        wa.open_url(url)
        tracks = wa.get_elements_by_xpath_name('track_name_in_playlist')

        if len(tracks) >= 10:
            wa.scroll_page_to_the_end(xpath_name = 'tracks_in_playlist')

        tracks = wa.get_elements_by_xpath_name('track_name_in_playlist')
        track_hrefs = self.__get_hrefs(tracks)

        artists = wa.get_elements_by_xpath_name('artist_name_in_playlist')
        artist_hrefs = self.__get_hrefs(artists)

        my_tracks = util.zip_arrays_with_condition(
            lambda x: x[0] == wa.get_current_url(),
            artist_hrefs,
            track_hrefs)

        my_tracks = map(lambda x: x[1], my_tracks)

        return my_tracks

    def follow_and_like_and_play(self, followers_url, max_new_users_to_follow,
        skip_list = []):
        # aka Great Code

        users = {
            'followed_by_me'   : [],
            'blank'            : [],
            'spammer'          : [],
            'ever_liked_by_me' : [],
        }

        wa = self.webagent

        wa.open_url(followers_url)

        followers = self.__pick_significant_followers(5)

        followers = filter(lambda x: x[1] not in skip_list, followers)

        self.logger.debug('Number of followers to process: %s', len(followers))

        followed_users_counter = 0

        for follower in followers:
            if followed_users_counter == max_new_users_to_follow:
                break

            wa.open_url(follower[1])
            self.logger.debug('User link: %s', follower[1])

            current_url = wa.get_current_url()

            if self.__user_is_followed_by_me():
                users['followed_by_me'].append(current_url)
                self.logger.debug('I already follow this user..')
            elif self.__user_is_blank():
                users['blank'].append(current_url)
                self.logger.debug('Blank user..')
            elif self.__user_is_spammer():
                users['spammer'].append(current_url)
                self.logger.debug('User is a spammer..')
            else:
                wa.scroll_page_to_the_end(xpath_name = 'tracks_in_playlist')
                self.logger.debug('Scrolling tracks to the end..')

                if self.__user_was_ever_liked_by_me():
                    users['ever_liked_by_me'].append(current_url)
                    self.logger.debug('User used to be liked by me..')
                elif self.__user_is_reposter():
                    self.logger.debug('User is a reposter..')

                    self.webagent.sleep(self.webagent.timeout)

                    button = self.webagent.get_element_by_xpath_name(
                        'follow_button')
                    button.click()

                    users['followed_by_me'].append(current_url)

                    followed_users_counter = followed_users_counter + 1
                else:
                    self.logger.debug(
                        'User is really interesting to get to know him'\
                        ' deeper!')
                    artists = self.webagent.get_elements_by_xpath_name(
                        'artist_name_in_playlist')
                    artist_hrefs = self.__get_hrefs(artists)

                    play_buttons = self.webagent.get_elements_by_xpath_name(
                        'play_button')
                    like_buttons = self.webagent.get_elements_by_xpath_name(
                        'like_button')

                    array_for_random_play = util.zip_arrays_with_condition(
                        lambda x: x[0] == current_url,
                        artist_hrefs, play_buttons, like_buttons)

                    random_num = random.randint(0,
                        len(array_for_random_play) - 1)
                    random_track = array_for_random_play[random_num]

                    random_track[1].click() #click play
                    random_time = random.randint(15, 30)
                    self.logger.debug('We will listen track for %s seconds',
                        random_time)

                    self.webagent.sleep(random_time)

                    random_track[2].click() #click_like
                    self.webagent.get_element_by_xpath_name(
                        'follow_button').click()
                    users['followed_by_me'].append(current_url)

                    followed_users_counter = followed_users_counter + 1

        return users

    def process_tracks(self, tracks):
        # aka GREAT LOOP

        tracks_info = {}

        for track_url in tracks:
            track_name = track_url.split('/')[-1]
            tracks_info[track_name] = {}
            self.logger.debug('Renew data about track: %s', track_name)

            self.logger.debug('Likes..')
            tracks_info[track_name]['likes'] =\
                self.__accumulate_new_hrefs(track_url + '/likes',
                    'users_badge', 20)

            self.logger.debug('Reposts..')
            tracks_info[track_name]['reposts'] =\
                self.__accumulate_new_hrefs(track_url + '/reposts',
                    'users_badge', 20)

            self.logger.debug('Comments..')
            tracks_info[track_name]['comments'] =\
                self.__accumulate_new_hrefs(track_url + '/comments',
                    'user_name_in_playlist', 20)

            self.logger.debug('Sets..')
            tracks_info[track_name]['sets'] =\
                self.__accumulate_new_hrefs(track_url + '/sets',
                    'artist_name_in_playlist', 20)

        return tracks_info

    def __accumulate_new_hrefs(self, url, xpath_name, threshold_num,
        accumulated_hrefs = []):
        # aka update_array

        self.webagent.open_url(url)

        # time.sleep(self.timeout * 4)

        return self.__scrape_urls_until_it_is_fruitful_enough(xpath_name,
            threshold_num, accumulated_hrefs)

    def __scrape_urls_until_it_is_fruitful_enough(self, xpath_name,
        threshold_num, acc
    ):
        elements = self.webagent.get_elements_by_xpath_name(xpath_name)
        hrefs = self.__get_hrefs(elements)

        new_hrefs_amount = len(list(set(hrefs) - set(acc)))
        accumulated_hrefs = list(set(acc + hrefs))

        # pprint.pprint(['hrefs', hrefs])
        # pprint.pprint(['accumulated_hrefs', accumulated_hrefs])
        # pprint.pprint(['new_hrefs_amount', new_hrefs_amount])

        if new_hrefs_amount >= threshold_num:
            self.scroll_page()
            return self.__scrape_urls_until_it_is_fruitful_enough(xpath_name,
                threshold_num, accumulated_hrefs)
        else:
            return accumulated_hrefs

    def __pick_significant_followers(self, significant_follower_threshold):
        wa = self.webagent

        users = wa.get_elements_by_xpath_name('users_badge')
        user_hrefs = self.__get_hrefs(users)

        follower_numbers_list =\
            self.__get_list_of_follower_numbers_on_avatars()

        return util.zip_arrays_with_condition(
            lambda x: x[0] > significant_follower_threshold,
            follower_numbers_list, user_hrefs)

    def __get_list_of_follower_numbers_on_avatars(self):
        wa = self.webagent

        data_on_badge =\
            wa.get_elements_by_xpath_name('follower_number_on_avatar')

        num_fol = []
        for d in data_on_badge:
            if d.text.find('\n') != -1:
                num = d.text.split('\n')[-1]
                num_fol.append(util.string_to_num(num))
            else:
                num_fol.append(0)
        return num_fol

    def __user_is_followed_by_me(self):
        button =\
            self.webagent.get_element_by_xpath_name('follow_button')

        followed = False

        if button.text == "Follow":
            followed = False
        elif button.text == 'Following':
            followed = True
        elif button.text == 'Follow back':
            followed = False
        else:
            followed = False

        return followed

    def __user_is_blank(self):
        is_blank = False

        artists =\
            self.webagent.get_elements_by_xpath_name('tracks_in_playlist')

        if len(artists) == 0:
            is_blank = True
        else:
            is_blank = False
        return is_blank

    def __user_is_spammer(self):
        is_spammer = False

        if self.__get_number_of_following() > 1500:
            is_spammer = True
        else:
            is_spammer = False
        return is_spammer

    def __get_number_of_following(self):
        elements =\
            self.webagent.get_elements_by_xpath_name('sidebar_header')

        a = '0'

        for el in elements:
            if el.text[el.text.find(" "):] == ' following':
                a = el.text[:el.text.find(" ")]
        number = util.string_to_num(a)
        return number

    def __user_is_reposter(self):
        is_reposter = False

        artists = self.webagent.get_elements_by_xpath_name(
            'artist_name_in_playlist')

        artists2 = []
        for a in artists:
            if a.get_attribute('href') == self.webagent.get_current_url:
                artists2.append(a.get_attribute('href'))
        if len(artists2) == 0:
            is_reposter = True
        else:
            is_reposter = False
        return is_reposter

    def __user_was_ever_liked_by_me(self):
        was_ever_liked = False

        counter = 1
        likes = self.webagent.get_elements_by_xpath_name('like')

        for like in likes:
            counter += 0
            if like.get_attribute('title') == "Liked":
                was_ever_liked = True
                break
            else:
                was_ever_liked = False

        return was_ever_liked

    def __get_hrefs(self, list):
        return map(lambda x: x.get_attribute('href'), list)
