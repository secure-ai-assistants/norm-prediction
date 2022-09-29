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

	print(f"{count}:  sent {questions[str(count)]}")
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
	total = data.shape[1]
	text_out = {}
	predict_out = f"{uid}: "
	control_out = f"{uid}: "

	user = User()

	# add user preferences from the request parameters
	# answers to Q0
	user.add_pref(f"{questions[uid][0]}_1", int(args["q0_1"]))
	user.add_pref(f"{questions[uid][0]}_2", int(args["q0_2"]))
	user.add_pref(f"{questions[uid][0]}_3", int(args["q0_3"]))
	user.add_pref(f"{questions[uid][0]}_4", int(args["q0_4"]))
	user.add_pref(f"{questions[uid][0]}_5", int(args["q0_5"]))
	user.add_pref(f"{questions[uid][0]}_6", int(args["q0_6"]))
	user.add_pref(f"{questions[uid][0]}_7", int(args["q0_7"]))
	user.add_pref(f"{questions[uid][0]}_8", int(args["q0_8"]))
	user.add_pref(f"{questions[uid][0]}_9", int(args["q0_9"]))
	user.add_pref(f"{questions[uid][0]}_10", int(args["q0_10"]))
	
	# answers to Q1
	user.add_pref(f"{questions[uid][1]}_1", int(args["q1_1"]))
	user.add_pref(f"{questions[uid][1]}_2", int(args["q1_2"]))
	user.add_pref(f"{questions[uid][1]}_3", int(args["q1_3"]))
	user.add_pref(f"{questions[uid][1]}_4", int(args["q1_4"]))
	user.add_pref(f"{questions[uid][1]}_5", int(args["q1_5"]))
	
	# answers to Q2
	user.add_pref(f"{questions[uid][2]}_1", int(args["q2_1"]))
	user.add_pref(f"{questions[uid][2]}_2", int(args["q2_2"]))
	user.add_pref(f"{questions[uid][2]}_3", int(args["q2_3"]))
	user.add_pref(f"{questions[uid][2]}_4", int(args["q2_4"]))
	user.add_pref(f"{questions[uid][2]}_5", int(args["q2_5"]))

	# answers to Q3
	user.add_pref(f"{questions[uid][3]}_1", int(args["q3_1"]))
	user.add_pref(f"{questions[uid][3]}_2", int(args["q3_2"]))
	user.add_pref(f"{questions[uid][3]}_3", int(args["q3_3"]))
	user.add_pref(f"{questions[uid][3]}_4", int(args["q3_4"]))
	user.add_pref(f"{questions[uid][3]}_5", int(args["q3_5"]))
	user.add_pref(f"{questions[uid][3]}_6", int(args["q3_6"]))

	# make predictions
	for i in range(3):
		while True:
			q = randint(0, total - 1)
			q_name = data.columns[q]
			q_text = data.iloc[0][q]
			if int(q_name.split("_")[0][1:]) <= 147:
				break
		p = pred.predict(user, q_name)
		predict_out += f"predict {q_name} as {p}; "
		text_out[f"p{i}"] = f"{q_text} {str(p)}"
	
	# choose controls
	for i in range(3):
		while True:
			q = randint(0, total - 1)
			q_name = data.columns[q]
			q_text = data.iloc[0][q]
			if int(q_name.split("_")[0][1:]) <= 147:
				break
		p = ["True", "False"][randint(0, 1)]
		control_out += f"control {q_name} as {p}; "
		text_out[f"c{i}"] = f"{q_text} {str(p)}"

	response = make_response(jsonify(text_out))
	print(predict_out)
	print(control_out)

	return response

def get_question(num_answers):
	total = data.shape[1]

	while True:
		q = randint(0, total - 1)
		q_name = data.columns[q].split("_")[0]
		q_text = data.iloc[0][q].split(":")[0]

		if int(q_name[1:]) <= 147:
			if data[f"{q_name}_1"][0].find("Your Parents") >= 0 and num_answers == 10:
				break
			elif data[f"{q_name}_1"][0].find("Assistant Provider") >= 0 and num_answers == 5:
				break
			elif data[f"{q_name}_1"][0].find("No conditions") >= 0 and num_answers == 6:
				break
		
	return (q_name, q_text)
