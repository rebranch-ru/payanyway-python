# -*- coding:utf-8 -*-
import hashlib


class Api(object):
    PAYMENT_SYSTEMS_WEBMONEY = u'1017'
    PAYMENT_SYSTEMS_QIWI = u'1031'
    PAYMENT_SYSTEMS_CARD = u'1887'
    PAYMENT_SYSTEMS_SMS = u'36960'

    __use_signature = False
    __integrity_check_code = None
    __notification_signature = None

    action_url = u'https://demo.moneta.ru/assistant.htm'

    #Идентификатор магазина в системе MONETA.RU. Соответствует номеру расширенного счета магазина.
    __PARAM_ACCOUNT_ID = u'MNT_ID'

    #Внутренний идентификатор заказа, однозначно определяющий заказ в магазине. Ограничение на размер – 255 символов.
    __PARAM_TRANSACTION_ID = u'MNT_TRANSACTION_ID'

    #ISO код валюты, в которой производится оплата заказа в магазине. Значение должно соответствовать коду валюты
    #счета получателя (MNT_ID).
    __PARAM_CURRENCY_CODE = u'MNT_CURRENCY_CODE'

    #Сумма оплаты. Десятичные символы отделяются точкой. Количество знаков после запятой - максимум два символа.
    #Значение суммы носит рекомендательный характер и технически может быть изменено пользователем.
    #Необязательный параметр, если указан «Check URL» в настройках счета. Если параметр не задан, то сумма будет
    #запрошена в учетной системе магазина соответствующим проверочным запросом.
    __PARAM_AMOUNT = u'MNT_AMOUNT'

    #(0 | 1) Необязательный параметр. Указание, что запрос происходит в тестовом режиме. Если параметр «MNT_TEST_MODE»
    #равен 1, то реального списания и зачисления средств не произойдет. Запросы также будут происходить в тестовом
    #режиме, если выставить флаг «Тестовый режим» в настройках счета.
    __PARAM_TEST_MODE = u'MNT_TEST_MODE'

    #Описание оплаты
    __PARAM_DESCRIPTION = u'MNT_DESCRIPTION'

    #Необязательный параметр. URL страницы магазина, куда должен попасть покупатель после благополучно проведенной
    #оплаты.
    __PARAM_SUCCESS_URL = u'MNT_SUCCESS_URL'

    #Необязательный параметр. Код для идентификации отправителя и проверки целостности данных. Если в запросе есть
    # данный параметр, то MONETA.RU сгенерирует собственный код на основе параметров запроса и сравнит его с данным
    # параметром. Если параметр «MNT_SIGNATURE» и код сгенерированный MONETA.RU не совпадут, то MONETA.Assistant
    # завершится с ошибкой. Является обязательным, если в настройках счета выставлен флаг «Подпись формы оплаты
    # обязательна».
    __PARAM_SIGNATURE = u'MNT_SIGNATURE'

    #Необязательный параметр. Внутренний идентификатор пользователя, однозначно определяющий получателя в учетной
    # системе магазина.
    __PARAM_SUBSCRIBER_ID = u'MNT_SUBSCRIBER_ID'

    #ID операции в системе payanyway
    __PARAM_OPERATION_ID = u'MNT_OPERATION_ID'

    #Пройти весь MONETA.Assistant с предустановленными значениями. Для этого необходимо выбрать платежную систему и
    # заполнить параметры платежной системы (если они есть).
    __PARAM_FOLLOWUP = u'followup'

    #Предварительный выбор платежной системы.
    __PARAM_PAYMENT_SYSTEM_UNIT_ID = u'paymentSystem.unitId'

    __params_list = (
        __PARAM_ACCOUNT_ID,
        __PARAM_TRANSACTION_ID,
        __PARAM_CURRENCY_CODE,
        __PARAM_AMOUNT,
        __PARAM_TEST_MODE,
        __PARAM_DESCRIPTION,
        __PARAM_SUCCESS_URL,
        __PARAM_SIGNATURE,
        __PARAM_OPERATION_ID
    )

    def raw_init(self, data):
        params_list = list(self.__params_list)
        params_list.remove(self.__PARAM_SIGNATURE)
        for param in params_list:
            if param in data.keys():
                self._set_param(param, data[param])
        self.__notification_signature = data.get(self.__PARAM_SIGNATURE)

    #проверка подписи уведомления
    def is_signature_valid(self):
        return self._generate_notification_signature() == self.__notification_signature

    #код ответа на уведомление об оплате
    def __get_response_code(self):
        return 200 if self.is_valid() else 100

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

    #подпись для ответа на уведомление
    def _generate_response_signature(self):
        """
        MNT_SIGNATURE = MD5(
            RESPONSE_CODE + MNT_ID + MNT_TRANSACTION_ID + КОД ПРОВЕРКИ ЦЕЛОСТНОСТИ ДАННЫХ
        )
        """
        response_code = self.__get_response_code()
        params = [response_code, self._account_id, self._transaction_id, self._integrity_check_code]
        string_to_encode = u''.join(map(unicode, params))
        signature = hashlib.md5(string_to_encode).hexdigest()
        return signature

    def _set_param(self, key, value):
        self.__params[key] = value

    def _get_param(self, key):
        return self.__params.get(key)

    def __get_account_id(self):
        return self._get_param(self.__PARAM_ACCOUNT_ID)

    def __set_account_id(self, value):
        self._set_param(self.__PARAM_ACCOUNT_ID, value)

    def __get_transaction_id(self):
        return self._get_param(self.__PARAM_TRANSACTION_ID)

    def __set_transaction_id(self, value):
        self._set_param(self.__PARAM_TRANSACTION_ID, value)

    def __get_currency_code(self):
        return self._get_param(self.__PARAM_CURRENCY_CODE)

    def __set_currency_code(self, value):
        self._set_param(self.__PARAM_CURRENCY_CODE, value)

    def __get_amount(self):
        value = self._get_param(self.__PARAM_AMOUNT)
        value = float(value)
        return u'{0:.2f}'.format(value)

    def __set_amount(self, value):
        self._set_param(self.__PARAM_AMOUNT, value)

    def __get_test_mode(self):
        return self._get_param(self.__PARAM_TEST_MODE)

    def __set_test_mode(self, value):
        """
        API монеты ждет значения 1 или 0
        """
        self._set_param(self.__PARAM_TEST_MODE, int(bool(value)))

    def __get_description(self):
        return self._get_param(self.__PARAM_DESCRIPTION)

    def __set_description(self, value):
        self._set_param(self.__PARAM_DESCRIPTION, value)

    def __get_success_url(self):
        return self._get_param(self.__PARAM_SUCCESS_URL)

    def __set_success_url(self, value):
        self._set_param(self.__PARAM_SUCCESS_URL, value)

    def __get_signature(self):
        return self._get_param(self.__PARAM_SIGNATURE)

    def __set_signature(self, value):
        self._set_param(self.__PARAM_SIGNATURE, value)

    def __get_integrity_check_code(self):
        return self.__integrity_check_code

    def __set_integrity_check_code(self, value):
        self.__integrity_check_code = value

    def __get_operation_id(self):
        return self._get_param(self.__PARAM_OPERATION_ID)

    def __set_operation_id(self, value):
        self._set_param(self.__PARAM_OPERATION_ID, value)

    def __get_payment_system(self):
        return self._get_param(self.__PARAM_PAYMENT_SYSTEM_UNIT_ID)

    def __set_payment_system(self, value):
        self._followup = u'true'
        self._set_param(self.__PARAM_PAYMENT_SYSTEM_UNIT_ID, value)

    def __get_followup(self):
        return self._get_param(self.__PARAM_FOLLOWUP)

    def __set_followup(self, value):
        self._set_param(self.__PARAM_FOLLOWUP, value)


    _account_id = property(__get_account_id, __set_account_id)
    _transaction_id = property(__get_transaction_id, __set_transaction_id)
    _currency_code = property(__get_currency_code, __set_currency_code)
    _amount = property(__get_amount, __set_amount)
    _description = property(__get_description, __set_description)
    _success_url = property(__get_success_url, __set_success_url)
    _test_mode = property(__get_test_mode, __set_test_mode)
    _operation_id = property(__get_operation_id, __set_operation_id)
    _request_signature = property(__get_signature, __set_signature)
    _payment_system = property(__get_payment_system, __set_payment_system)
    _followup = property(__get_followup, __set_followup)

    #код проверки целостности данных
    _integrity_check_code = property(__get_integrity_check_code, __set_integrity_check_code)

    def __init__(self, account_id=None, transaction_id=None, amount=0, integrity_check_code=None,
                 use_signature=False,
                 currency_code=u'RUB', test_mode=False, *args, **kwargs):
        self.__params = {}
        self._account_id = account_id
        self._transaction_id = transaction_id
        self._currency_code = currency_code
        self._test_mode = test_mode
        self._amount = amount
        self._integrity_check_code = integrity_check_code
        if use_signature:
            self._request_signature = self._generate_request_signature()