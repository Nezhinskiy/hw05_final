# **hw05_final**
### **Описание**
Социальная сеть блогеров. **Учебный проект**.

Сообщество для публикаций. Блог с возможностью публикации постов, подпиской на группы и авторов, а также комментированием постов.

### **Стек технологий**
- Python 3.9
- Django framework 2.2.16
- HTML
- CSS (Bootstrap 3)
- Djangorestframework-simplejwt 4.7.2
- Pillow 8.3.1
- sorl-thumbnail 12.7.0

### **Запуск проекта в dev-режиме**
Инструкция ориентирована на операционную систему windows и утилиту git bash.<br/>
Для прочих инструментов используйте аналоги команд для вашего окружения.

1. Клонируйте репозиторий и перейдите в него в командной строке:

```
git clone https://github.com/Nezhinskiy/hw05_final.git
```

```
cd hw05_final
```

2. Установите и активируйте виртуальное окружение
```
python -m venv venv
``` 
```
source venv/Scripts/activate
```

3. Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
```

4. В папке с файлом manage.py выполните миграции:
```
python manage.py migrate
```

5. В папке с файлом manage.py запустите сервер, выполнив команду:
```
python manage.py runserver
```

### *Что могут делать пользователи*:

**Залогиненные** пользователи могут:
1. Просматривать, публиковать, удалять и редактировать свои публикации;
2. Просматривать информацию о сообществах;
3. Просматривать и публиковать комментарии от своего имени к публикациям других пользователей *(включая самого себя)*, удалять и редактировать **свои** комментарии;
4. Подписываться на других пользователей и просматривать **свои** подписки.<br/>
***Примечание***: Доступ ко всем операциям записи, обновления и удаления доступны только после аутентификации и получения токена.

**Анонимные** пользователи могут:
1. Просматривать публикации;
2. Просматривать информацию о сообществах;
3. Просматривать комментарии;

### **Набор доступных эндпоинтов**:
* ```posts/``` - Отображение постов и публикаций (_GET, POST_);
* ```posts/{id}``` - Получение, изменение, удаление поста с соответствующим **id** (_GET, PUT, PATCH, DELETE_);
* ```posts/{post_id}/comments/``` - Получение комментариев к посту с соответствующим **post_id** и публикация новых комментариев(_GET, POST_);
* ```posts/{post_id}/comments/{id}``` - Получение, изменение, удаление комментария с соответствующим **id** к посту с соответствующим **post_id** (_GET, PUT, PATCH, DELETE_);
* ```posts/groups/``` - Получение описания зарегестрированных сообществ (_GET_);
* ```posts/groups/{id}/``` - Получение описания сообщества с соответствующим **id** (_GET_);
* ```posts/follow/``` - Получение информации о подписках текущего пользователя, создание новой подписки на пользователя (_GET, POST_).<br/>
