from django.db.migrations.loader import MigrationLoader
from django.test import SimpleTestCase, override_settings

from csvimport.models import CSVImport


class ProductionMigrationTest(SimpleTestCase):
    @override_settings(MIGRATION_MODULES={"csvimport": "csvimport.migrations"})
    def test_model_name_default_matches_production_migrations(self):
        loader = MigrationLoader(None, ignore_no_migrations=True)
        state = loader.project_state(("csvimport", "0002_alter_csvimport_model_name"))
        migrated_model = state.apps.get_model("csvimport", "CSVImport")

        self.assertEqual(
            migrated_model._meta.get_field("model_name").default,
            CSVImport._meta.get_field("model_name").default,
        )
