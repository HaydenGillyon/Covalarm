"""This module tests one of the functions from the Covalarm program.

It exports the following test function:
test_close_notif
"""
import covalarm
from covalarm import close_notif

def test_close_notif():
    covalarm.notifications = [
        {'title' : 'Test1'},
        {'title' : 'Test2'},
        {'title' : 'Test3'}
    ]
    close_notif('Test2')
    assert covalarm.notifications == [
        {'title' : 'Test1'},
        {'title' : 'Test3'}
    ]

if __name__ == '__main__':
    test_close_notif()