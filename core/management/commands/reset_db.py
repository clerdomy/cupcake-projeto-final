import glob
import os

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Reseta o banco de dados, exclui arquivos de migração e cria um usuário admin automaticamente"

    def handle(self, *args, **kwargs):
        self.stdout.write(
            self.style.NOTICE(
                "Iniciando reset do banco de dados, excluindo arquivos de migração e criação de usuário admin..."
            )
        )

        # Apagar o banco de dados existente
        db_path = "db.sqlite3"
        if os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write(
                self.style.SUCCESS(f"Banco de dados {db_path} apagado com sucesso.")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"Banco de dados {db_path} não encontrado.")
            )

        # Apagar arquivos de migração
        migration_files = glob.glob("*/migrations/*.py")

        for migration_file in migration_files:
            if "init" not in migration_file.split("__"):
                os.remove(migration_file)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Arquivo de migração {migration_file} apagado com sucesso."
                    )
                )

        # Recriar o banco de dados e as tabelas
        call_command("makemigrations", interactive=False)
        self.stdout.write(self.style.SUCCESS("Migrações criadas com sucesso."))

        call_command("migrate", interactive=False)
        self.stdout.write(self.style.SUCCESS("Tabelas criadas com sucesso."))

        # Criar um usuário admin automaticamente
        username = os.getenv("DEV_USERNAME")
        email = os.getenv("DEV_EMAIL")
        password = os.getenv("DEV_PASSWORD")

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(
                self.style.SUCCESS(f"Usuário {username} criado com sucesso.")
            )
        else:
            self.stdout.write(self.style.WARNING(f"Usuário {username} já existe."))
