# Introduction
這個網頁的資料庫設計得非常爛，在做的途中才發現超爛，因為這是我的第一個專案，先前無任何設計經驗，而且資料庫的授課教授... 懂得都懂。
此網站根據使用者身分提供不同功能:
-學士: 繳交證照、專題報告書以供審核
-碩士(包含在職碩士): 繳交論文計畫書、學位考試相關資料、論文、取消申請表
-管理員(系助教、系辦pt): 審核學生繳交之資料、確認書籍借閱申請

knowledge required: python, html, tag language, sql(sqlite3)

# Enviroment setup
    -install virtualenv >> pip install virtualenv
    -build virtual enviroment >> virtualenv your_env_name
    -install requirments in virtual enviroment
     
    -activate virtual enviroment >> your_env_name\Scripts\activate

# Activate website
    -python manage.py runserver