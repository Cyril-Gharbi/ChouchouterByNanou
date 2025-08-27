import app.utils as utils


def test_utils_functions_exist():
    # On vérifie l'existence de fonctions RÉELLEMENT présentes
    assert any(
        [
            hasattr(utils, "send_email"),
            hasattr(utils, "generate_password_reset_token"),
            hasattr(utils, "verify_password_reset_token"),
            hasattr(utils, "update_user_session"),
            hasattr(utils, "send_discount_email"),
        ]
    )
