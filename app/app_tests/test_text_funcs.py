#This test is run in terminal with the command: python3 -m pytest app_tests/test_text_funcs.py
import pytest 
from utils import text_processing_functions as text_functions

def test_clean_text():
    """Test the clean_text function."""
    text = "I'm a #test"
    text = text_functions.clean_text(text)
    assert text == "i am a test"
    text = "!#="
    text = text_functions.clean_text(text)
    assert text == ""
    text = "I will eat a banana"
    text = text_functions.clean_text(text)
    assert text == "i will eat a banana"
    text = ""
    text = text_functions.clean_text(text)
    assert text == ""


def test_delete_words():
    black_list = ["test", "banana"]
    text = "I will eat a banana"
    text = text_functions.delete_words(text, black_list)
    assert text == "I will eat a "
    text = "I will eat a test"
    text = text_functions.delete_words(text, black_list)
    assert text == "I will eat a "
    text = "I will eat a test and a banana"
    text = text_functions.delete_words(text, black_list)
    assert text == "I will eat a and a "
    text = "I will eat a test and a banana and a test"
    text = text_functions.delete_words(text, black_list)
    assert text == "I will eat a and a and a "
    text = "today is a nice day"
    text = text_functions.delete_words(text, black_list)
    assert text == "today is a nice day"
    text = ""
    text = text_functions.delete_words(text, black_list)
    assert text == ""
    text = " "
    text = text_functions.delete_words(text, black_list)
    assert text == " "
    text = "test"
    text = text_functions.delete_words(text, black_list)
    assert text == ""


def test_count_words():
    text = "I will eat a banana in a house  because  a banana is a fruit, banana eat" 
    text = text_functions.count_occurrences(text, top_n = 3)
    assert len(text) == 3
    assert text == [("a", 4), ("banana", 3), ("eat", 2)]
    text = "1 2 3 4 5 6 7 8 9"
    text = text_functions.count_occurrences(text)
    assert len(text) == 9
    assert text == [("1", 1), ("2", 1), ("3", 1), ("4", 1), ("5", 1), ("6", 1), ("7", 1), ("8", 1), ("9", 1)]
    text = ""
    text = text_functions.count_occurrences(text)
    assert len(text) == 0
    assert text == []
    text = " "
    text = text_functions.count_occurrences(text)
    assert len(text) == 0
    assert text == []
    text = "banana banana banana Banana BAnana BAnaNa, BANANA"
    text = text_functions.count_occurrences(text)
    assert len(text) == 1
    assert text == [("banana", 7)]

