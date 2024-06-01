import pytest


def test_imports():
    from calmmage_feature_bot.handler import ShowcaseHandler
    from calmmage_feature_bot.app import ShowcaseApp

    assert ShowcaseHandler
    assert ShowcaseApp
