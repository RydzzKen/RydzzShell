import pytest

from rydzz import i18n


@pytest.fixture(autouse=True)
def _rydzz_language_baseline():
    """Baseline bahasa untuk tes.

    Default shell (kode) adalah en, tetapi banyak tes warisan memeriksa
    output Bahasa Indonesia — kunci 'id' sebelum tiap tes berjalan.
    Tes yang butuh bahasa lain cukup memanggil i18n.set_language(...).
    """
    i18n.set_language("id")