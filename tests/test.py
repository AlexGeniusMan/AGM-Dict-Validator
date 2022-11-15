from src.dict_validator.dict_validator import validate_dict
import pytest


def test_syntax_exceptions():
    with pytest.raises(TypeError) as e:
        result_dict, errors, has_errors = validate_dict(
            original_dict=[],
            scheme={}
        )
    assert e.value.args[0] == "'original_dict' must be <class 'dict'>, not <class 'list'>."

    with pytest.raises(TypeError) as e:
        result_dict, errors, has_errors = validate_dict(
            original_dict={},
            scheme=[]  # Test 'scheme' type
        )
    assert e.value.args[0] == "'scheme' must be <class 'dict'>, not <class 'list'>."

    with pytest.raises(TypeError) as e:
        result_dict, errors, has_errors = validate_dict(
            original_dict={
                'test_key': 2,
            },
            scheme={
                'test_key': 'test_value'  # Test Value rules
            }
        )
    assert e.value.args[0] == "Value rules must be <class 'tuple'>, not <class 'str'>."

    with pytest.raises(TypeError) as e:
        result_dict, errors, has_errors = validate_dict(
            original_dict={
                'test_key': 2,
            },
            scheme={
                'test_key': (
                    'test',  # Test 'is_necessary'
                    int,
                    True)
            }
        )
    assert e.value.args[0] == "'is_necessary' parameter type must be <class 'bool'>, not <class 'str'>."

    with pytest.raises(TypeError) as e:
        result_dict, errors, has_errors = validate_dict(
            original_dict={
                'test_key': 2,
            },
            scheme={
                'test_key': (True,
                             True,  # Test 'value_type'
                             True)
            }
        )
    assert e.value.args[0] == "'value_type' parameter type must be <class 'type'>, not instance of <class 'bool'>."

    with pytest.raises(TypeError) as e:
        result_dict, errors, has_errors = validate_dict(
            original_dict={
                'test_key': 2,
            },
            scheme={
                'test_key': (True,
                             int,
                             'test')  # Test 'conversion'
            }
        )
    assert e.value.args[0] == "'conversion' parameter type must be <class 'bool'>, not <class 'str'>."


def test_no_errors():
    result_dict, errors, has_errors = validate_dict(
        original_dict={
            'key_str': 'value_str',
            'key_int': 123,
            'key_float': 123.321,
            'key_bool': True
        },
        scheme={
            'key_str': (True, str, True),
            'key_int': (True, int, True),
            'key_float': (True, float, True),
            'key_bool': (True, bool, True)
        }
    )
    assert has_errors is False


def test_missing_fields():
    result_dict, errors, has_errors = validate_dict(
        original_dict={
            'key_1': 'value',
            'key_3': 'value',
            'key_4': 'value',
            'key_6': 'value',
        },
        scheme={
            'key_1': (True, str, False),
            'key_2': (True, str, False),
            'key_3': (True, str, False),
            'key_4': (True, str, False),
            'key_5': (True, str, False),
            'key_6': (True, str, False),
        }
    )
    assert result_dict == {
        'key_1': 'value',
        'key_3': 'value',
        'key_4': 'value',
        'key_6': 'value'
    }
    assert has_errors is True
    assert errors == {
        'missing_keys': ['key_2', 'key_5'],
        'value_type_errors_keys': [],
        'converting_errors_keys': []
    }


class SomeClass:
    def __init__(self):
        self.test_field = 'test_value'


def test_keys_have_wrong_values_with_conversion():
    some_instance = SomeClass()
    result_dict, errors, has_errors = validate_dict(
        original_dict={
            'key_1': 'value',
            'key_2': '4',
            'key_3': '4.33',
            'key_4': 'True',
            'key_5': 'some_string',
            'key_6': some_instance
        },
        scheme={
            'key_1': (True, str, True),
            'key_2': (True, int, True),
            'key_3': (True, float, True),
            'key_4': (True, bool, True),
            'key_5': (True, int, True),
            'key_6': (True, SomeClass, True),
        }
    )
    assert result_dict == {
        'key_1': 'value',
        'key_2': 4,
        'key_3': 4.33,
        'key_4': True,
        'key_6': some_instance,
    }
    assert has_errors is True
    assert errors == {
        'missing_keys': [],
        'value_type_errors_keys': ['key_5'],
        'converting_errors_keys': ['key_5']
    }


def test_keys_have_wrong_values_without_conversion():
    some_instance = SomeClass()
    result_dict, errors, has_errors = validate_dict(
        original_dict={
            'key_1': 'value',
            'key_2': '4',
            'key_3': '4.33',
            'key_4': 'True',
            'key_5': 'some_string',
            'key_6': some_instance
        },
        scheme={
            'key_1': (True, str, False),
            'key_2': (True, int, False),
            'key_3': (True, float, False),
            'key_4': (True, bool, False),
            'key_5': (True, int, False),
            'key_6': (True, SomeClass, False),
        }
    )
    assert result_dict == {
        'key_1': 'value',
        'key_6': some_instance,
    }
    assert has_errors is True
    assert errors == {
        'missing_keys': [],
        'value_type_errors_keys': ['key_2', 'key_3', 'key_4', 'key_5'],
        'converting_errors_keys': []
    }
