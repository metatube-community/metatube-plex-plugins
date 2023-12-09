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

    @classmethod
    def Parse(cls, raw_pid):
        values = raw_pid.split(':')
        return cls(
            provider=values[0] if len(values) >= 1 else '',
            id=unquote(values[1]) if len(values) >= 2 else '',
            position=cls.to_float(values[2]) if len(values) >= 3 else None,
            update=cls.to_bool(values[3]) if len(values) >= 4 else None,
        )

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
