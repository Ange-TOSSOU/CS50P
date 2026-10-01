from jar import Jar

# pip install pytest
import pytest


def test_init_with_negative_capacity():
    with pytest.raises(ValueError):
        Jar(-2)


def test_init_with_no_capacity():
    jar = Jar(0)
    assert jar.capacity == 0


def test_init():
    jar = Jar(10)
    assert jar.capacity == 10
    assert jar.size == 0


def test_init_with_default_capacity():
    jar = Jar()
    assert jar.capacity == 12


def test_deposit():
    jar = Jar(3)
    jar.deposit(2)
    assert jar.size == 2


def test_deposit_with_excedeed_capacity():
    jar = Jar(3)
    with pytest.raises(ValueError):
        jar.deposit(5)


def test_deposit_with_reached_capacity():
    jar = Jar(3)
    jar.deposit(3)
    assert jar.size == 3


def test_deposit_nothing():
    jar = Jar(3)
    jar.deposit(0)
    assert jar.size == 0


def test_deposit_with_negative_n():
    jar = Jar()
    with pytest.raises(ValueError):
        jar.deposit(-2)


def test_withdraw():
    jar = Jar(3)
    jar.deposit(3)
    jar.withdraw(2)
    assert jar.size == 1


def test_withdraw_with_insufficient_size():
    jar = Jar(3)
    with pytest.raises(ValueError):
        jar.withdraw(5)


def test_withdraw_all():
    jar = Jar()
    jar.deposit(3)
    jar.withdraw(3)
    assert jar.size == 0


def test_withdraw_nothing():
    jar = Jar(3)
    jar.withdraw(0)
    assert jar.size == 0


def test_withdraw_with_negative_n():
    jar = Jar()
    with pytest.raises(ValueError):
        jar.withdraw(-2)


def test_str():
    jar = Jar()
    jar.deposit(3)
    assert str(jar) == "🍪🍪🍪"


def test_str_with_nothing():
    jar = Jar()
    assert str(jar) == ""
