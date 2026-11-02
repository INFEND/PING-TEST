# PING TEST · Official Android OTA

Исходный Android-проект PING TEST 1.5.0 с автоматической сборкой APK в GitHub Actions.

## OTA

- Репозиторий: https://github.com/INFEND/PING-TEST
- APK: https://github.com/INFEND/PING-TEST/releases/latest/download/PING-TEST.apk
- Манифест: https://github.com/INFEND/PING-TEST/releases/latest/download/update.json
- Android ID: `com.xarkon.pingtest`
- Подпись закреплена в `UpdateManager.java`. Один раз создайте Actions Secret `PING_TEST_SIGNING_BUNDLE` из персонального файла, предоставленного владельцу отдельно.
- `push` в `main` или `Run workflow` запускает Gradle 9.6.1, затем `zipalign`, `apksigner`, генерацию манифеста и GitHub Release.
- Для каждого нового релиза повышайте `versionName` и `versionCode` в `app/build.gradle`.

Первое обновление с debug APK Code on the Go до официального release APK потребует резервной копии данных и удаления старой debug-версии: подписи несовместимы. Последующие официальные обновления устанавливаются поверх прежних.

Первая публикация невозможна без Actions Secret. Частный ключ никогда не публикуется в репозитории.
