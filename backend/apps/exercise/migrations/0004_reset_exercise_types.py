from django.db import migrations


def reset_exercise_types(apps, schema_editor):
    ExerciseType = apps.get_model('exercise', 'ExerciseType')
    ExerciseType.objects.all().delete()

    ExerciseType.objects.create(
        name='舉重',
        description='雙臂保持垂直角度的舉重動作，專注於肩膀與手臂肌群。',
        difficulty_level=2,
        target_muscles=['肩膀', '手臂', '核心肌群'],
        instructions=[
            '雙腳與肩同寬站立',
            '雙手握住器材並向上舉起',
            '保持上臂與前臂呈垂直角度',
            '核心收緊、避免身體晃動',
        ],
    )


def reverse_reset_exercise_types(apps, schema_editor):
    ExerciseType = apps.get_model('exercise', 'ExerciseType')
    ExerciseType.objects.filter(name='舉重').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('exercise', '0003_add_weightlifting'),
    ]

    operations = [
        migrations.RunPython(reset_exercise_types, reverse_reset_exercise_types),
    ]

