import numpy as np
import pandas as pd


def read_file(file=None):
	data = pd.read_excel('Words.xlsx')

	return data

def push():
	word = input("Enter word: ")
	translation = input("Enter translation: ")


def main():
	# read_file()
	pass


if __name__ == "__main__":
	push()