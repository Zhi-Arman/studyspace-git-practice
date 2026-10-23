# Черновик матрицы прослеживаемости StudySpace

> Исторический черновик: DEC-018 от 2026-10-23 и [локальная версия](18_Local_Version.md) заменяют прежние ограничения реальной проверки вуза, домена/HTTPS и статуса каркаса. Остальные стабильные правила сохранены.


| Metadata | Value |
| --- | --- |
| Doc-ID | DOC-07 |
| Version | 0.4.0 |
| Status | DRAFT |
| Updated | 2026-10-23 |
| Language | ru-RU |

> Черновик инициализации: бизнес-требования ещё не прошли формальное рассмотрение и утверждение. Положения со статусом «проектное допущение» или «требует подтверждения» не являются согласованными требованиями. Документ не подтверждает проведение исследования пользователей, бизнес-тестирования или приёмки.

## 1 Границы прослеживаемости

Кандидаты происходят из ../data/requirements.json, планируемые тесты — из ../data/test-cases.json. Раздел проектирования обозначает целевое место; пустое implementation означает отсутствие связи с бизнес-реализацией. Все TC имеют NOT_RUN; связь не доказывает утверждение требования или прохождение теста.

## 2 Связи требований с проектированием, реализацией и тестами

<!-- GENERATED:BEGIN -->
| ID требования | Статус | Источник | Черновой проект | Реализация | Планируемые тест-кейсы | Статус тестов |
| --- | --- | --- | --- | --- | --- | --- |
| FR-001 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-003, DEC-007, DEC-013; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §3.1; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-001 | TC-001: NOT_RUN |
| FR-002 | PROPOSED | Задание курсового проекта; формальное рассмотрение требований не проведено. | [04_System_Design.md](04_System_Design.md) §3.1; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-002 | TC-002: NOT_RUN |
| FR-003 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-003, DEC-013; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §3.1; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-003 | TC-003: NOT_RUN |
| FR-004 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-002, DEC-011; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §3.2; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-004 | TC-004: NOT_RUN |
| FR-005 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-005, DEC-006; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §3.2; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-005 | TC-005: NOT_RUN |
| FR-006 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-002, DEC-005; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §3.2; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-006 | TC-006: NOT_RUN |
| FR-007 | PROPOSED | Задание и явная последующая поправка пользователя; DEC-016 заменяет общий лимит взаимным исключением времени, всяSRS ещё рассматривается. | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-007 | TC-007: NOT_RUN |
| FR-008 | PROPOSED | Задание и явная последующая поправка пользователя; DEC-016 заменяет общий лимит взаимным исключением времени, всяSRS ещё рассматривается. | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-008 | TC-008: NOT_RUN |
| FR-009 | PROPOSED | Задание и явная последующая поправка пользователя; DEC-016 заменяет общий лимит взаимным исключением времени, всяSRS ещё рассматривается. | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-009 | TC-009: NOT_RUN |
| FR-010 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-007; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-010 | TC-010: NOT_RUN |
| FR-011 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-002, DEC-011; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §3.4; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-011 | TC-011: NOT_RUN |
| FR-012 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-005; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §3.4; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-012 | TC-012: NOT_RUN |
| FR-013 | PROPOSED | Задание и явная последующая поправка пользователя; DEC-016 заменяет общий лимит взаимным исключением времени, всяSRS ещё рассматривается. | [04_System_Design.md](04_System_Design.md) §3.4; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-013 | TC-013: NOT_RUN |
| FR-014 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-007, DEC-011; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §3.4; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-014 | TC-014: NOT_RUN |
| FR-015 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-003, DEC-007, DEC-013; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §3.4; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-015 | TC-015: NOT_RUN |
| FR-016 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-012; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §3.4; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-016 | TC-016: NOT_RUN |
| FR-017 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-002, DEC-011; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §3.2; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-017 | TC-017: NOT_RUN |
| FR-018 | PROPOSED | Задание курсового проекта; формальное рассмотрение требований не проведено. | [04_System_Design.md](04_System_Design.md) §3.5 | Не реализовано | TC-018 | TC-018: NOT_RUN |
| FR-019 | PROPOSED | Задание курсового проекта; формальное рассмотрение требований не проведено. | [04_System_Design.md](04_System_Design.md) §3.5 | Не реализовано | TC-019 | TC-019: NOT_RUN |
| FR-020 | PROPOSED | Задание курсового проекта; формальное рассмотрение требований не проведено. | [04_System_Design.md](04_System_Design.md) §3.5 | Не реализовано | TC-020 | TC-020: NOT_RUN |
| FR-021 | PROPOSED | Задание курсового проекта; формальное рассмотрение требований не проведено. | [04_System_Design.md](04_System_Design.md) §3.5 | Не реализовано | TC-021 | TC-021: NOT_RUN |
| NFR-001 | PROPOSED | Задание курсового проекта; формальное рассмотрение требований не проведено. | [04_System_Design.md](04_System_Design.md) §7; [18_Local_Version.md](18_Local_Version.md) §5 | backend/app/main.py; frontend/src/App.tsx | TC-022 | TC-022: NOT_RUN |
| NFR-002 | PROPOSED | Задание курсового проекта; формальное рассмотрение требований не проведено. | [04_System_Design.md](04_System_Design.md) §7; [18_Local_Version.md](18_Local_Version.md) §5 | backend/app/main.py; frontend/src/App.tsx | TC-023 | TC-023: NOT_RUN |
| NFR-003 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-003, DEC-007, DEC-013; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §6; [18_Local_Version.md](18_Local_Version.md) §5 | backend/app/main.py; frontend/src/App.tsx | TC-024 | TC-024: NOT_RUN |
| NFR-004 | PROPOSED | Задание и явная последующая поправка пользователя; DEC-016 заменяет общий лимит взаимным исключением времени, всяSRS ещё рассматривается. | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §5 | backend/app/main.py; frontend/src/App.tsx | TC-025 | TC-025: NOT_RUN |
| NFR-005 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-015; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §4; [18_Local_Version.md](18_Local_Version.md) §5 | backend/app/main.py; frontend/src/App.tsx | TC-026 | TC-026: NOT_RUN |
| NFR-006 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-009; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §7; [18_Local_Version.md](18_Local_Version.md) §5 | backend/app/main.py; frontend/src/App.tsx | TC-027 | TC-027: NOT_RUN |
| NFR-007 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-007; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §6; [18_Local_Version.md](18_Local_Version.md) §5 | backend/app/main.py; frontend/src/App.tsx | TC-028 | TC-028: NOT_RUN |
| NFR-008 | PROPOSED | Задание курсового проекта; формальное рассмотрение требований не проведено. | [04_System_Design.md](04_System_Design.md) §7; [18_Local_Version.md](18_Local_Version.md) §5 | backend/app/main.py; frontend/src/App.tsx | TC-029 | TC-029: NOT_RUN |
| BR-001 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-004, DEC-005, DEC-006; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-030 | TC-030: NOT_RUN |
| BR-002 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-002, DEC-005; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-031 | TC-031: NOT_RUN |
| BR-003 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-004, DEC-005; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-032 | TC-032: NOT_RUN |
| BR-004 | PROPOSED | Задание и явная последующая поправка пользователя; DEC-016 заменяет общий лимит взаимным исключением времени, всяSRS ещё рассматривается. | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-033 | TC-033: NOT_RUN |
| BR-005 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-005, DEC-013; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-034 | TC-034: NOT_RUN |
| BR-006 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-003, DEC-007, DEC-013; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §3.1; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-035 | TC-035: NOT_RUN |
| BR-007 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-005, DEC-007, DEC-011; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §3.4; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-036 | TC-036: NOT_RUN |
| BR-008 | PROPOSED | Исходное задание и уточнения/делегированные решения от2026-10-12 DEC-005, DEC-006; вся SRS ещё не рассмотрена официально. | [04_System_Design.md](04_System_Design.md) §5; [18_Local_Version.md](18_Local_Version.md) §3 | backend/app/main.py; frontend/src/App.tsx | TC-037 | TC-037: NOT_RUN |
| FR-022 | RETIRED | Пользователь от2026-10-12 требует проверку вуза; DEC-003 и DEC-013; вся SRS не утверждена. | [04_System_Design.md](04_System_Design.md) §3.1 | Не реализовано | TC-038 | TC-038: RETIRED |
<!-- GENERATED:END -->

## 3 Двустороннее сопровождение

После реализации указать реальные файлы и необходимые символы, добавить исполняемые тесты и доказательства; проверить совпадение requirement_ids тестов и test_cases требований. Проверки здоровья не отображаются как пройденные бизнес-TC. Снятые требования сохраняют ID и причину; повторное использование запрещено.

## 4 Запись рассмотрения

Первое рассмотрение требований, полноты связей и бизнес-тестирование не выполнены; ответственные, даты и решения предстоит заполнить.
