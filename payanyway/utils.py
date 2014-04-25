class AttributeDescriptor(object):
    def __init__(self, key):
        self.key = key

    def __get__(self, instance, owner):
        return instance._get_param(self.key)

    def __set__(self, instance, value):
        instance._set_param(self.key, value)