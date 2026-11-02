# PING TEST · Android OTA

Официальный исходный Android-проект: `com.xarkon.pingtest`.

## OTA, перенесённое из QR LINK

- Встроенное AMOLED-окно OTA с анимированным кольцом, прогрессом загрузки и накопительным changelog.
- Установка APK в приложении через системный установщик Android, без веб-браузера.
- Проверки перед установкой: официальный HTTPS-канал, версия, packageName, размер, SHA-256 и закреплённый сертификат подписи.
- Проверка обновлений при запуске (по желанию), фоновые проверки (по желанию), интервалы 1/3/6/12/24 ч, 3/7 дней, уведомление о новой версии.
- Исходники в `app/`, версия в `app/build.gradle`, тексты изменений в `release_notes/v<version>.txt`, индексация версий в `release_notes/versions.json`.
- Релиз автоматически собирается из `main`. Для каждой новой версии необходимо увеличить `versionCode` и `versionName`.

## Постоянные адреса

- APK: https://github.com/INFEND/PING-TEST/releases/latest/download/PING-TEST.apk
- OTA JSON: https://github.com/INFEND/PING-TEST/releases/latest/download/update.json
- Сборки: https://github.com/INFEND/PING-TEST/actions
- Релизы: https://github.com/INFEND/PING-TEST/releases

## Подпись первого официального APK

Для GitHub Actions необходим секрет `PING_TEST_SIGNING_BUNDLE`, содержащий **одной строкой полное Base64-представление JSON** с `keystoreBase64`, `storePassword`, `keyAlias`, `keyPassword`, `certSha256`. Секрет хранится только в GitHub Actions, не публикуется в исходниках.

Если Actions сообщает `Invalid signing bundle: Error`, значение секрета повреждено или неверно скопировано. Его нужно обновить значением из ранее выданного приватного файла подписи. Нельзя заменять уже используемый сертификат новым, иначе OTA перестанет устанавливаться поверх старого приложения.

Первая установка официального APK поверх debug-сборки из Code on the Go, вероятно, потребует удаления debug-версии из-за другой подписи. Сохраните нужную историю заранее.

**Статус APK определяется GitHub Actions и Releases, а не наличием исходников.**
