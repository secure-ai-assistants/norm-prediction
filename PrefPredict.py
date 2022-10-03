import pandas as pd
import numpy as np
import math
from User import User

class PrefPredict:

    def __init__(self,max_dist, min_common, min_users_pred):
        """
        We load the database and prepare everything to make predictions
        :param max_dist: The maximum distance between to users for them to be considered similar
        :param min_common: The minimum ammount of commonly known preferences for assessing the distance between users
        :param min_users_pred: The minimum ammount of similar users required to make a prediction
        """
        self.max_dist = max_dist
        self.min_common = min_common
        self.min_users_pred = min_users_pred
        # We read the privacy preferences database.
        self.data = pd.read_csv("main_data.csv", encoding="ISO-8859-1", low_memory=False)
        # There are 1737 participants in the database, we list their ids.
        self.user_ids = list(range(1, 1738))
        # The database has some errors in a few participants that break the code when making predictions.
        # We remove these participants.
        problematic_users = [168, 204, 218, 322, 795, 1124, 1153, 1154, 1240, 1445]
        for pu in problematic_users:
            self.user_ids.remove(pu)
        # We build the ids of the privacy preferences, these are the id of the question in the survey they come from
        # e.g. "Q12_1".
        self.preference_ids = self.get_preference_ids()
        # To access the preference knowleddge in the database we will use the list of their users.
        self.database_users = []
        # We fill this list.
        self.build_database_users()
        # This dictionary is used to avoid calculating common known preference between users more than once.
        self.common_prefs = {}

    def get_preference_ids(self):
        """
        This function retrieves the preference ids from the dataset. These ids are strings containing the
        names of the questions from which the preferences were gathered, for example, "Q12_1".
        :return: A list of strings.
        """
        preference_ids = []
        for id in self.data.columns:
            #Only questions up to Q147 are related to preferences, later questions are related to demografics.
            if int(id.split("_")[0].replace("Q", ""))<148:
                preference_ids.append(id)
        return preference_ids

    def build_database_users(self):
        """
        This function loads the preferences from the database as User instances into self.database_users.
        """
        for u_id in self.user_ids:
            user = User(u_id)
            for p_id in self.preference_ids:
                #if the preference is not Nan we add it to the known preferences of the user.
                if not pd.isna(self.data.loc[user.get_id(), p_id]):
                    #Before adding it, we parse the preference from string to numerical form.
                    user.add_pref(p_id, self.num_answer(self.data.loc[user.get_id(), p_id]))
            self.database_users.append(user)

    def find_valid_users(self, pref_id):
        """
        From all participants in the database it selects those for which we know their preferences for pref_id
        It returns the list of these users. Hence, if we want to predict pref_id for another user, we can use this
        list of users to check similarity and eventually make the prediction.
        :param pref_id: A string id of the preference we are checking.
        :return: A list of User instances
        """
        validusers = []
        for user in self.database_users:
            if user.has_pref(pref_id):
                validusers.append(user)
        return validusers

    def num_answer(self, ans):
        """
        In the database the answers to the survey questions are in text for (e.g. "completely unacceptable")
        Thi function transforms them into numbers from 1-5 as follows:
        completely unacceptable -> 1, unacceptable -> 2, neutral -> 3, acceptable -> 4, completely acceptable -> 5
        :param ans: A string containing the answer from the dataset
        :return: An integer representing the anser, as detailed above
        """
        ans = ans.lower().replace(" ", "")
        num = math.nan
        if "unacceptable" in ans:
            if "completely" in ans:
                #This is the case "completely unacceptable"
                num = 1
            else:
                # This is the case "unacceptable"
                num = 2
        elif "acceptable" in ans:
            if "completely" in ans:
                # This is the case "completely acceptable"
                num = 5
            else:
                # This is the case "unacceptable"
                num = 4
        if "neutral" in ans:
            # This is the case "neutral"
            num = 3
        return num

    def common_known_prefs(self, user1, user2):
        """
        Given two User instances, this function computes their commonly known preferences, i.e. those which we
        already know for both users. To avoid computing it more than once, it saves the list of preference ids
        for their commonly known preferences into the dictionary self.common_prefs.
        :param user1: A User instance.
        :param user2: A User instance.
        :return: An integer with the ammount of common preferences.
        """
        if user1 not in self.common_prefs:
            self.common_prefs[user1] = {}
        if user2 not in self.common_prefs[user1]:
            self.common_prefs[user1][user2] = []
            #for p_id in self.preference_ids:
            #    if user1.has_pref(p_id) and user2.has_pref(p_id):
            #        self.common_prefs[user1][user2].append(p_id)
            for p_id in set(user1.known_pref).intersection(set(user2.known_pref)):
                self.common_prefs[user1][user2].append(p_id)

        return len(self.common_prefs[user1][user2])

    def distance(self, user1, user2):
        """
        This function returns the distance between two users, this is the average diference between
        their commonly known preferences. This function makes use of the variable self.min_common,
        this is an integer of the minimum ammount of common known variables, if the ammount is lower
        we consider we have not enough information and assess the distance as infinity.
        :param user1: A User instance.
        :param user2: A User instance.
        :return: A float, the distance between user1 and user2.
        """
        numcommon = self.common_known_prefs(user1, user2)
        if numcommon >= self.min_common:
            #If the users do have the minimum required ammount of common preferences
            dis = 0
            #For each of their commonly known preferences we calculate their difference and add it to the distance
            for p_id in self.common_prefs[user1][user2]:
                dis += abs(user1.get_pref(p_id) - user2.get_pref(p_id))
            #We average the distance
            dis = dis / float(numcommon)
        else:
            #If the users do not have the minimum required ammount of common preferences
            dis = math.inf
        return dis

    def list_similar_users(self, user1, pred_pref_id = None):
        """
        Finds the users in the database for which we known their preference toward the
        targeted pred_pref_id preference we want to predict, and returns a list of those
        considered similar to user1
        :param user1: A User instance
        :param pred_pref_id: A targeted prefernce to predict
        :return: A list of User instances, those similar with user1 and for which
        we know their preference toward pred_pref_id
        """
        retdis = []
        distances = {}
        similarusers = []
        # If a preference id is provided we will only check the userss for which we know that preference
        # Otherwise all users are considered
        if pred_pref_id:
            listusers = self.find_valid_users(pred_pref_id)
        else:
            listusers = self.database_users

        # We calculate the distance between the provided user1 and all (valid) users
        for user2 in listusers:
            distances[user2] = self.distance(user1, user2)
            # If the distance is lower than the threshold, we consider the users to be similar
            if distances[user2] <= self.max_dist:
                    similarusers.append(user2)
                    retdis.append(distances[user2])
        # If the number of similar users is lower than the required threshold to make predictions
        # We add the ones that are the most similar (even if they have larger distance than max_dist)
        # Until we have enough similar users
        if len(similarusers) < self.min_users_pred:
            for i in range(self.min_users_pred-len(similarusers)):
                key = min(distances, key=distances.get)
                similarusers.append(key)
                retdis.append(distances.pop(key))
        return similarusers, retdis

    def predict(self, user, pref_id, rho = 0.5, mu = 0.5, conf = True):
        """
        Given a user instance and a preference id, this function predicts the preference of the user.
        :param user: A User instance.
        :param pref_id: A string with the id of the targeted preference
        :return: A float, the predicted preference in the scale 1-5
        (1: completly unacceptable, 5:completely acceptaable)
        """
        # We build a list of the database users that are similar with the user and for which we know
        # their preference for pref_id.
        similar_users, dis = self.list_similar_users(user, pref_id)
        # We gather their preferences for the targeted id and put them into a list
        ans = []
        for sim_u in similar_users:
            ans.append(sim_u.get_pref(pref_id))
        # The predicted preference is the average of those we gathered
        # We also calculate the preference confidence and return it if required
        if conf:
            rhopart = min(1.0, sum(dis)/len(dis))
            mupart = min(1.0, float(np.std(ans)))
            confidence = 1 - rho * rhopart - mu * mupart
            ret = (sum(ans)/float(len(ans)), confidence)
        else:
            ret = sum(ans)/float(len(ans))
        return ret

    def norm_block(self, pred, conf):
        """
        This function transforms numeric preferences into norms. It devides the preference scale 1-5 into three
        blocks relating to prohibition, unclear preference (no norm generated), and permission.
        :param pred: A float representing a preference in [1,5]
        :param conf: A float representing the prediction confidence in [0,1] (larger numbers mean larger confidence)
        :return: An integer 1-3, representing 1:prohibition, 2:unclear preference (no norm produced), 3:permission
        """
        block = 1
        if pred >2+conf and pred <4-conf:
            block = 2
        if pred > 4-conf:
            block = 3
        return block

    def getUser(self, id):
        return self.database_users[id]

    def getPrefIds(self):
        return self.preference_ids

if __name__ == "__main__":

    #EXAMPLE OF USE

    #Example thresholds
    max_dist = 0
    min_common = 5
    min_users_prediction = 5
    #Load the dataset
    pred = PrefPredict(max_dist, min_common, min_users_prediction)
    #Create a User instance for the user for which you want to make predictions
    #ex_user = User()
    ex_user = pred.getUser(2)
    #Add the known preferences using the string preference id and an integer preference in the scale 1-5
    #ex_user.add_pref("Q67_1",1)
    #ex_user.add_pref("Q67_2",2)
    #ex_user.add_pref("Q67_3",3)
    #ex_user.add_pref("Q67_4",4)
    #ex_user.add_pref("Q67_5",5)
    #ex_user.add_pref("Q67_6",1)
    #ex_user.add_pref("Q67_7",2)
    #ex_user.add_pref("Q67_8",3)
    #ex_user.add_pref("Q67_9",4)
    #ex_user.add_pref("Q67_10",5)
    #Predict the preference for the user to an unknown preference id
    #print(pred.predict(ex_user, 'Q68_1'))
    for id in pred.getPrefIds():
        if not ex_user.has_pref(id):
            print(str(id)+":"+str(pred.predict(ex_user, id)))