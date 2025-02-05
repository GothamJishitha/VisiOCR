from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="VisitorPass",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("visitor_pass_id", models.CharField(max_length=20, unique=True)),
                ("name", models.CharField(max_length=100)),
                (
                    "gender",
                    models.CharField(
                        choices=[
                            ("Male", "Male"),
                            ("Female", "Female"),
                            ("Other", "Other"),
                        ],
                        max_length=10,
                    ),
                ),
                ("mobile_number", models.CharField(max_length=10)),
                ("aadhaar_number", models.CharField(max_length=14)),
                ("dob", models.DateField()),
                ("date_of_visiting", models.DateField()),
                ("duration_of_visiting", models.IntegerField()),
            ],
        ),
    ]