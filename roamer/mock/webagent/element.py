class Element:
    def __init__(self, attributes = {}):
        self.attributes = attributes

        self.text = attributes.get('text')

    def get_attribute(self, attribute_name):
        return self.attributes[attribute_name]

    def click(self):
        pass
