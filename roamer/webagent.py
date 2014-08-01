from selenium import webdriver
import time
import pprint

import util

class WebAgent:
    def __init__(self, timeout = 6):
        self.browser       = webdriver.Firefox()
        self.action_chains = webdriver.ActionChains
        self.timeout       = timeout

        self.xpaths = {
            'users_badge'               :
                "//a[@class='userAvatarBadge__usernameLink']",
            'track_name_in_playlist'    :
                "//div[@class = 'sound__header']"\
                "//a[starts-with(@class, 'soundTitle__title sc-link-dark')]",
            'tracks_in_playlist'        :
                "//div[@class = 'sound__header']",
            'artist_name_in_playlist'   :
                "//div[@class = 'sound__header']"\
                "//a[starts-with(@class, 'soundTitle__user')]",
            'follower_number_on_avatar' :
                "//div [@class = 'userAvatarBadge__header']",
            'follow_button'             :
                "//button[starts-with(@class, 'sc-button sc-button-follow "\
                "sc-button-medium')]",
            'play_button'               :
                "//li//div[@class = 'sound__header']"\
                "//button[@title = 'Play']",
            'like_button'               :
                "//li//div[starts-with(@ class, 'sound__footer')]"\
                "//button[starts-with(@class, 'sc-button sc-button-like')]",
            'like'                      :
                "//li//div[starts-with(@ class, 'sound__foot')]"\
                "//button[starts-with(@class, 'sc-button sc-button-l')]",
            'sidebar_header'            :
                "//span[@class = 'sidebarHeader__actualTitle']",
            'user_name_in_playlist'     :
                "//a [starts-with(@class, 'commentItem__username')]"
        }

    def get_current_url(self):
        return self.browser.current_url

    def login_to_soundcloud(self):
        self.open_url('https://soundcloud.com')
        self.__login_facebook('USER', 'PASSWORD')

    # def get_hrefs_from_page(self, url, xpath_name): # Shoud this method exist?
    #     self.__open_url(url)
    #     elements = self.__get_elements_by_xpath_name(xpath_name)
    #     return self.__get_hrefs(elements)

    def get_element_by_xpath_name(self, xpath_name):
        xpath_string = self.__get_xpath_string(xpath_name)
        return self.browser.find_element_by_xpath(xpath_string)

    def get_elements_by_xpath_name(self, xpath_name):
        xpath_string = self.__get_xpath_string(xpath_name)
        return self.browser.find_elements_by_xpath(xpath_string)

    def scroll_page_to_the_end(self, xpath_name):
        elements_xpath = self.__get_xpath_string(xpath_name)

        stop = False
        length_prev = 0

        while not stop:
            length = len(self.browser.find_elements_by_xpath(elements_xpath))

            if length != length_prev:
                self.scroll_page()
                length_prev = length
            else:
                stop = True

    def scroll_page(self):
        self.browser.execute_script(
            'window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(self.timeout)

    def open_url(self, url):
        url = url
        self.browser.get(url)
        time.sleep(self.timeout)

    def sleep(self, timeout):
        time.sleep(timeout)

    def __login_facebook(self, mail, passw):
        browser = self.browser

        parent_h = browser.current_window_handle
        sign_in = browser.find_element_by_xpath("//button[starts-with(@title,\
            'Sign')]")
        sign_in.click()
        handles = browser.window_handles # before the pop-up window closes
        handles.remove(parent_h)
        browser.switch_to_window(handles.pop())
        facebook = browser.find_element_by_class_name("facebook-signin")
        facebook.click()
        email = browser.find_element_by_class_name("inputtext")
        email.send_keys(mail)

        password = browser.find_element_by_class_name("inputpassword")
        password.send_keys(passw)
        login_button = browser.find_element_by_id("u_0_1")
        login_button.click()
        browser.switch_to_window(parent_h)

    def __get_xpath_string(self, xpath_name):
        return self.xpaths[xpath_name]
