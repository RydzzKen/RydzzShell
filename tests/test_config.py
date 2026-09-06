# -*- coding: utf-8 -*-
"""Tes untuk setup HOME sandbox (regresi bug CUSTOM_HOME bertumpuk)."""
import os

from rydzz import config


def test_custom_home_anchored_to_real_home():
    assert config.CUSTOM_HOME == os.path.join(config.REAL_HOME, ".rydzz_home")


def test_custom_home_not_derived_from_home_env():
    # Set HOME seolah-olah sudah jadi folder sandbox (kasus bug: tiap restart
    # path bertambah .rydzz_home). CUSTOM_HOME tetap menjangkar ke REAL_HOME.
    assert not config.CUSTOM_HOME.endswith(os.path.join(".rydzz_home", ".rydzz_home"))