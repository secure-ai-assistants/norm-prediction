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

	# choose a selection of question types that will give 32 data points
	q0 = get_question(10)
	questions[str(count)].append(q0[0])
	text_out["q0"] = q0[1]
	q1 = get_question(5)
	questions[str(count)].append(q1[0])
	text_out["q1"] = q1[1]
	q2 = get_question(5)
	questions[str(count)].append(q2[0])
	text_out["q2"] = q2[1]
	q3 = get_question(6)
	questions[str(count)].append(q3[0])
	text_out["q3"] = q3[1]
	q4 = get_question(6)
	questions[str(count)].append(q4[0])
	text_out["q4"] = q4[1]

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
	print(args)
	total = data.shape[1]
	text_out = {}

	# add user preferences from the request parameters
	user = User()
	for i in range(5):
		q = questions[uid][i]
		a = int(args[str(i)])
		user.add_pref(q, a)
		print(f"Added pref for question '{q}' (type {type(q)} = '{a}' (type {type(a)})")

	# make predictions
	for i in range(3):
		q = randint(0, total - 1)
		q_name = data.columns[q]
		q_text = data.iloc[0][q]
		print(q_name, q_text)
		p = pred.predict(user, q_name)
		print(p, round(p))
		text_out[f"p{i}"] = q_text + str(p)

	response = make_response(jsonify(text_out))

	return response

def get_question(num_answers):
	total = data.shape[1]

	while True:
		q = randint(0, total - 1)
		q_name = data.columns[q].split("_")[0]
		q_text = data.iloc[0][q].split(":")[0]

		if data[f"{q_name}_1"][0].find("Your Parents") >= 0 and num_answers == 10:
			break
		elif data[f"{q_name}_1"][0].find("Assistant Provider") >= 0 and num_answers == 5:
			break
		elif data[f"{q_name}_1"][0].find("No conditions") >= 0 and num_answers == 6:
			break
		
	return (q_name, q_text)
