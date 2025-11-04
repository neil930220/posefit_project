"""
Add Weightlifting Exercise Type
"""

from django.db import migrations


def add_weightlifting_exercise_type(apps, schema_editor):
    """添加舉重運動類型"""
    ExerciseType = apps.get_model('exercise', 'ExerciseType')
    
    exercise_data = {
        'name': '舉重',
        'description': '舉重是鍛鍊上半身肌群的動作，重點是保持手臂垂直角度，主要訓練肩膀、手臂和核心肌群。',
        'difficulty_level': 2,
        'target_muscles': ['肩膀', '手臂', '核心肌群', '背部'],
        'instructions': [
            '雙腳與肩同寬站立',
            '雙手握住槓鈴或啞鈴',
            '保持上半身手垂直角度（肩膀到手腕）',
            '手臂應該垂直於地面',
            '保持核心收緊',
            '避免手臂過度前傾或後傾'
        ]
    }
    
    ExerciseType.objects.get_or_create(
        name=exercise_data['name'],
        defaults=exercise_data
    )


def reverse_add_weightlifting_exercise_type(apps, schema_editor):
    """反向操作 - 刪除舉重運動類型"""
    ExerciseType = apps.get_model('exercise', 'ExerciseType')
    ExerciseType.objects.filter(name='舉重').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('exercise', '0002_initial_exercise_types'),
    ]

    operations = [
        migrations.RunPython(
            add_weightlifting_exercise_type,
            reverse_add_weightlifting_exercise_type
        ),
    ]
