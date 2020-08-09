import sqlite3
from sqlite3 import Error
import os
import sys


class SimpleTM:
    def __init__(self,sSqliteFileName):
        self.__sSqliteFileName=sSqliteFileName
        isExist=os.path.isfile(sSqliteFileName)
        if(isExist==False):
            self.__InitSQLite(self.__sSqliteFileName)
        try:
            self.__conn=sqlite3.connect(self.__sSqliteFileName)
        except Error as e:
            raise RuntimeError(e)
    def __InitSQLite(self,sSqliteFileName):
        try:
            self.__conn=sqlite3.connect(self.__sSqliteFileName)
            c=self.__conn.cursor()
            c.execute('''
            CREATE TABLE SimpleTM
            (
                GameTitle text,
                RawWord text,
                TranslatedWord text,
                unique (GameTitle,RawWord) 
            )
            ''')
            self.__conn.commit()
            self.__conn.close()
        except Error as e:
            raise RuntimeError(e)
    def Query(self,sRawWord):
        try:
            c=self.__conn.cursor()
            c.execute('''
            select RawWord,TranslatedWord,GameTitle
            from SimpleTM
            where instr(?,RawWord) > 0
            ''',(sRawWord.lower(),))
            self.__conn.commit()
            rows=c.fetchall()
            return rows
        except Error as e:
            raise RuntimeError(e)

    def QueryAll(self, game):
        try:
            c=self.__conn.cursor()
            c.execute('''
            select RawWord,TranslatedWord,GameTitle
            from SimpleTM
            where instr(?,GameTitle) > 0
            ''',(game.lower(),))
            self.__conn.commit()
            rows=c.fetchall()
            return rows
        except Error as e:
            raise RuntimeError(e)

    def Insert(self,sRawWord,sTranslatedWord,sGameTitle):
        try:
            c=self.__conn.cursor()
            c.execute('''
            insert into SimpleTM(GameTitle,RawWord,TranslatedWord)
            values (?,?,?)
            ''', (sGameTitle.lower(),sRawWord.lower(),sTranslatedWord.lower()))
            if c.rowcount < 1:
                self.__conn.rollback()
                return False
            else:
                self.__conn.commit()
                return True
        except Error as e:
            raise RuntimeError(e)
    def Update(self,sRawWord,sTranslatedWord,sGameTitle):
        try:
            c=self.__conn.cursor()
            c.execute('''
            update SimpleTM
            set TranslatedWord=?
            where GameTitle=? and RawWord=?
            ''', (sTranslatedWord.lower(),sGameTitle.lower(),sRawWord.lower()))
            if c.rowcount < 1:
                self.__conn.rollback()
                return False
            else:
                self.__conn.commit()
                return True
        except Error as e:
            raise RuntimeError(e)
    def Close(self):
        self.__conn.close()
if __name__ == "__main__":
#SimpleTest
    objSimpleTM=SimpleTM('SimpleTM.db')
    print(objSimpleTM.Insert('Test','测试','TestGame1'))
    print(objSimpleTM.Insert('Argument','理由','TestGame1'))
    print(objSimpleTM.Insert('Test','测验','TestGame2'))
    try:
        print(objSimpleTM.Insert('Test','测试','TestGame1'))
    except Exception as e:
        print(e)
    print(objSimpleTM.Update('Test','测试2','TestGame1'))
    print(objSimpleTM.Update('Test','测试3','TestGame1'))
    print(objSimpleTM.QueryAll('TestGame1'))
    print(objSimpleTM.Query('reason'))