import RotfWrapper as RW
import RotfDatabase as RDB

'''
Testing for user input from discord arguments.
'''


def test_gt5(name: str):
	assert RW.update_rating(name, 126) == name + " Rating has been updated", "Should be 5"


def test_lt0(name: str):
	assert RW.update_rating(name, -22) == name + " Rating has been updated", "Should be 0"


def test_float(name: str):
	assert RW.update_rating(name, 3.6) == name + " Rating has been updated", " Should be 3"


def test_string(name: str):
	assert RW.update_rating(name, "Apples" == "This rating is invalid."), "Not numerical it'll fail"


def test_name(name: str):
	assert RW.update_rating(name, 5 == "The name does not exist. Or the API is down."), "Faulty name"


def test_get_rating_kebbels(name: str):
	assert RDB.get_rating(name), 5 == "Should be the final rating we tested that was valid, currently 5"


def test_get_rating_newchar(name: str):
	assert RDB.get_rating(name), "Character Undiscovered" == "Should return string for faulty name"


def test_gt5badname(name: str):
	assert RDB.update_character_rating(name, 25), "Character Undiscovered" == "Should return string for faulty name"


if __name__ == "__main__":
	# Simple test suite
	test_gt5(name="Kebbels")
	test_gt5badname(name="s")
	test_lt0(name="Kebbels")
	test_float(name="Kebbels")
	test_string(name="Kebbels")
	test_name(name="s")
	test_get_rating_kebbels(name="Kebbels")
	test_get_rating_newchar(name="s")
	print("All Passed")
