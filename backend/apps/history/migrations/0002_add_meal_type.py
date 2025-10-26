from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='foodentry',
            name='meal_type',
            field=models.CharField(
                blank=True,
                choices=[('breakfast', '早餐'), ('lunch', '午餐'), ('dinner', '晚餐')],
                default='',
                help_text='Optional: 早餐/午餐/晚餐',
                max_length=16,
            ),
        ),
    ]


