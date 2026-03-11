from django.db import migrations, models
import django.db.models.deletion
import pgvector.django


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_enable_pgvector'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('user_id', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('pattern_summary', models.TextField(blank=True, default='')),
                ('commitments', models.JSONField(default=list)),
                ('goals', models.JSONField(default=list)),
            ],
            options={'db_table': 'user_profiles'},
        ),
        migrations.CreateModel(
            name='Memory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('memory_type', models.CharField(
                    choices=[
                        ('commitment', 'Compromiso'), ('goal', 'Meta'),
                        ('excuse', 'Excusa'), ('achievement', 'Logro'),
                        ('pattern', 'Patrón'), ('context', 'Contexto'),
                    ],
                    default='context', max_length=20
                )),
                ('embedding', pgvector.django.VectorField(dimensions=384)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('importance', models.FloatField(default=1.0)),
                ('promised_at', models.DateTimeField(blank=True, null=True)),
                ('fulfilled', models.BooleanField(blank=True, null=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='memories', to='chat.userprofile'
                )),
            ],
            options={'db_table': 'memories', 'ordering': ['-importance', '-created_at']},
        ),
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('session_id', models.CharField(max_length=100)),
                ('role', models.CharField(max_length=20)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='conversations', to='chat.userprofile'
                )),
            ],
            options={'db_table': 'conversations', 'ordering': ['created_at']},
        ),
    ]
