# Generated by Django 3.2.5 on 2022-03-31 01:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20220327_1848'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='amount_id',
            new_name='amount_paid',
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('New', 'Nuevo'), ('Accepted', 'Aceptado'), ('Completed', 'Completado'), ('Cancelled', 'Cancelado')], default='new', max_length=50),
        ),
    ]
