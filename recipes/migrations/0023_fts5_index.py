from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0022_menus_likes'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                """
                CREATE VIRTUAL TABLE recipes_fts USING fts5(
                    title, ingredients, instructions,
                    tokenize='unicode61'
                )
                """,
                """
                INSERT INTO recipes_fts(rowid, title, ingredients, instructions)
                SELECT id, title, ingredients, instructions FROM recipes_recipe
                """,
                """
                CREATE TRIGGER recipes_fts_ai AFTER INSERT ON recipes_recipe BEGIN
                    INSERT INTO recipes_fts(rowid, title, ingredients, instructions)
                    VALUES (new.id, new.title, new.ingredients, new.instructions);
                END
                """,
                """
                CREATE TRIGGER recipes_fts_ad AFTER DELETE ON recipes_recipe BEGIN
                    DELETE FROM recipes_fts WHERE rowid = old.id;
                END
                """,
                """
                CREATE TRIGGER recipes_fts_au AFTER UPDATE ON recipes_recipe BEGIN
                    DELETE FROM recipes_fts WHERE rowid = old.id;
                    INSERT INTO recipes_fts(rowid, title, ingredients, instructions)
                    VALUES (new.id, new.title, new.ingredients, new.instructions);
                END
                """,
            ],
            reverse_sql=[
                "DROP TRIGGER IF EXISTS recipes_fts_au",
                "DROP TRIGGER IF EXISTS recipes_fts_ad",
                "DROP TRIGGER IF EXISTS recipes_fts_ai",
                "DROP TABLE IF EXISTS recipes_fts",
            ],
        ),
    ]
