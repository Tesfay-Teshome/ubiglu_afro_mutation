from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),  # Adjust this if your initial migration has a different name
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profile_image',
            field=models.ImageField(upload_to='user_profile_images/%Y/%m/%d/', blank=True, null=True, default='user_profile_images/default.jpg'),
        ),
    ]