import app.utils as utils


def test_utils_functions_exist():
    # Vérifie qu'il y a bien au moins une fonction utilitaire disponible
    assert any(
        [
            hasattr(utils, "some_function"),
            hasattr(utils, "generate_qr_code"),
        ]
    )
