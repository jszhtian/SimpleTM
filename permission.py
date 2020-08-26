from config import Config
import flask_login
from SimpleTM import SimpleTM
import functools

class Permission:
    NONE = 0
    READ = 1
    EDIT = 2
    ADMIN = 3

def must_has_permission(user, game, level):
    db = SimpleTM(Config.dbFileName)
    perm = db.getPermission(user, game)
    if perm < level:
        raise Exception("Permission Denied")

