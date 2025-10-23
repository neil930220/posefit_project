"""
Initial data for Exercise Types
"""

from django.db import migrations


def create_initial_exercise_types(apps, schema_editor):
    """創建初始的運動類型"""
    ExerciseType = apps.get_model('exercise', 'ExerciseType')
    
    exercise_types = [
        {
            'name': '深蹲',
            'description': '深蹲是鍛鍊下半身肌群的基本動作，主要訓練大腿前側、後側、臀部和核心肌群。',
            'difficulty_level': 1,
            'target_muscles': ['大腿前側', '大腿後側', '臀部', '核心肌群'],
            'instructions': [
                '雙腳與肩同寬站立',
                '腳尖稍微向外',
                '保持背部挺直',
                '臀部向後坐，膝蓋彎曲',
                '下蹲至大腿與地面平行',
                '用腳跟發力站起'
            ]
        },
        {
            'name': '伏地挺身',
            'description': '伏地挺身是鍛鍊上半身肌群的經典動作，主要訓練胸部、肩膀和手臂肌群。',
            'difficulty_level': 2,
            'target_muscles': ['胸部', '肩膀', '手臂', '核心肌群'],
            'instructions': [
                '俯臥撐姿勢，雙手與肩同寬',
                '保持身體成一直線',
                '核心收緊',
                '胸部下降至接近地面',
                '用胸部肌群推起身體',
                '保持身體穩定'
            ]
        },
        {
            'name': '平板支撐',
            'description': '平板支撐是鍛鍊核心肌群的靜態動作，主要訓練腹部、背部和肩膀穩定性。',
            'difficulty_level': 1,
            'target_muscles': ['腹部', '背部', '肩膀', '核心肌群'],
            'instructions': [
                '俯臥撐姿勢，但用前臂支撐',
                '保持身體成一直線',
                '核心收緊',
                '保持正常呼吸',
                '避免臀部過高或過低',
                '保持姿勢穩定'
            ]
        },
        {
            'name': '弓箭步',
            'description': '弓箭步是單側下肢訓練動作，主要鍛鍊大腿前側、後側和臀部肌群。',
            'difficulty_level': 2,
            'target_muscles': ['大腿前側', '大腿後側', '臀部', '核心肌群'],
            'instructions': [
                '雙腳與肩同寬站立',
                '向前跨一大步',
                '後腳保持穩定',
                '前腳膝蓋彎曲至90度',
                '後腳膝蓋接近地面',
                '用前腳發力回到起始位置'
            ]
        },
        {
            'name': '引體向上',
            'description': '引體向上是鍛鍊上半身拉力的動作，主要訓練背部、手臂和肩膀肌群。',
            'difficulty_level': 3,
            'target_muscles': ['背部', '手臂', '肩膀', '核心肌群'],
            'instructions': [
                '雙手正握單槓，與肩同寬',
                '身體懸垂',
                '肩胛骨收緊',
                '用背部肌群拉起身體',
                '下巴超過單槓',
                '控制速度下降'
            ]
        }
    ]
    
    for exercise_data in exercise_types:
        ExerciseType.objects.get_or_create(
            name=exercise_data['name'],
            defaults=exercise_data
        )


def reverse_create_initial_exercise_types(apps, schema_editor):
    """反向操作 - 刪除初始運動類型"""
    ExerciseType = apps.get_model('exercise', 'ExerciseType')
    ExerciseType.objects.filter(
        name__in=['深蹲', '伏地挺身', '平板支撐', '弓箭步', '引體向上']
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('exercise', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_initial_exercise_types,
            reverse_create_initial_exercise_types
        ),
    ]
