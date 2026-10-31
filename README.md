# PING TEST · Android OTA

Официальный исходный репозиторий Android-приложения PING TEST.

## Первый импорт и подпись

1. В Settings → Secrets and variables → Actions создайте **Repository secret** `PING_TEST_SIGNING_BUNDLE`. Значение предоставлено владельцу в отдельном приватном файле и не должно публиковаться.
2. Загрузите в корень репозитория файл **PING_TEST_SOURCE.zip** (источник версии 1.5.0).
3. GitHub Actions автоматически распакует проект, добавит исходники в `main`, соберёт и подпишет APK, проверит сертификат и создаст GitHub Release.

После первой публикации исходники будут редактироваться напрямую в `app/`. Для новой версии обязательно увеличивайте `versionCode` и `versionName` в `app/build.gradle`.

## Адреса OTA

- APK: https://github.com/INFEND/PING-TEST/releases/latest/download/PING-TEST.apk
- Манифест: https://github.com/INFEND/PING-TEST/releases/latest/download/update.json
- Публикации: https://github.com/INFEND/PING-TEST/releases
- Автоматические сборки: https://github.com/INFEND/PING-TEST/actions

Первое обновление с APK, собранного в Code on the Go с debug-подписью, может потребовать удаления старого APK. Сохраните историю и настройки, если они важны: при удалении APK его локальные данные могут пропасть.

**Без секрета подписи выпуск релиза намеренно блокируется.** Приватный ключ не хранится в репозитории.
