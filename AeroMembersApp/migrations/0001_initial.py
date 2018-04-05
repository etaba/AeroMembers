# Generated by Django 2.0.3 on 2018-04-03 15:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('department', models.CharField(max_length=200)),
                ('cage_code', models.CharField(blank=True, max_length=6, null=True)),
                ('number_of_employees', models.IntegerField()),
                ('activity_type', models.CharField(choices=[('CM', 'Contract Management'), ('DES', 'Design'), ('ENG', 'Engineering'), ('FM', 'Facility Management'), ('GM', 'General Management'), ('HR', 'Human Resources'), ('IT', 'IT'), ('ME', 'Manufacturing Engineering'), ('MKT', 'Marketing'), ('OP', 'Operations'), ('PLN', 'Planning'), ('PROD', 'Production'), ('PRCH', 'Purchasing'), ('QA', 'Quality'), ('RD', 'R&D'), ('RW', 'Repair & Warranty'), ('SAL', 'Sales'), ('SCM', 'Supply Chain Management')], max_length=200)),
                ('naics', models.IntegerField()),
                ('description', models.TextField(blank=True, max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='CompanyUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_admin', models.BooleanField(default=False)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AeroMembersApp.Company')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_address', models.CharField(blank=True, max_length=200)),
                ('city', models.CharField(blank=True, max_length=200)),
                ('state', models.CharField(blank=True, max_length=200)),
                ('zip_code', models.CharField(blank=True, max_length=200)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('company', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contact', to='AeroMembersApp.Company')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contact', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('active', models.BooleanField()),
                ('rate', models.FloatField()),
                ('expiration', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('type', models.CharField(choices=[('UM', 'User Membership'), ('CM', 'Company Membership'), ('R', 'Resource')], max_length=200)),
                ('description', models.TextField(max_length=1000)),
                ('price', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='JobDescription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('industry', models.CharField(choices=[('Accommodation and Food Services', 'Accommodation and Food Services'), ('Administrative and Support and Waste Management and Remediation Services', 'Administrative and Support and Waste Management and Remediation Services'), ('Agriculture, Forestry, Fishing and Hunting', 'Agriculture, Forestry, Fishing and Hunting'), ('Arts, Entertainment, and Recreation', 'Arts, Entertainment, and Recreation'), ('Construction', 'Construction'), ('Educational Services', 'Educational Services'), ('Finance and Insurance', 'Finance and Insurance'), ('Health Care and Social Assistance', 'Health Care and Social Assistance'), ('Information', 'Information'), ('Management of Companies and Enterprises', 'Management of Companies and Enterprises'), ('Mining, Quarrying, and Oil and Gas Extraction', 'Mining, Quarrying, and Oil and Gas Extraction'), ('Other Services (except Public Administration)', 'Other Services (except Public Administration)'), ('Professional, Scientific, and Technical Services', 'Professional, Scientific, and Technical Services'), ('Public Administration', 'Public Administration'), ('Real Estate and Rental and Leasing', 'Real Estate and Rental and Leasing'), ('Utilities', 'Utilities'), ('Wholesale Trade', 'Wholesale Trade')], max_length=200)),
                ('job_title', models.CharField(max_length=200)),
                ('salary', models.IntegerField(blank=True, help_text='Will not be visible to other users.')),
                ('start_date', models.DateTimeField(verbose_name='start date')),
                ('end_date', models.DateTimeField(verbose_name='end date')),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('SILVER_USER', 'Silver'), ('GOLD_USER', 'Gold'), ('PLATINUM_USER', 'Platinum'), ('SILVER_COMPANY', 'Silver'), ('GOLD_COMPANY', 'Gold'), ('SPONSOR_COMPANY', 'Sponsor')], max_length=200)),
                ('company', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='membership', to='AeroMembersApp.Company')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='membership', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('O', 'Open'), ('C', 'Closed'), ('CA', 'Canceled'), ('IP', 'In Progress')], default='O', max_length=200)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('requestingCompany', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order', to='AeroMembersApp.Company')),
                ('requestingUser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('price', models.FloatField()),
                ('discount', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='orderLine', to='AeroMembersApp.Discount')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AeroMembersApp.Item')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='OrderLines', to='AeroMembersApp.Order')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=1000)),
                ('score', models.IntegerField(default=0)),
                ('createdOn', models.DateTimeField(default=django.utils.timezone.now)),
                ('editedOn', models.DateTimeField(default=django.utils.timezone.now)),
                ('quotedText', models.TextField(blank=True, max_length=1000, null=True)),
                ('object_id', models.PositiveIntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('birthdate', models.DateTimeField(blank=True, help_text='Will not be visible to other users.', null=True, verbose_name='date of birth')),
                ('private', models.BooleanField(default=False, help_text='Keep personal information hidden from other users. Only your username will be visible.')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Resume',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('education', models.CharField(blank=True, max_length=200)),
                ('awards', models.TextField(blank=True, max_length=200)),
                ('certifications', models.TextField(blank=True, max_length=200)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='resume', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SectorMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField(unique=True)),
                ('sector', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='UserUpvote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('postId', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='AeroMembersApp.Post')),
                ('title', models.CharField(max_length=200)),
                ('status', models.CharField(choices=[('O', 'Open'), ('C', 'Closed'), ('R', 'Resolved')], default='O', max_length=200)),
                ('threadType', models.CharField(choices=[('Q', 'Question'), ('D', 'Discussion')], max_length=200)),
                ('tags', models.ManyToManyField(blank=True, to='AeroMembersApp.Tag')),
            ],
            bases=('AeroMembersApp.post',),
        ),
        migrations.AddField(
            model_name='post',
            name='content_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='post',
            name='createdBy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='jobdescription',
            name='profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='jobDescription', to='AeroMembersApp.Profile'),
        ),
        migrations.AlterUniqueTogether(
            name='item',
            unique_together={('type', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='userupvote',
            unique_together={('user', 'postId')},
        ),
        migrations.AddField(
            model_name='tag',
            name='threads',
            field=models.ManyToManyField(to='AeroMembersApp.Thread'),
        ),
        migrations.AlterUniqueTogether(
            name='companyuser',
            unique_together={('user', 'company')},
        ),
    ]
