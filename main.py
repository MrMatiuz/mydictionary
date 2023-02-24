import App
import numpy as np

if __name__ == "__main__":
	vocabulary_name = 'Words.xlsx'
	app = App.App(vocabulary_name)

	app.read_file()
	word = app.check_your_vocabulary()