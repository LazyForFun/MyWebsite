# Introduction
本專案為個人早期網頁開發專案，主要目的是建置一個依據使用者身分提供不同功能的系統。由於為首次進行完整系統開發，在實作過程中逐步體會資料庫設計對系統可維護性與擴充性的影響，亦累積了實務上的設計經驗。

此網站依使用者角色提供對應功能：

-學士生：上傳證照與專題報告書供系所審核

-碩士生（含在職碩士）：上傳論文計畫書、學位考試相關資料、論文與取消申請表

-管理員（系助教、系辦人員）：審核學生繳交資料，並處理書籍借閱申請確認

專案過程中負責前後端整合、資料庫設計與功能實作，並透過實際開發理解系統需求分析與資料結構設計的重要性。

knowledge required: python, django, html, TypeScript, sql(sqlite3)

# Enviroment setup
    -install virtualenv >> pip install virtualenv
    -build virtual enviroment >> virtualenv your_env_name
    -install requirments in virtual enviroment
     
    -activate virtual enviroment >> your_env_name\Scripts\activate

# Activate website
    -python manage.py runserver
