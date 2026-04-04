from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = "apps.accounts"
    label = "accounts"      # <– app label Django uses
    def ready(self):
        import apps.accounts.signals