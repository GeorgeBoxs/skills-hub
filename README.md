# skills-hub

Личный хаб Claude-скиллов: **единственный marketplace, который подключают все мои проекты**. Здесь живут собственные скиллы и курированные копии из апстрим-репозиториев. Merge в `main` = релиз для всех проектов (автообновление marketplace).

## Структура

```
.claude-plugin/marketplace.json   # манифест маркетплейса (6 плагинов, 44 скилла)
plugins/
  george-core/   # собственные скиллы (5)
  design/        # дизайн и UX (7)
  landing-cro/   # лендинги и конверсия (5)
  product/       # продукт (6)
  growth/        # рост и маркетинг (8)
  engineering/   # инженерия (13)
sources.lock                      # откуда и с какого SHA свендорены апстрим-скиллы
scripts/sync_upstream.py          # обновляет вендоренные копии по sources.lock
.github/workflows/sync-upstream.yml  # еженедельный синк → PR на ревью
```

## Как подключить в проект

В `.claude/settings.json` проекта (в шаблоне уже есть):

```json
{
  "extraKnownMarketplaces": {
    "skills-hub": {
      "source": { "source": "github", "repo": "GeorgeBoxs/skills-hub" }
    }
  },
  "enabledPlugins": [
    "george-core@skills-hub",
    "design@skills-hub",
    "landing-cro@skills-hub",
    "product@skills-hub",
    "growth@skills-hub",
    "engineering@skills-hub"
  ]
}
```

Затем один раз в проекте: `/plugin install george-core@skills-hub` (и остальные бандлы). Скиллы доступны как `george-core:ship-gate`, `engineering:database-designer` и т.д. Репо приватный — потребление работает через ваш локальный git/gh-доступ.

## Как это обновляется

- **Апстрим → хаб**: workflow `sync-upstream` (понедельник 06:00 UTC или вручную через *Run workflow*) клонирует апстримы из `sources.lock`, заменяет вендоренные копии, бампает SHA и открывает PR. Ревью диффа — единственное ручное действие. `SYNC_NOTES.md` в PR показывает предупреждения (например, скилл удалён апстримом).
- **Хаб → проекты**: ничего делать не нужно. Версии у плагинов намеренно не проставлены — Claude Code трекает их по git SHA, поэтому каждый merge в `main` автоматически доезжает до потребителей; форсировать можно командой `/plugin update`.

## Правила

- **Не редактировать** скиллы в `design/ landing-cro/ product/ growth/ engineering/` — их перезапишет синк. Нужна правка → либо убрать маппинг из `sources.lock` (скилл становится «своим»), либо контрибьютить в апстрим.
- Свои скиллы кладутся в `plugins/george-core/skills/<имя>/SKILL.md` (или новый плагин + запись в `marketplace.json`).
- Новый апстрим-источник = новая запись в `sources.lock` (repo, branch, sha, mappings).
- Репо-специфичные скиллы (типа `repo-conventions`) сюда **не** переносятся — они живут в `.claude/skills/` своих проектов.

## Лицензии

Вендоренные скиллы — MIT из [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills), см. `THIRD_PARTY_NOTICES.md` и точный пин в `sources.lock`.
