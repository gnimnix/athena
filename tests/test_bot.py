import pytest


def test_db():
    print("TWO")
    from athena import get_db
    db = get_db()
    assert db == {}
    
    import athena.config
    print("DB PATH:", athena.config.DATABASE)
