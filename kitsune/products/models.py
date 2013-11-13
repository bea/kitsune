import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from kitsune.sumo.models import ModelBase


HOT_TOPIC_SLUG = 'hot'


class Product(ModelBase):
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField(upload_to=settings.PRODUCT_IMAGE_PATH, null=True,
                              blank=True,
                              max_length=settings.MAX_FILEPATH_LENGTH)

    # Dictates the order in which products are displayed in product
    # lists.
    display_order = models.IntegerField()

    # Whether or not this product is visible in the ui to users.
    visible = models.BooleanField(default=False)

    # Platforms this Product runs on.
    platforms = models.ManyToManyField('Platform')

    class Meta(object):
        ordering = ['display_order']

    def __unicode__(self):
        return u'%s' % self.title

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return os.path.join(
            settings.STATIC_URL, 'img', 'product_placeholder.png')


# Note: This is the "new" Topic class
class Topic(ModelBase):
    title = models.CharField(max_length=255, db_index=True)
    # We don't use a SlugField here because it isn't unique by itself.
    slug = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    image = models.ImageField(upload_to=settings.TOPIC_IMAGE_PATH, null=True,
                              blank=True,
                              max_length=settings.MAX_FILEPATH_LENGTH)

    # Topics are product-specific
    product = models.ForeignKey(Product, related_name='topics')

    # Topics can optionally have a parent.
    parent = models.ForeignKey('self', related_name='subtopics',
                               null=True, blank=True)

    # Dictates the order in which topics are displayed in topic lists.
    display_order = models.IntegerField()

    # Whether or not this topic is visible in the ui to users.
    visible = models.BooleanField(default=False)

    class Meta(object):
        ordering = ['product', 'display_order']
        unique_together = ('slug', 'product')

    def __unicode__(self):
        return u'[%s] %s' % (self.product.title, self.title)

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return os.path.join(
            settings.STATIC_URL, 'img', 'topic_placeholder.png')


class Version(ModelBase):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    min_version = models.FloatField()
    max_version = models.FloatField()
    product = models.ForeignKey('Product', related_name='versions')
    visible = models.BooleanField()
    default = models.BooleanField()

    class Meta(object):
        ordering = ['-max_version']
    
    def save(self):
        if self.default:
            others = (Version.objects
                      .filter(default=True, product=self.product)
                      .exclude(pk=self.pk))

            if others.count() > 0:
                raise ValidationError('Only one version can be default for '
                                      'each product.')

        super(Version, self).save()


class Platform(ModelBase):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    visible = models.BooleanField()
    # Dictates the order in which products are displayed in product
    # lists.
    display_order = models.IntegerField()

