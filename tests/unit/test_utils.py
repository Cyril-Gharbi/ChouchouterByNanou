import app.utils as utils


def test_utils_functions_exist():
    expected_functions = [
        "send_email",
        "generate_password_reset_token",
        "verify_password_reset_token",
        "update_user_session",
        "send_discount_email",
    ]

    for func in expected_functions:
        assert hasattr(utils, func), f"Function {func} is missing in utils.py"
