"""DB 路由"""

from django.conf import settings


DATABASE_MAPPING = settings.DATABASE_MAPPING


class DbRouter:
    """DB路由"""

    def db_for_read(self, model, **hints):
        """
        读DB路由
        """
        if model._meta.model_name in DATABASE_MAPPING:
            return DATABASE_MAPPING[model._meta.model_name]
        return None

    def db_for_write(self, model, **hints):
        """
        写DB路由
        """
        if model._meta.model_name in DATABASE_MAPPING:
            return DATABASE_MAPPING[model._meta.model_name]
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        关联DB路由
        """
        if obj1._meta.model_name in DATABASE_MAPPING and obj2._meta.model_name in DATABASE_MAPPING:
            return DATABASE_MAPPING[obj1._meta.model_name] == DATABASE_MAPPING[obj2._meta.model_name]
        return None

    def allow_migrate(self, database, app_label, model_name=None, **hints):
        """
        迁移DB路由
        """
        if database in DATABASE_MAPPING.values():
            return DATABASE_MAPPING.get(model_name) == database
        if model_name in DATABASE_MAPPING:
            return False
        return None
