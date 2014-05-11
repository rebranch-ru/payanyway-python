# -*- coding:utf-8 -*-
import hashlib
import urllib
from django import forms

from payanyway.api import Api


class MonetaForm(forms.Form, Api):
    def _set_param(self, key, value):
        if not key in self.fields.keys():
            self.fields[key] = forms.CharField(widget=forms.HiddenInput)
        self.fields[key].initial = value


    #код ответа на уведомление об оплате
    def _get_response_code(self):
        return 200 if self.is_valid() else 100

    #подпись для ответа на уведомление
    def _generate_response_signature(self):
        """
        MNT_SIGNATURE = MD5(
            RESPONSE_CODE + MNT_ID + MNT_TRANSACTION_ID + КОД ПРОВЕРКИ ЦЕЛОСТНОСТИ ДАННЫХ
        )
        """
        response_code = self._get_response_code()
        params = [response_code, self._account_id, self._transaction_id, self._integrity_check_code]
        string_to_encode = u''.join(map(unicode, params))
        signature = hashlib.md5(string_to_encode).hexdigest()
        return signature

    def _get_param(self, key):
        if key in self.fields.keys():
            return self.fields[key].initial
        else:
            return None

    def get_payment_url(self):
        data = {}
        for field in self.fields:
            data[field] = self.fields[field].initial
        url = u'{}?{}'.format(
            self.action_url,
            urllib.urlencode(data)
        )
        return url

    def __init__(self, account_id=None, transaction_id=None, amount=0, integrity_check_code=None,
                 use_signature=False, currency_code=u'RUB', test_mode=False, payment_system=None, test_server=True,
                 *args, **kwargs):
        super(MonetaForm, self).__init__(*args, **kwargs)
        self._account_id = account_id
        self._transaction_id = transaction_id
        self._currency_code = currency_code
        self._test_mode = test_mode
        self._amount = amount
        self._integrity_check_code = integrity_check_code
        self._use_test_server = test_server
        if payment_system:
            self._payment_system = payment_system
        if use_signature:
            self._request_signature = self._generate_request_signature()