# Generated by Django 5.1.2 on 2024-12-22 06:11

import builtins
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
            name='Event',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('category', models.CharField(choices=[('OL', 'Olahraga'), ('SN', 'Seni'), ('MS', 'Musik'), ('CP', 'Cosplay'), ('LG', 'Lingkungan'), ('VL', 'Volunteer'), ('AK', 'Akademis'), ('KL', 'Kuliner'), ('PW', 'Pariwisata'), ('FS', 'Festival'), ('FM', 'Film'), ('FN', 'Fashion'), ('LN', 'Lainnya')], default='LN', max_length=2)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('location', models.CharField(max_length=200, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image_urls', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Merchandise',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('image_url', models.URLField(max_length=500)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('quantity', models.IntegerField(default=10)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('related_event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='merchandise', to='main.event')),
            ],
        ),
        migrations.CreateModel(
            name='MerchCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
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
                ('rating', models.IntegerField(default=5, verbose_name=builtins.max)),
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
                ('quantity', models.IntegerField(default=0)),
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
                ('registeredEvent', models.ManyToManyField(blank=True, to='main.ticketprice')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='rating',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.userprofile'),
        ),
        migrations.CreateModel(
            name='ForumReply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('forum', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.forum')),
                ('reply_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.forumreply')),
                ('dislike', models.ManyToManyField(blank=True, related_name='forum_reply_dislike', to='main.userprofile')),
                ('like', models.ManyToManyField(blank=True, related_name='forum_reply_like', to='main.userprofile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.userprofile')),
            ],
        ),
        migrations.AddField(
            model_name='forum',
            name='dislike',
            field=models.ManyToManyField(blank=True, related_name='forum_dislike', to='main.userprofile'),
        ),
        migrations.AddField(
            model_name='forum',
            name='like',
            field=models.ManyToManyField(blank=True, related_name='forum_like', to='main.userprofile'),
        ),
        migrations.AddField(
            model_name='forum',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.userprofile'),
        ),
    ]
