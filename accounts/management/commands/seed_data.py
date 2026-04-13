"""
Management-команда seed_data — заполнение БД тестовыми данными.

Создаёт:
    - Пользователей: admin@test.com, editor@test.com, viewer@test.com, guest@test.com
    - Ресурсы: documents, reports, tasks
    - Действия: create, read, update, delete
    - Роли: admin, editor, viewer
    - Разрешения (полный набор для каждой роли)
    - Назначения ролей пользователям

Пароль всех тестовых пользователей: TestPass123!
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

from accounts.models import CustomUser
from rbac.models import Resource, Action, Role, Permission, UserRole


class Command(BaseCommand):
    help = "Заполняет БД тестовыми данными для демонстрации системы RBAC."

    def handle(self, *args, **options):
        self.stdout.write("Начинаем заполнение тестовыми данными...\n")

        # ── Пользователи ────────────────────────────────────────
        users_data = [
            {
                "email": "admin@test.com",
                "first_name": "Админ",
                "last_name": "Админов",
                "patronymic": "Админович",
                "role_codename": "admin",
            },
            {
                "email": "editor@test.com",
                "first_name": "Редактор",
                "last_name": "Редакторов",
                "patronymic": "Редакторович",
                "role_codename": "editor",
            },
            {
                "email": "viewer@test.com",
                "first_name": "Читатель",
                "last_name": "Читателей",
                "patronymic": "",
                "role_codename": "viewer",
            },
            {
                "email": "guest@test.com",
                "first_name": "Гость",
                "last_name": "Гостев",
                "patronymic": "",
                "role_codename": None,
            },
        ]

        users = {}
        for ud in users_data:
            user, created = CustomUser.objects.get_or_create(
                email=ud["email"],
                defaults={
                    "first_name": ud["first_name"],
                    "last_name": ud["last_name"],
                    "patronymic": ud["patronymic"],
                    "password": make_password("TestPass123!"),
                    "is_active": True,
                },
            )
            users[ud["role_codename"] or "guest"] = user
            status_msg = "создан" if created else "уже существует"
            self.stdout.write(f"  Пользователь {ud['email']} — {status_msg}")

        # ── Ресурсы ────────────────────────────────────────────
        resources_data = [
            {"codename": "documents", "name": "Документы", "description": "Управление документами организации"},
            {"codename": "reports", "name": "Отчёты", "description": "Просмотр и формирование отчётов"},
            {"codename": "tasks", "name": "Задачи", "description": "Управление задачами сотрудников"},
        ]
        resources = {}
        for rd in resources_data:
            res, created = Resource.objects.get_or_create(
                codename=rd["codename"],
                defaults={"name": rd["name"], "description": rd["description"]},
            )
            resources[rd["codename"]] = res
            status_msg = "создан" if created else "уже существует"
            self.stdout.write(f"  Ресурс {rd['codename']} — {status_msg}")

        # ── Действия ────────────────────────────────────────────
        actions_data = [
            {"codename": "create", "name": "Создание"},
            {"codename": "read", "name": "Чтение"},
            {"codename": "update", "name": "Обновление"},
            {"codename": "delete", "name": "Удаление"},
        ]
        actions = {}
        for ad in actions_data:
            act, created = Action.objects.get_or_create(
                codename=ad["codename"],
                defaults={"name": ad["name"]},
            )
            actions[ad["codename"]] = act
            status_msg = "создано" if created else "уже существует"
            self.stdout.write(f"  Действие {ad['codename']} — {status_msg}")

        # ── Роли ────────────────────────────────────────────────
        roles_data = [
            {
                "codename": "admin",
                "name": "Администратор",
                "description": "Полный доступ ко всем ресурсам и действиям, управление RBAC",
            },
            {
                "codename": "editor",
                "name": "Редактор",
                "description": "Чтение, создание и обновление документов и задач; чтение отчётов",
            },
            {
                "codename": "viewer",
                "name": "Читатель",
                "description": "Только чтение документов, отчётов и задач",
            },
        ]
        roles = {}
        for rld in roles_data:
            role, created = Role.objects.get_or_create(
                codename=rld["codename"],
                defaults={"name": rld["name"], "description": rld["description"]},
            )
            roles[rld["codename"]] = role
            status_msg = "создана" if created else "уже существует"
            self.stdout.write(f"  Роль {rld['codename']} — {status_msg}")

        # ── Разрешения ──────────────────────────────────────────
        # admin: все действия на все ресурсы
        admin_perms_created = 0
        for res_codename, res in resources.items():
            for act_codename, act in actions.items():
                _, created = Permission.objects.get_or_create(
                    role=roles["admin"],
                    resource=res,
                    action=act,
                )
                admin_perms_created += 1 if created else 0

        # editor: create/read/update на documents и tasks; read на reports
        editor_perms = [
            ("documents", "create"),
            ("documents", "read"),
            ("documents", "update"),
            ("reports", "read"),
            ("tasks", "create"),
            ("tasks", "read"),
            ("tasks", "update"),
        ]
        editor_perms_created = 0
        for res_cn, act_cn in editor_perms:
            _, created = Permission.objects.get_or_create(
                role=roles["editor"],
                resource=resources[res_cn],
                action=actions[act_cn],
            )
            editor_perms_created += 1 if created else 0

        # viewer: read на все ресурсы
        viewer_perms_created = 0
        for res_codename, res in resources.items():
            _, created = Permission.objects.get_or_create(
                role=roles["viewer"],
                resource=res,
                action=actions["read"],
            )
            viewer_perms_created += 1 if created else 0

        self.stdout.write(
            f"  Разрешения: admin={admin_perms_created}, "
            f"editor={editor_perms_created}, viewer={viewer_perms_created}"
        )

        # ── Назначения ролей ───────────────────────────────────
        assignments = [
            (users["admin"], roles["admin"]),
            (users["editor"], roles["editor"]),
            (users["viewer"], roles["viewer"]),
        ]
        for user, role in assignments:
            ur, created = UserRole.objects.get_or_create(user=user, role=role)
            status_msg = "назначена" if created else "уже назначена"
            self.stdout.write(f"  Роль {role.codename} пользователю {user.email} — {status_msg}")

        self.stdout.write(self.style.SUCCESS("\nЗаполнение тестовыми данными завершено!"))
        self.stdout.write("\nТестовые учётные данные:")
        self.stdout.write("  admin@test.com  / TestPass123!  — Администратор (полный доступ)")
        self.stdout.write("  editor@test.com / TestPass123!  — Редактор (создание/чтение/обновление)")
        self.stdout.write("  viewer@test.com / TestPass123!  — Читатель (только чтение)")
        self.stdout.write("  guest@test.com  / TestPass123!  — Гость (без ролей, доступ запрещён)")
