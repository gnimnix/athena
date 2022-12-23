from subprocess import getstatusoutput


def test_bot():
    rv, out = getstatusoutput(f"python -m athena run")
    assert rv == 0
