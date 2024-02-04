# HearthTrice Manager
Менеджер для создания пользовательских Hearthstone карт для симулятора карточных настольных игр [Cockatrice](https://cockatrice.github.io/).
Платформа: Windows 10.

### Зависимости
###### Для корректной работы клиента необходимо установить следующие компоненты:
Отрисовка текста: [ImageMagick-7.1.1.](Dependencies/ImageMagick-7.1.1-27-Q16-HDRI-x64-dll.exe)
Драйвер связи с сервером: [SQL Server Native Client 11.0.](Dependencies/sqlncli.msi)  (опционально, для поддержки хранилища).


Для связи клиента с сервером предполагается нахождения устройств в одной виртуальной локальной сети ([Radmin](https://www.radmin-vpn.com/), [Hamachi](https://vpn.net/)).

### Как пользоваться
Генерация изображений карт:
1. Перейти в модуль редактора карт.
2. Заполнить метаданные
3. Импортировать изображение локально, перетянув его в поле превью, или из буфера обмена нажав по превью и вставив с помощью CTRL+V.
4. Сохранить как... (локально)
4.1. Загрузить в библиотеку (при поддержке хранилища)

Выгрузка изображений и .xml метаданных для Cockatrice:
1. Указать в настройках корневую директорию Cockatrice.
2. Перейти в модуль библиотеки.
3. Экспорт библиотеки.

## Сборка
### Получение стандартных Hearthstone карт (опционально)
Изображения и метаданные для стандартных карт компилируются в ресурсный файл и хранятся вместе с клиентом. Чтобы скачать стандартную коллекцию в библиотеку приложения, необходимо получить API ключ сервиса [RapidAPI Hearthstone by omgvamp](https://rapidapi.com/omgvamp/api/hearthstone) и воспользоваться скриптом src/utils/get_standard_cards.py.
Скрипт необходимо дополнить личным API ключем и названиями сетов для скачивания (Classic, Naxxramas, и т.д.). После этого необходимо сгенерировать ресурсный файл.
### Генерация ресурсов

Основные ресурсные компоненты: 
```sh 
pyrcc5 src\assets\resource_list.qrc -o src\resources.py
```
Ресурсы стандартной коллекции (необходимо даже при отсутствии стандартных карт).
```sh
pyrcc5 src\assets\resource_list_std.qrc -o src\resources_std.py
```

### Компиляция 
```sh
python build.py
cd dist\
```

## Для сервера
Для хранения карт и колод используется MS SQL Server. 

На устройстве, держащим базу данных, необходимо открыть порт 1433 для входящих запросов. 
Для Windows 10:
Брандмауэр Защитника Windows -> Дополнительные параметры -> Правила для входящих подключений -> Создать правило -> Для порта TCP или UDP -> Протокол TCP, Порт 1433 -> Разрешить безопасное подключение.