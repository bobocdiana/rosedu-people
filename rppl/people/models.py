from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime

class Person(models.Model):
    class Meta:
        unique_together = ('first_name', 'last_name')

    user = models.ForeignKey(User, null=True, blank=True, help_text='User owning this profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    description = models.TextField(max_length=2000, blank=True)

    @property
    def projects(self):
        """
        A list of projects this person participated to
        """
        return Project.objects.filter(editions__in=self.person_roles.values('edition')).distinct()

    @property
    def name(self):
        return self.first_name + ' ' + self.last_name

    def __unicode__(self):
        return self.name


class Link(models.Model):
    """ Link for person's external accounts """
    url = models.CharField(max_length=100)
    person = models.ForeignKey(Person, blank=True, null=True)


class Organization(models.Model):
    """ External affiliations for users """
    url = models.CharField(max_length=100)
    persons = models.ManyToManyField(Person, blank=True, null=True, related_name="organisations")


class Project(models.Model):
    """ Project in community """
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=200, blank=True, null=True)

    logo = models.ImageField(blank=True, null=True, upload_to=settings.MEDIA_ROOT)

    def __unicode__(self):
        return self.name


class Edition(models.Model):
    """ Project edition """
    project = models.ForeignKey(Project, related_name="editions")
    name = models.CharField(max_length=100)
    picture = models.ImageField(blank=True, null=True, upload_to=settings.MEDIA_ROOT)

    date_start = models.DateField(default=datetime.now)
    date_end = models.DateField(default=datetime.now)
    persons = models.ManyToManyField(Person, through='PersonRole', blank=True)

    def add_person(self, person, role, timestamp=None):
        """
        Add a person role to this edition
        """
        if not isinstance(role, Role):
            role = Role.objects.get_or_create(name=role)[0]

        if timestamp:
            PersonRole.objects.create(person=person, edition=self, role=role, timestamp=timestamp)
        else:
            PersonRole.objects.create(person=person, edition=self, role=role)

    def __unicode__(self):
        return self.name


class Role(models.Model):
    """ A role that can be given to many persons in an edition """
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class PersonRole(models.Model):
    person = models.ForeignKey(Person, related_name="person_roles")
    edition = models.ForeignKey(Edition, related_name="person_roles")
    role = models.ForeignKey(Role)
    timestamp = models.DateTimeField(default=datetime.now)