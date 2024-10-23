# Generated by Django 5.1.1 on 2024-10-23 02:20

import cloudinary.models
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Merchandise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.URLField()),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('category', models.CharField(choices=[('OL', 'Olahraga'), ('SN', 'Seni'), ('MS', 'Musik'), ('CP', 'Cosplay'), ('LG', 'Lingkungan'), ('VL', 'Volunteer'), ('LN', 'Lainnya')], default='LN', max_length=2)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('location', models.CharField(max_length=200, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image_urls', models.JSONField(blank=True, null=True)),
                ('merch', models.ManyToManyField(blank=True, to='main.merchandise')),
            ],
        ),
        migrations.CreateModel(
            name='MerchCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('merchandise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.merchandise')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField()),
                ('review', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('rated_event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.event')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='user_rating',
            field=models.ManyToManyField(blank=True, to='main.rating'),
        ),
        migrations.CreateModel(
            name='TicketPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ticketPrice', to='main.event')),
            ],
        ),
        migrations.CreateModel(
            name='EventCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.ticketprice')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('bio', models.TextField()),
                ('profile_picture', cloudinary.models.CloudinaryField(blank=True, default=None, max_length=255, null=True, verbose_name='image')),
                ('categories', models.CharField(blank=True, max_length=200, null=True)),
                ('wallet', models.DecimalField(decimal_places=2, default=1000000, max_digits=10)),
                ('role', models.CharField(choices=[('AD', 'Admin'), ('US', 'User')], default='US', max_length=2)),
                ('boughtMerch', models.ManyToManyField(blank=True, to='main.merchandise')),
                ('friends', models.ManyToManyField(blank=True, to='main.userprofile')),
                ('registeredEvent', models.ManyToManyField(blank=True, to='main.event')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='rating',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.userprofile'),
        ),
    ]
