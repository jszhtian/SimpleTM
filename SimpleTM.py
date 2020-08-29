import sqlite3
from sqlite3 import Error
import os
import sys


class SimpleTM:
    def __init__(self,sSqliteFileName):
        self.__sSqliteFileName=sSqliteFileName
        isExist=os.path.isfile(sSqliteFileName)
        if(isExist==False):
            self.__InitSQLite()
        try:
            self.__conn=sqlite3.connect(self.__sSqliteFileName)
        except Error as e:
            raise RuntimeError(e)
    def __InitSQLite(self):
        try:
            self.__conn=sqlite3.connect(self.__sSqliteFileName)
            c = self.__conn.cursor()
            f = open('init_db.sql', encoding='utf-8')
            statements = f.read().split(';')
            for s in statements:
                #print(s)
                c.execute(s)
            self.__conn.commit()
            self.__conn.close()
        except Error as e:
            raise RuntimeError(e)
    def __GetCursor(self):
            c = self.__conn.cursor()
            c.execute('PRAGMA foreign_keys = ON')
            return c
    def Query(self, game, raw):
        try:
            c = self.__GetCursor()
            c.execute('''
                SELECT raw_word, trans_word
                FROM Translate
                WHERE game_id=? AND raw_word=?''',
                (game, raw,))
            self.__conn.commit()
            rows=c.fetchall()
            return rows
        except Error as e:
            raise RuntimeError(e)

    def QueryByGame(self,game):
        try:
            c = self.__GetCursor()
            c.execute('''
                SELECT raw_word, trans_word
                FROM Translate
                WHERE game_id=?''',
                (game,))
            self.__conn.commit()
            rows=c.fetchall()
            return rows
        except Error as e:
            raise RuntimeError(e)
    def QueryGame(self):
        try:
            c = self.__GetCursor()
            c.execute('''
            SELECT * FROM Game
            ''')
            self.__conn.commit()
            rows=c.fetchall()
            return rows
        except Error as e:
            raise RuntimeError(e)

    def __Insert(self, sql, c, *args):
        commit = c is None
        if commit:
            c = self.__GetCursor()
        c.execute(sql, args)
        if c.rowcount < 1:
            self.__conn.rollback()
            return False
        else:
            if commit:
                self.__conn.commit()
            return True

    def AddTranslation(self, sRawWord, sTranslatedWord, sGameID):
        return self.__Insert(
                '''
                INSERT INTO Translate(game_id,raw_word,trans_word)
                VALUES (?,?,?)
                ''', None,
                sGameID, sRawWord, sTranslatedWord
            )
    
    def UpdateTranslation(self,sRawWord, sTranslatedWord, game_id):
        c = self.__GetCursor()
        c.execute('''
            UPDATE Translate
            SET trans_word=?
            WHERE game_id=? AND raw_word=?''',
            (sTranslatedWord, game_id, sRawWord)
        )
        if c.rowcount < 1:
            self.__conn.rollback()
            return False
        else:
            self.__conn.commit()
            return True

    def UpdatePermission(self, user_id, game_id, permission, c=None):
        commit = c is None
        if commit:
            c = self.__GetCursor()
        c.execute('SELECT * FROM Permission WHERE user_id=? AND game_id=?', (user_id, game_id))
        rows = c.fetchall()
        if len(rows) == 0:
            c.execute('INSERT INTO Permission VALUES (?,?,?)', (user_id, game_id, permission))
        else:
            c.execute('''
                UPDATE Permission SET permission=?
                WHERE user_id=? AND game_id=?''',
                (permission, user_id, game_id)
            )
        if c.rowcount < 1:
            self.__conn.rollback()
            return False
        else:
            if commit:
                self.__conn.commit()
            return True

    def getPermission(self, uid, gid):
        c = self.__GetCursor()
        c.execute('SELECT permission FROM Permission WHERE user_id=? AND game_id=?', (uid, gid))
        row = c.fetchone()
        if not row:
            return 0
        return row[0]

    def AddUser(self, user, salt, token):
        return self.__Insert('INSERT INTO User VALUES (?, ?)', None, user, salt) \
            and self.__Insert('INSERT INTO APIToken VALUES (?, ?)', None, user, token)

    def UpdateToken(self, user, token):
        c = self.__GetCursor()
        c.execute('UPDATE APIToken SET token=? WHERE user_id=?', (token, user))
        if c.rowcount < 1:
            self.__conn.rollback()
            return False
        else:
            self.__conn.commit()
            return True

    def QueryUser(self, user):
        c = self.__GetCursor()
        c.execute('SELECT * FROM User WHERE id=?', (user,))
        return c.fetchone()

    def GetUserAPIToken(self, user):
        c = self.__GetCursor()
        c.execute('SELECT token FROM APIToken WHERE user_id=?', (user,))
        return c.fetchall()

    def AddGame(self, game_id, game_title):
        return self.__Insert('INSERT INTO Game VALUES (?, ?)', None, game_id, game_title)

    def AddGameAsUser(self, uid, gid, gtitle):
        c = self.__GetCursor()
        assert self.__Insert('INSERT INTO Game VALUES (?, ?)', c, gid, gtitle)
        assert self.UpdatePermission(uid, gid, 3, c)
        self.__conn.commit()

    def DeleteGame(self, game_id):
        c = self.__GetCursor()
        c.execute('DELETE FROM Game WHERE id=?', (game_id,))
        self.__conn.commit()
        

    def GetUser(self, username):
        c = self.__GetCursor()
        c.execute('SELECT * from USER where id=?', (username,))
        return c.fetchone()

    def GetGamesByUser(self, username):
        c = self.__GetCursor()
        c.execute('''
            SELECT p.user_id, p.game_id, g.title, p.permission from Permission AS p 
            JOIN User AS u ON p.user_id=u.id
            JOIN Game AS g ON p.game_id=g.id
            WHERE p.user_id=?
        ''', (username,))
        result = []
        rows = c.fetchall()
        perm_map = ['无','只读','读写','管理员']
        for uid, gid, gtitle, perm in rows:
            result.append({
                'user_id': uid,
                'game_id': gid,
                'game_title': gtitle,
                "permission": perm_map[perm]
            })
        return result


    
    def Close(self):
        self.__conn.close()
    
if __name__ == "__main__":
    #SimpleTest
    db = SimpleTM('SimpleTM.db') 
    assert db.AddTranslation('Test','测试','imoyaba')
    print(db.QueryByGame('imoyaba'))
    print(db.Query('imoyaba', 'Test'))
    assert db.UpdateTranslation('Test','测试2','imoyaba')
    assert db.UpdateTranslation('Test','测试3','imoyaba')
    assert db.UpdateTranslation('Test2','测试a','imoyaba')
    assert db.UpdateTranslation('Test2','测试b','imoyaba')
    print(db.QueryByGame('imoyaba'))
    try:
        print(db.AddTranslation('Test','测试','imoyaba'))
    except Exception as e:
        print(e)
    try:
        print(db.AddTranslation('Test','测试','test_game'))
    except Exception as e:
        print(e)
    assert db.AddUser('test_user', 'test_salt')
    assert db.AddGame('test_game', 'test_title')
    assert db.AddTranslation('Test','测试','test_game')
    print(db.QueryGame())
    print(db.QueryByGame('test_game'))