#! /usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from PrefPredict import PrefPredict
from User import User
import pandas as pd
from random import randint

# WSGI entry point
app = Flask(__name__)

# define global vars
questions = dict()
count = 0
NUM_QUESTIONS = 4

# load questions
data = pd.read_csv("main_data.csv", encoding="ISO-8859-1", low_memory=False)

# API START
@app.route('/questions', methods=['GET'])
def gen_questions():
	global count
	global questions
	global data

	# we need to keep track of participants so that we know what questions they answered later
	count += 1
	questions[str(count)] = []
	text_out = {"uid":count}
	total = data.shape[1]

	# choose n questions at random for the participant to answer
	for i in range(NUM_QUESTIONS):
		q = randint(0, total - 1)
		questions[str(count)].append(data.columns[q])
		text_out[str(i)] = data.iloc[0][q]

	print("User number", count, "Sent questions", questions[str(count)])
	response = make_response(jsonify(text_out))
	return response

@app.route('/predict', methods=['GET'])
def predict():
	global questions
	max_dist = 0
	min_common = 5
	min_users_prediction = 5
	pred = PrefPredict(max_dist, min_common, min_users_prediction)
	args = request.args
	uid = args['uid']

	# add user preferences from the request parameters
	user = User()
	for i in range(NUM_QUESTIONS):
		q = questions[uid][i]
		a = int(args[str(i)])
		user.add_pref(q, a)
		print("Added pref for question", q, "=", a, type(a))

	# make predictions
	p = pred.predict(user, "Q12_14")
	print(p)

	response = make_response(jsonify({"response": "placeholder"}))

	return response

