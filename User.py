
class User:

    def __init__(self, num=None):
        self.id = num
        self.known_pref = {}

    def add_pref(self, p_id, pref_val):
        self.known_pref[p_id] = pref_val

    def get_pref(self, p_id):
        return self.known_pref[p_id]

    def has_pref(self, p_id):
        return p_id in self.known_pref.keys()

    def known_pref_fields(self):
        return self.known_pref.keys()

    def get_id(self):
        return self.id