# -*- coding: utf-8 -*-

try:  # Python 2
    from urllib import quote, unquote
except ImportError:  # Python 3
    from urllib.parse import quote, unquote


class ProviderID(object):
    def __init__(self, provider, id, position=None, update=None):
        self.provider = provider
        self.id = quote(id)
        self.position = position
        self.update = update

    def validate(self):
        if (isinstance(self.provider, str) and self.provider.strip()) and \
                (isinstance(self.id, str) and self.id.strip()):
            return True
        else:
            return False

    @classmethod
    def Parse(cls, s):
        values = s.split(':')
        if (len(values) < 2
                or not values[0].strip()
                or not values[1].strip()):
            raise ValueError('invalid provider format: {0}'.format(s))
        return cls(
            provider=values[0],
            id=unquote(values[1]),
            position=cls.to_float(values[2]) if len(values) >= 3 else None,
            update=cls.to_bool(values[3]) if len(values) >= 4 else None,
        )

    @classmethod
    def TryParse(cls, s):
        # noinspection PyBroadException
        try:
            return cls.Parse(s)
        except:
            return None

    @staticmethod
    def to_float(s):
        try:
            return round(float(s), 2)
        except ValueError:
            return None

    @staticmethod
    def to_bool(s):
        if s in ('1', 't', 'T', 'true', 'True', 'TRUE'):
            return True
        elif s in ('0', 'f', 'F', 'false', 'False', 'FALSE'):
            return False
        else:
            return None

    def __str__(self):
        values = [self.provider, self.id]
        values.append(str(round(self.position, 2))) \
            if self.position is not None else None
        values.append((':' if self.position is None else '') +
                      ('1' if self.update else '0')) \
            if self.update is not None else None
        return ':'.join(values)
