# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, Markup, redirect, url_for
import heap

app = Flask(__name__)
show_word = False
word_list = None
savefile = None
root = None
tmp_data = None

class word_pair:
	def __init__(self, index, pair):
		self.text = pair[0]
		self.meaning = pair[1]
		self.index = index
	
	def __repr__(self):
		return str((self.index, self.text, self.meaning))
	
	def __str__(self):
		return self.__repr__()

@app.route('/')
def home():
	if word_list is None:
		return redirect('/login')
	global root
	word_list.save(savefile)
	if show_word:
		return render_template('home.html', meaning=root.word.meaning, word=root.word.text)
	else:
		root = word_list.get_next()
		if root is None:
			return render_template('home.html', meaning='UPLOAD WORDS', word='')
		return render_template('home.html', meaning=root.word.meaning, word='')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
	if 'user' not in request.form:
		return render_template('login.html')
	global word_list
	global savefile
	savefile = request.form['user']+'.pl'
	word_list = heap.main(savefile)
	if len(word_list.word_heap_map) > 0:
		return redirect('/')
	else:
		return redirect('/upload')

@app.route('/edit')
def edit_page():
	global tmp_data
	if word_list is None:
		return redirect('/login')
	wp = word_list.get_all_word_pairs()
	tmp_data = [word_pair(i, wp[i]) for i in range(len(wp))]
	return render_template('edit.html', words=tmp_data)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
	global tmp_data
	print 'started'
	for i in range(len(tmp_data)):
		delete = request.form.get('delete_' + str(i), False)
		text = request.form.get('text_' + str(i), tmp_data[i].text)
		meaning = request.form.get('meaning_' + str(i), tmp_data[i].meaning)
		if delete:
			word_list.delete_word(tmp_data[i].text, tmp_data[i].meaning)
		if text != tmp_data[i].text or meaning != tmp_data[i].meaning:
			word_list.change_word(text, meaning, tmp_data[i].text, tmp_data[i].meaning)
	print 'to while'
	i = 1
	while request.form.get('text_new_' + str(i), False):
		text = request.form['text_new_' + str(i)]
		meaning = request.form['meaning_new_' + str(i)]
		if len(text) > 0 and len(meaning) > 0:
			word_list.add_to_add(text, meaning)
		i += 1
	print 'complete'
	return edit_page()

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
	if word_list is None:
		return redirect('/login')
	if 'csv_name' not in request.form:
		return render_template('upload.html')
	word_list.add_csv_file(request.form['csv_name'])
	return redirect('/')

@app.route('/guess', methods=['GET', 'POST'])
def guess_word():
	global show_word
	word_guessed = request.form['guess']
	w = root.word
	w.say()
	if word_guessed == w.text:
		w.update_stats(not show_word)
		root.update()
		show_word = False
	else:
		show_word = True
	return redirect('/')
	
if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
