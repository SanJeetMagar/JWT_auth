from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0004_customuser_groups_customuser_is_active_and_more'),
    ]
    operations = [
        migrations.AddField(
            model_name='customuser',
            name='username',
field=models.CharField(max_length=150, unique=True),
        ),
    ]
