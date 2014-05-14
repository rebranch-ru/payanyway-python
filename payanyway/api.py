# -*- coding:utf-8 -*-
import hashlib
import urllib

from utils import AttributeDescriptor


class Api(object):
    PAYMENT_SYSTEMS_WEBMONEY = u'1017'
    PAYMENT_SYSTEMS_QIWI = u'1031'
    PAYMENT_SYSTEMS_CARD = u'1887'
    PAYMENT_SYSTEMS_SMS = u'36960'
    PAYMENT_SYSTEMS_YANDEX = u'1020'
    PAYMENT_SYSTEMS_ALFACLICK = u'31877'
    PAYMENT_SYSTEMS_SBERBANK = u'32863'

    _use_signature = False
    _integrity_check_code = None
    _notification_signature = None

    _action_url_dev = u'https://demo.moneta.ru/assistant.htm'
    _action_url_production = u'https://moneta.ru/assistant.htm'

    #Идентификатор магазина в системе MONETA.RU. Соответствует номеру расширенного счета магазина.
    _PARAM_ACCOUNT_ID = u'MNT_ID'

    #Внутренний идентификатор заказа, однозначно определяющий заказ в магазине. Ограничение на размер – 255 символов.
    _PARAM_TRANSACTION_ID = u'MNT_TRANSACTION_ID'

    #ISO код валюты, в которой производится оплата заказа в магазине. Значение должно соответствовать коду валюты
    #счета получателя (MNT_ID).
    _PARAM_CURRENCY_CODE = u'MNT_CURRENCY_CODE'

    #Сумма оплаты. Десятичные символы отделяются точкой. Количество знаков после запятой - максимум два символа.
    #Значение суммы носит рекомендательный характер и технически может быть изменено пользователем.
    #Необязательный параметр, если указан «Check URL» в настройках счета. Если параметр не задан, то сумма будет
    #запрошена в учетной системе магазина соответствующим проверочным запросом.
    _PARAM_AMOUNT = u'MNT_AMOUNT'

    #(0 | 1) Необязательный параметр. Указание, что запрос происходит в тестовом режиме. Если параметр «MNT_TEST_MODE»
    #равен 1, то реального списания и зачисления средств не произойдет. Запросы также будут происходить в тестовом
    #режиме, если выставить флаг «Тестовый режим» в настройках счета.
    _PARAM_TEST_MODE = u'MNT_TEST_MODE'

    #Описание оплаты
    _PARAM_DESCRIPTION = u'MNT_DESCRIPTION'

    #Необязательный параметр. URL страницы магазина, куда должен попасть покупатель после благополучно проведенной
    #оплаты.
    _PARAM_SUCCESS_URL = u'MNT_SUCCESS_URL'

    #Необязательный параметр. Код для идентификации отправителя и проверки целостности данных. Если в запросе есть
    # данный параметр, то MONETA.RU сгенерирует собственный код на основе параметров запроса и сравнит его с данным
    # параметром. Если параметр «MNT_SIGNATURE» и код сгенерированный MONETA.RU не совпадут, то MONETA.Assistant
    # завершится с ошибкой. Является обязательным, если в настройках счета выставлен флаг «Подпись формы оплаты
    # обязательна».
    _PARAM_SIGNATURE = u'MNT_SIGNATURE'

    #Необязательный параметр. Внутренний идентификатор пользователя, однозначно определяющий получателя в учетной
    # системе магазина.
    _PARAM_SUBSCRIBER_ID = u'MNT_SUBSCRIBER_ID'

    #ID операции в системе payanyway
    _PARAM_OPERATION_ID = u'MNT_OPERATION_ID'

    #Пройти весь MONETA.Assistant с предустановленными значениями. Для этого необходимо выбрать платежную систему и
    # заполнить параметры платежной системы (если они есть).
    _PARAM_FOLLOWUP = u'followup'

    #Предварительный выбор платежной системы.
    _PARAM_PAYMENT_SYSTEM_UNIT_ID = u'paymentSystem.unitId'

    _raw_init_params = (
        _PARAM_ACCOUNT_ID,
        _PARAM_TRANSACTION_ID,
        _PARAM_CURRENCY_CODE,
        _PARAM_AMOUNT,
        _PARAM_TEST_MODE,
        _PARAM_DESCRIPTION,
        _PARAM_SUCCESS_URL,
        _PARAM_OPERATION_ID
    )

    def _set_param(self, key, value):
        self._params[key] = value

    def _get_param(self, key):
        return self._params.get(key)

    def raw_init(self, data):
        for param in self._raw_init_params:
            if param in data.keys():
                self._set_param(param, data[param])
        self._notification_signature = data.get(self._PARAM_SIGNATURE)

    #проверка подписи уведомления
    def is_signature_valid(self):
        return self._generate_notification_signature() == self._notification_signature

    #подпись для запроса оплату
    def _generate_request_signature(self):
        """
        MNT_SIGNATURE = MD5(
            MNT_ID + MNT_TRANSACTION_ID + MNT_AMOUNT + MNT_CURRENCY_CODE + MNT_SUBSCRIBER_ID +
            ТЕСТОВЫЙ РЕЖИМ + КОД ПРОВЕРКИ ЦЕЛОСТНОСТИ ДАННЫХ
        )
        """
        params = [self._account_id, self._transaction_id, self._amount, self._currency_code, self._test_mode,
                  self._integrity_check_code]
        string_to_encode = u''.join(map(unicode, params))
        print string_to_encode
        signature = hashlib.md5(string_to_encode).hexdigest()
        return signature

    #подпись уведомления об оплате
    def _generate_notification_signature(self):
        """
        MNT_SIGNATURE = MD5(
            MNT_ID + MNT_TRANSACTION_ID + OPERATION_ID + MNT_AMOUNT + MNT_CURRENCY_CODE +
            ТЕСТОВЫЙ РЕЖИМ + КОД ПРОВЕРКИ ЦЕЛОСТНОСТИ ДАННЫХ
        )
        """
        params = [self._account_id, self._transaction_id, self._operation_id, self._amount, self._currency_code,
                  self._test_mode, self._integrity_check_code]
        string_to_encode = u''.join(map(unicode, params))
        signature = hashlib.md5(string_to_encode).hexdigest()
        return signature

    @property
    def _amount(self):
        value = self._get_param(self._PARAM_AMOUNT)
        value = float(value)
        return u'{0:.2f}'.format(value)

    @_amount.setter
    def _amount(self, value):
        self._set_param(self._PARAM_AMOUNT, value)

    @property
    def _test_mode(self):
        return self._get_param(self._PARAM_TEST_MODE)

    @_test_mode.setter
    def _test_mode(self, value):
        """
        API монеты ждет значения 1 или 0
        """
        self._set_param(self._PARAM_TEST_MODE, int(bool(value)))

    @property
    def _payment_system(self):
        return self._get_param(self._PARAM_PAYMENT_SYSTEM_UNIT_ID)

    @_payment_system.setter
    def _payment_system(self, value):
        self._followup = u'true'
        self._set_param(self._PARAM_PAYMENT_SYSTEM_UNIT_ID, value)

    @property
    def action_url(self):
        if self._use_test_server:
            return self._action_url_dev
        else:
            return self._action_url_production

    _account_id = AttributeDescriptor(_PARAM_ACCOUNT_ID)
    _transaction_id = AttributeDescriptor(_PARAM_TRANSACTION_ID)
    _currency_code = AttributeDescriptor(_PARAM_CURRENCY_CODE)
    _description = AttributeDescriptor(_PARAM_DESCRIPTION)
    _success_url = AttributeDescriptor(_PARAM_SUCCESS_URL)
    _operation_id = AttributeDescriptor(_PARAM_OPERATION_ID)
    _request_signature = AttributeDescriptor(_PARAM_SIGNATURE)
    _followup = AttributeDescriptor(_PARAM_FOLLOWUP)

    def get_payment_url(self):
        data = self._params.copy()
        url = u'{}?{}'.format(
            self.action_url,
            urllib.urlencode(data)
        )
        return url

    def __init__(self, account_id=None, transaction_id=None, amount=0, integrity_check_code=None, use_signature=False,
                 currency_code=u'RUB', test_mode=False, test_server=True, payment_system=None, *args, **kwargs):
        self._params = {}
        self._account_id = account_id
        self._transaction_id = transaction_id
        self._currency_code = currency_code
        self._test_mode = test_mode
        self._amount = amount
        self._integrity_check_code = integrity_check_code
        self._use_test_server = test_server
        if use_signature:
            self._request_signature = self._generate_request_signature()
        if payment_system:
            self._payment_system = payment_system