from app.utils.logger import setup_logs


def test_logger():
    # Test the logger
    setup_logs("app", overwrite=True, level="DEBUG")
    assert True
