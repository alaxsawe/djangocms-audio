# -*- coding: utf-8 -*-
"""
Enables the user to add an "Audio player" plugin that serves as
a wrapper rendering the player and its options.

The "Audio player" plugin allows to add either a single "File" or a reference
to a "Folder" as children.
"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _

from cms.models import CMSPlugin

from djangocms_attributes_field.fields import AttributesField

from filer.fields.file import FilerFileField
from filer.fields.folder import FilerFolderField


# mp3 is supported by all major browsers
ALLOWED_EXTENSIONS = getattr(
    settings,
    'DJANGOCMS_AUDIO_ALLOWED_EXTENSIONS',
    ['mp3', 'ogg'],
)


# Add additional choices through the ``settings.py``.
def get_templates():
    choices = getattr(
        settings,
        'DJANGOCMS_AUDIO_TEMPLATES',
        [],
    )
    return choices


@python_2_unicode_compatible
class AudioPlayer(CMSPlugin):
    """
    Renders a container around the HTML <audio> elements.
    """
    DEFAULT_CHOICE = 'default'

    TEMPLATE_CHOICES = [
        ('default', _('Default')),
    ]

    # The label will be displayed as help text in the structure board view.
    template = models.CharField(
        verbose_name=_('Template'),
        choices=TEMPLATE_CHOICES + get_templates(),
        default=DEFAULT_CHOICE,
        max_length=50,
    )
    label = models.CharField(
        verbose_name=_('Label'),
        blank=True,
        max_length=200,
    )
    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
    )

    def __str__(self):
        return self.label or str(self.pk)


@python_2_unicode_compatible
class AudioFile(CMSPlugin):
    """
    Renders the HTML <audio> element, add params through attributes.
    """
    audio_file = FilerFileField(
        verbose_name=_('File'),
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    text_title = models.CharField(
        verbose_name=_('Title'),
        blank=True,
        max_length=200,
    )
    text_description = models.TextField(
        verbose_name=_('Description'),
        blank=True,
    )
    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
    )

    def __str__(self):
        if self.audio_file_id and self.audio_file.label:
            return self.audio_file.label
        return str(self.pk)

    def clean(self):
        if (self.audio_file and
            self.audio_file.extension not in ALLOWED_EXTENSIONS):
            raise ValidationError(
                ugettext('Incorrect file type: {extension}.')
                    .format(extension=self.audio_file.extension)
            )

    def get_short_description(self):
        if self.audio_file_id and self.audio_file.label:
            return self.audio_file.label
        return ugettext('<file is missing>')

    def copy_relations(self, oldinstance):
        # Because we have a ForeignKey, it's required to copy over
        # the reference from the instance to the new plugin.
        self.audio_file = oldinstance.audio_file


@python_2_unicode_compatible
class AudioFolder(CMSPlugin):
    """
    Render files contained in a folder, only ALLOWED_EXTENSIONS are considered.
    If you desire more customisation (title name, description) use the
    File plugin.
    """
    audio_folder = FilerFolderField(
        verbose_name=_('Folder'),
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
        help_text=_('Is applied to all audio file instances.'),
    )

    def __str__(self):
        if self.audio_folder_id and self.audio_folder.name:
            return self.audio_folder.name
        return str(self.pk)

    def get_files(self):
        files = []

        for audio_file in self.audio_folder.files:
            if audio_file.extension in ALLOWED_EXTENSIONS:
                files.append(audio_file)
        return files

    def get_short_description(self):
        if self.audio_folder_id and self.audio_folder.name:
            return self.audio_folder.name
        return ugettext('<folder is missing>')

    def copy_relations(self, oldinstance):
        # Because we have a ForeignKey, it's required to copy over
        # the reference from the instance to the new plugin.
        self.audio_folder = oldinstance.audio_folder


@python_2_unicode_compatible
class AudioTrack(CMSPlugin):
    """
    Renders the HTML <track> element inside <audio>.
    """
    KIND_CHOICES = [
        ('subtitles', _('Subtitles')),
        ('captions', _('Captions')),
        ('descriptions', _('Descriptions')),
        ('chapters', _('Chapters')),
    ]

    kind = models.CharField(
        verbose_name=_('Kind'),
        choices=KIND_CHOICES,
        max_length=50,
    )
    src = FilerFileField(
        verbose_name=_('Source file'),
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    srclang = models.CharField(
        verbose_name = _('Source language'),
        blank=True,
        max_length=10,
        help_text=_('Examples: "en" or "de" etc.'),
    )
    label = models.CharField(
        verbose_name=_('Label'),
        blank=True,
        max_length=200,
    )
    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
    )

    def __str__(self):
        return self.kind