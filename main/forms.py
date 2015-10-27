# encoding: utf8

from django import forms

from bootstrap3_datetime.widgets import DateTimePicker

class DateTimeRangeForm(forms.Form):

  DATETIME_PICKER_OPTIONS = {
    "format": "MM/DD/YYYY HH:mm:ss",
    "pickSeconds": False,
    "sideBySide": True,
    "widgetPositioning": "top",
  }

  from_datetime = forms.DateTimeField(
    label='From',
    widget=DateTimePicker(options=DATETIME_PICKER_OPTIONS)
  )
  to_datetime = forms.DateTimeField(
    label='To',
    widget=DateTimePicker(options=DATETIME_PICKER_OPTIONS)
  )
