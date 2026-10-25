# CI/CD — AI Build Challenge

## Модель работы

- `main`: утверждённые технические задания и опубликованные версии.
- `team/<project>`: разработка команды. Одна команда — одна папка `projects/<project>/`.
- Pull Request: обязательная проверка перед слиянием.
- `.github/workflows/ci.yml`: структура, unit tests, Chromium smoke test и ZIP-артефакт.
- `.github/workflows/pages.yml`: сборка общей галереи и публикация в GitHub Pages после push в `main`.

## Включение Pages (владелец репозитория)

Откройте **Settings → Pages → Build and deployment → Source: GitHub Actions**. Убедитесь, что Actions разрешены. Затем вручную запустите `Publish student gallery` или сделайте коммит в `main`.

Ожидаемый адрес: https://tozhievr.github.io/prompt-engeeniring-ithub/

## Рекомендуемые ограничения

В **Settings → Rules → Rulesets** создайте правило для `main`: pull request обязателен, минимум одно одобрение, CI checks `validate` и `browser-smoke` должны проходить. Не давайте студентам обходить правила. Учтите ограничения доступности rulesets/branch protection для публичного репозитория и плана GitHub.

## Как проверяется проект

Статическая проверка требует `index.html`, `README.md`, корректное имя папки, отсутствие package.json и слишком крупных файлов. Unit tests проверяют сам валидатор. Chromium smoke test открывает каждое опубликованное приложение, ждёт 2.5 секунды и фиксирует необработанные JS-ошибки. Это **не** функциональные тесты из ТЗ: команды должны добавить собственные проверки сценариев.

## Ограничения

- GitHub Pages — статический хостинг; он не выполняет Python или серверную SQLite.
- `sql.js` исполняется в браузере, а сохранение данных требует IndexedDB либо иного браузерного хранилища.
- Для ES-модулей и WASM используйте относительные URL, совместимые с подпутём `/prompt-engeeniring-ithub/projects/<slug>/`.
- Непроверенный код в PR запускается в CI. Workflow использует только `contents: read`, без секретов и без публикации из PR.
- Студенты не должны изменять `.github/workflows/` и `scripts/`; такие изменения преподаватель проверяет отдельно.
