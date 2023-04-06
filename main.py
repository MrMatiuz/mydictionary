import App
import numpy as np

if __name__ == "__main__":
	vocabulary_name = 'Words.xlsx'
	app = App.App(vocabulary_name)

	app.read_file()
	# word = app.check_your_vocabulary(random=True)
	word_indxs = app.get_indxs(random=True)
	app.check_word(indx=word_indxs[0])
