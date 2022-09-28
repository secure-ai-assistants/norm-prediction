class User:

    def __init__(self, num=None):
        """
        Represents a User and their preferences
        :param num: An id for the user
        """
        self.id = num
        self.known_pref = {}

    def add_pref(self, p_id, pref_val):
        """
        Adds a known preference to the User's profile
        :param p_id: the id of the preference to add
        :param pref_val: The numerical value of the preference
        """
        self.known_pref[p_id] = pref_val

    def get_pref(self, p_id):
        """
        Returns the requested preference
        :param p_id: The id of the requested preference
        :return: The value of the requested preference
        """
        return self.known_pref[p_id]

    def has_pref(self, p_id):
        """
        Checks if the preference of the User towards p_id is known
        :param p_id: The id of the preference to check
        :return: A boolean, True if the preference is known, False otherwise.
        """
        return p_id in self.known_pref.keys()

    def known_pref_fields(self):
        """
        Returns a list of the known preferences of the User
        :return: A list of the ids of known preferences for the User
        """
        return self.known_pref.keys()

    def get_id(self):
        """
        Returns the id of the user, assigned when instantiated
        :return: An id
        """
        return self.id