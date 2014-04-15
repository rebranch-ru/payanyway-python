# -*- coding:utf-8 -*-
from django import forms
from django.template.loader import render_to_string

from payanyway.api import Api


class MonetaForm(forms.Form, Api):
    def _set_param(self, key, value):
        if not key in self.fields.keys():
            self.fields[key] = forms.CharField(widget=forms.HiddenInput)
        self.fields[key].initial = value

    def _get_param(self, key):
        if key in self.fields.keys():
            return self.fields[key].initial
        else:
            return None

    def __init__(self, account_id=None, transaction_id=None, amount=0, integrity_check_code=None,
                 use_signature=False, currency_code=u'RUB', test_mode=False, payment_system=None, *args, **kwargs):
        super(MonetaForm, self).__init__(*args, **kwargs)
        self._account_id = account_id
        self._transaction_id = transaction_id
        self._currency_code = currency_code
        self._test_mode = test_mode
        self._amount = amount
        self._integrity_check_code = integrity_check_code
        if payment_system:
            self._payment_system = payment_system
        if use_signature:
            self._request_signature = self._generate_request_signature()