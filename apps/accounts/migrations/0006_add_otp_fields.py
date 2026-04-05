from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_add_username_to_customuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='otp',
            field=models.CharField(max_length=6, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='otp_expiry',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
