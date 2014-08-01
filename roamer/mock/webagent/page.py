class Page:
    def __init__(self):
        self.elements = {}

    def add_element(self, xpath_name, element):
        if xpath_name not in self.elements:
            self.elements[xpath_name] = []

        self.elements[xpath_name].append(element)

    def get_elements_by_xpath_name(self, xpath_name):
        return self.elements.get(xpath_name) or []

    def get_element_by_xpath_name(self, xpath_name):
        els = self.elements.get(xpath_name)
        return els and els[0] or None
