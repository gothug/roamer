import pprint

class WebAgent:
    def __init__(self, timeout = 0):
        self.pages          = {}
        self.current_page   = None
        self.current_url    = None
        self.timeout        = timeout

    def add_page_for_url(self, url, page):
        self.pages[url] = page
        pass

    def open_url(self, url):
        try:
            self.current_page = self.pages[url]
            self.current_url = url
        except KeyError, e:
            raise Exception(
                'mock.webagent.WebAgent.open_url(): "%s"' % str(e))

    def sleep(self, timeout):
        pass

    def get_elements_by_xpath_name(self, xpath_name):
        return self.current_page.get_elements_by_xpath_name(xpath_name)

    def get_element_by_xpath_name(self, xpath_name):
        return self.current_page.get_element_by_xpath_name(xpath_name)

    def scroll_page_to_the_end(self, xpath_name):
        pass

    def login_to_soundcloud(self):
        pass

    def get_current_url(self):
        return self.current_url
