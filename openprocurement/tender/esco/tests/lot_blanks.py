# -*- coding: utf-8 -*-
from datetime import timedelta
from iso8601 import parse_date
from copy import deepcopy
# Tender Lot Resouce Test


def create_tender_lot_invalid(self):
    response = self.app.post_json('/tenders/some_id/lots', {'data': {'title': 'lot title', 'description': 'lot description'}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
    ])

    request_path = '/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token)

    response = self.app.post(request_path, 'data', status=415)
    self.assertEqual(response.status, '415 Unsupported Media Type')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description':
            u"Content-Type header should be one of ['application/json']", u'location': u'header', u'name': u'Content-Type'}
    ])

    response = self.app.post(request_path, 'data', content_type='application/json', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'No JSON object could be decoded', u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, 'data', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available', u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, {'not_data': {}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available',u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, {'data': {}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'minimalStepPercentage'},
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'title'},
    ])

    response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field', u'location': u'body', u'name': u'invalid_field'}
    ])

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {"items": [{'relatedLot': '0' * 32}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}], u'location': u'body', u'name': u'items'}
    ])


def patch_tender_lot_minValue(self):
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token), {'data': self.test_lots_data[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']

    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token), {"data": {"minValue": {"amount": 300}}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('minValue', response.json['data'])
    self.assertEqual(response.json['data']['minValue']['amount'], 0)
    self.assertEqual(response.json['data']['minValue']['currency'], 'UAH')


def get_tender_lot(self):
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': self.test_lots_data[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']

    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data']), set(
        [u'status', u'date', u'description', u'title', u'auctionPeriod', u'minValue', u'id',
         u'minimalStepPercentage', u'fundingKind', u'yearlyPaymentsPercentageRange']))

    self.set_status('active.qualification')

    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot.pop('auctionPeriod')
    self.assertEqual(response.json['data'], lot)

    response = self.app.get('/tenders/{}/lots/some_id'.format(self.tender_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'lot_id'}
    ])

    response = self.app.get('/tenders/some_id/lots/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])


def get_tender_lots(self):
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': self.test_lots_data[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']

    response = self.app.get('/tenders/{}/lots'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data'][0]), set(
        [u'status', u'description', u'date', u'title', u'auctionPeriod', u'minValue', u'id',
         u'minimalStepPercentage', u'fundingKind', u'yearlyPaymentsPercentageRange']))

    self.set_status('active.qualification')

    response = self.app.get('/tenders/{}/lots'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot.pop('auctionPeriod')
    self.assertEqual(response.json['data'][0], lot)

    response = self.app.get('/tenders/some_id/lots', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])


def lot_minimal_step_invalid(self):
    request_path = '/tenders/{}'.format(self.tender_id)
    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotIn('minimalStep', response.json['data'])

    data = self.test_lots_data[0]
    data['minimalStep'] = {'amount': 100}
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token), {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotIn('minimalStep', response.json['data'])
    lot = response.json['data']

    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token), {"data": {"minimalStep": {"amount": 300}}})
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('minimalStep', response.json['data'])


def tender_minimal_step_percentage(self):
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token), {'data': self.test_lots_data[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['minimalStepPercentage'], self.test_lots_data[0]['minimalStepPercentage'])

    request_path = '/tenders/{}'.format(self.tender_id)
    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['minimalStepPercentage'], min([i['minimalStepPercentage'] for i in self.test_lots_data]))


def tender_lot_funding_kind(self):
    data = deepcopy(self.initial_data)
    data['fundingKind'] = 'budget'
    response = self.app.post_json('/tenders', {'data': data})
    tender = response.json['data']
    tender_token = response.json['access']['token']
    self.assertEqual(response.status, '201 Created')
    self.assertIn('fundingKind', response.json['data'])
    self.assertEqual(response.json['data']['fundingKind'], 'budget')

    lot = deepcopy(self.test_lots_data[0])
    lot['fundingKind'] = 'budget'
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender['id'], tender_token), {'data': lot})
    self.assertEqual(response.status, '201 Created')
    self.assertIn('fundingKind', response.json['data'])
    self.assertEqual(response.json['data']['fundingKind'], 'budget')
    lot1_id = response.json['data']['id']

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], tender_token), {'data': {'fundingKind': 'other'}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('fundingKind', response.json['data'])
    self.assertEqual(response.json['data']['fundingKind'], 'other')

    response = self.app.get('/tenders/{}/lots/{}'.format(tender['id'], lot1_id))
    self.assertEqual(response.status, '200 OK')
    self.assertIn('fundingKind', response.json['data'])
    self.assertEqual(response.json['data']['fundingKind'], 'other')

    lot['fundingKind'] = 'budget'
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender['id'], tender_token), {'data': lot}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'lot funding kind should be identical to tender funding kind'], u'location': u'body', u'name': u'lots'}
    ])

    # try to change lot funding king to budget, but it stays the same (other, same as tender funding kind)
    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(tender['id'], lot1_id, tender_token), {'data': lot})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('fundingKind', response.json['data'])
    self.assertEqual(response.json['data']['fundingKind'], 'other')


def tender_1lot_fundingKind_default(self):
    data = deepcopy(self.initial_data)
    del data['fundingKind']
    lot = deepcopy(self.test_lots_data[0])
    del lot['fundingKind']

    response = self.app.post_json('/tenders', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    # when no fundingKind field in initial data, default value should be set
    self.assertEqual(response.json['data']['fundingKind'], 'other')
    tender = response.json['data']
    tender_token = response.json['access']['token']

    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender['id'], tender_token), {'data': lot})
    self.assertEqual(response.status, '201 Created')
    self.assertIn('fundingKind', response.json['data'])
    self.assertEqual(response.json['data']['fundingKind'], 'other')

    lot['fundingKind'] = 'budget'
    response = self.app.post_json('/tenders', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['fundingKind'], 'other')
    tender = response.json['data']
    tender_token = response.json['access']['token']

    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender['id'], tender_token), {'data': lot})
    self.assertEqual(response.status, '201 Created')
    self.assertIn('fundingKind', response.json['data'])
    self.assertEqual(response.json['data']['fundingKind'], 'other')

    lot['fundingKind'] = 'other'
    data['fundingKind'] = 'budget'
    response = self.app.post_json('/tenders', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['fundingKind'], 'budget')
    tender = response.json['data']
    tender_token = response.json['access']['token']

    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender['id'], tender_token), {'data': lot})
    self.assertEqual(response.status, '201 Created')
    self.assertIn('fundingKind', response.json['data'])
    self.assertEqual(response.json['data']['fundingKind'], 'budget')

    del lot['fundingKind']
    response = self.app.post_json('/tenders', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['fundingKind'], 'budget')
    tender = response.json['data']
    tender_token = response.json['access']['token']

    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender['id'], tender_token), {'data': lot})
    self.assertEqual(response.status, '201 Created')
    self.assertIn('fundingKind', response.json['data'])
    self.assertEqual(response.json['data']['fundingKind'], 'budget')

    data['lots'] = []
    data['lots'].append(deepcopy(lot))
    data['lots'][0]['fundingKind'] = 'budget'
    del data['fundingKind']
    response = self.app.post_json('/tenders', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertIn('fundingKind', response.json['data'])
    self.assertEqual(response.json['data']['fundingKind'], 'other')
    self.assertIn('lots', response.json['data'])
    self.assertIn('fundingKind', response.json['data']['lots'][0])
    self.assertEqual(response.json['data']['lots'][0]['fundingKind'], 'other')

    del data['lots'][0]['fundingKind']
    data['fundingKind'] = 'budget'
    response = self.app.post_json('/tenders', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertIn('fundingKind', response.json['data'])
    self.assertEqual(response.json['data']['fundingKind'], 'budget')
    self.assertIn('lots', response.json['data'])
    self.assertIn('fundingKind', response.json['data']['lots'][0])
    self.assertEqual(response.json['data']['lots'][0]['fundingKind'], 'budget')


def tender_2lot_fundingKind_default(self):
    data = deepcopy(self.initial_data)
    lot = deepcopy(self.test_lots_data[0])
    data['lots'] = []
    data['lots'].append(deepcopy(lot))
    data['lots'].append(deepcopy(lot))
    del data['fundingKind']
    del data['lots'][0]['fundingKind']
    del data['lots'][1]['fundingKind']

    response = self.app.post_json('/tenders', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['fundingKind'], 'other')
    self.assertIn('lots', response.json['data'])
    self.assertIn('fundingKind', response.json['data']['lots'][0])
    self.assertEqual(response.json['data']['lots'][0]['fundingKind'], 'other')
    self.assertIn('fundingKind', response.json['data']['lots'][1])
    self.assertEqual(response.json['data']['lots'][1]['fundingKind'], 'other')

    data['lots'][0]['fundingKind'] = 'budget'
    data['lots'][1]['fundingKind'] = 'budget'
    response = self.app.post_json('/tenders', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['fundingKind'], 'other')
    self.assertIn('lots', response.json['data'])
    self.assertIn('fundingKind', response.json['data']['lots'][0])
    self.assertEqual(response.json['data']['lots'][0]['fundingKind'], 'other')
    self.assertIn('fundingKind', response.json['data']['lots'][1])
    self.assertEqual(response.json['data']['lots'][1]['fundingKind'], 'other')

    data['fundingKind'] = 'budget'
    del data['lots'][0]['fundingKind']
    del data['lots'][1]['fundingKind']
    response = self.app.post_json('/tenders', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['fundingKind'], 'budget')
    self.assertIn('lots', response.json['data'])
    self.assertIn('fundingKind', response.json['data']['lots'][0])
    self.assertEqual(response.json['data']['lots'][0]['fundingKind'], 'budget')
    self.assertIn('fundingKind', response.json['data']['lots'][1])
    self.assertEqual(response.json['data']['lots'][1]['fundingKind'], 'budget')

    del data['fundingKind']
    data['lots'][0]['fundingKind'] = 'other'
    data['lots'][1]['fundingKind'] = 'budget'
    response = self.app.post_json('/tenders', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'lot funding kind should be identical to tender funding kind'], u'location': u'body', u'name': u'lots'}
    ])


def tender_lot_yearlyPaymentsPercentageRange(self):
    data = deepcopy(self.initial_data)
    data['fundingKind'] = 'budget'
    data['yearlyPaymentsPercentageRange'] = 0.7
    lot = deepcopy(self.test_lots_data[0])
    data['lots'] = []
    data['lots'].append(deepcopy(lot))
    data['lots'].append(deepcopy(lot))

    del data['lots'][0]['yearlyPaymentsPercentageRange']
    del data['lots'][1]['yearlyPaymentsPercentageRange']
    response = self.app.post_json('/tenders', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('lots', response.json['data'])
    self.assertEqual(response.json['data']['lots'][0]['yearlyPaymentsPercentageRange'], 0.8)
    self.assertEqual(response.json['data']['lots'][1]['yearlyPaymentsPercentageRange'], 0.8)
    tender_id = response.json['data']['id']
    tender_token = response.json['access']['token']
    lot1_id = response.json['data']['lots'][0]['id']

    response = self.app.get('/tenders/{}'.format(tender_id))
    lots = response.json['data']['lots']
    self.assertEqual(response.json['data']['yearlyPaymentsPercentageRange'], min([i['yearlyPaymentsPercentageRange'] for i in lots]))

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, tender_token), {'data': {'yearlyPaymentsPercentageRange': 0.5}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['yearlyPaymentsPercentageRange'], min([i['yearlyPaymentsPercentageRange'] for i in lots]))

    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(tender_id, lot1_id, tender_token), {'data': {'yearlyPaymentsPercentageRange': 0.3}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['yearlyPaymentsPercentageRange'], 0.3)

    response = self.app.get('/tenders/{}'.format(tender_id))
    lots = response.json['data']['lots']
    self.assertEqual(response.json['data']['yearlyPaymentsPercentageRange'], min([i['yearlyPaymentsPercentageRange'] for i in lots]))

    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(tender_id, lot1_id, tender_token), {'data': {'yearlyPaymentsPercentageRange': 0.9}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'when fundingKind is budget, yearlyPaymentsPercentageRange should be less or equal 0.8, and more or equal 0'], u'location': u'body', u'name': u'yearlyPaymentsPercentageRange'}
    ])

    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(tender_id, lot1_id, tender_token), {'data': {'yearlyPaymentsPercentageRange': 0.8}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['yearlyPaymentsPercentageRange'], 0.8)

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, tender_token), {'data': {'fundingKind': 'other', 'yearlyPaymentsPercentageRange': 0.8}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('fundingKind', response.json['data'])
    self.assertEqual(response.json['data']['fundingKind'], 'other')
    self.assertEqual(response.json['data']['yearlyPaymentsPercentageRange'], 0.8)

    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(tender_id, lot1_id, tender_token), {'data': {'yearlyPaymentsPercentageRange': 0.9}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'when fundingKind is other, yearlyPaymentsPercentageRange should be equal 0.8'], u'location': u'body', u'name': u'yearlyPaymentsPercentageRange'}
    ])

# Tender Lot Feature Resource Test


def tender_min_value(self):
    request_path = '/tenders/{}'.format(self.tender_id)
    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['minValue']['amount'], sum([i['minValue']['amount'] for i in self.initial_lots]))

    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token), {'data': self.test_lots_data[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']

    response = self.app.get(request_path)
    self.assertEqual(len(response.json['data']['lots']), 3)
    self.assertEqual(response.json['data']['minValue']['amount'], sum([i['minValue']['amount'] for i in response.json['data']['lots']]))

    response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    response = self.app.get(request_path)
    self.assertEqual(len(response.json['data']['lots']), 2)
    self.assertEqual(response.json['data']['minValue']['amount'], sum([i['minValue']['amount'] for i in response.json['data']['lots']]))


# TenderLotBidResourceTest

def create_tender_bid_invalid(self):
    request_path = '/tenders/{}/bids'.format(self.tender_id)
    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers']}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'lotValues'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": self.test_bids_data[0]['value']}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedLot': [u'This field is required.']}], u'location': u'body', u'name': u'lotValues'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': "0" * 32}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}], u'location': u'body', u'name': u'lotValues'}
    ])

    # comment this test while minValue = 0
    # response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": {
    #     'yearlyPayments': 0.9,
    #     'annualCostsReduction': 15.5,
    #     'contractDuration': 10}, 'relatedLot': self.initial_lots[0]['id']}]}}, status=422)
    # self.assertEqual(response.status, '422 Unprocessable Entity')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['status'], 'error')
    # self.assertEqual(response.json['errors'], [
    #     {u'description': [{u'value': [u'value of bid should be greater than minValue of lot']}], u'location': u'body', u'name': u'lotValues'}
    # ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": {
        'yearlyPaymentsPercentage': 0.9,
        'annualCostsReduction': [751.5] * 11,
        'contractDuration': {'years': 10}}, 'relatedLot': self.initial_lots[0]['id']}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'value':{u'annualCostsReduction': [u'annual costs reduction should be set for 21 period']}}], u'location': u'body', u'name': u'lotValues'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": {
        'yearlyPaymentsPercentage': 0.9,
        'annualCostsReduction': 751.5,
        'contractDuration': {'years': 25}}, 'relatedLot': self.initial_lots[0]['id']}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'value':{u'contractDuration': {u'years': [u'Int value should be less than 15.']}}}], u'location': u'body', u'name': u'lotValues'},
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], "value": self.test_bids_data[0]['value'], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': self.initial_lots[0]['id']}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'value should be posted for each lot of bid'], u'location': u'body', u'name': u'value'}
    ])


def patch_tender_bid(self):
    lot_id = self.initial_lots[0]['id']
    response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]["tenderers"], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': lot_id}]}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertGreater(response.json['data']['lotValues'][0]['value']['amountPerfomance'], 10)
    self.assertLess(response.json['data']['lotValues'][0]['value']['amountPerfomance'], 1500)
    self.assertGreater(response.json['data']['lotValues'][0]['value']['amount'], 500)
    self.assertLess(response.json['data']['lotValues'][0]['value']['amount'], 15000)
    bid = response.json['data']
    bid_token = response.json['access']['token']
    lot = bid['lotValues'][0]

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token), {"data": {'tenderers': [{"name": u"Державне управління управлінням справами"}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']['tenderers'][0]['name'], bid['tenderers'][0]['name'])

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token), {"data": {'lotValues': [{"value": {
        'yearlyPaymentsPercentage': 0.9,
        'annualCostsReduction': [760.5] * 21,
        'contractDuration': {'years': 10}}, 'relatedLot': lot_id}], 'tenderers': self.test_bids_data[0]["tenderers"]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['tenderers'][0]['name'], bid['tenderers'][0]['name'])

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token), {"data": {'lotValues': [{"value": {
        'yearlyPaymentsPercentage': 0.9,
        'annualCostsReduction': [751.5] * 21,
        'contractDuration': {'years': 10, 'days': 80}}, 'relatedLot': lot_id}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['data']['lotValues'][0]["value"]["amountPerfomance"], 751.5) # TODO Change when NPV is OK
    # self.assertEqual(response.json['data']['lotValues'][0]["value"]["amount"], 751.5) # TODO Change when NPV is OK

    self.time_shift('active.pre-qualification')
    self.check_chronograph()

    response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotIn('lotValues', response.json['data'])

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token), {"data": {'lotValues': [{"value": {"yearlyPaymentsPercentage": 0.8}, 'relatedLot': lot_id}], 'status': 'active'}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update bid in current (unsuccessful) tender status")

# TenderLotFeatureBidResourceTest


def create_tender_feature_bid_invalid(self):
    request_path = '/tenders/{}/bids'.format(self.tender_id)
    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers']}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": self.test_bids_data[0]['value']}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedLot': [u'This field is required.']}], u'location': u'body', u'name': u'lotValues'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': "0" * 32}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}], u'location': u'body', u'name': u'lotValues'}
    ])

    # comment this test while minValue = 0
    # response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": {
    #     'yearlyPayments': 0.9,
    #     'annualCostsReduction': 15.5,
    #     'contractDuration': 10}, 'relatedLot': self.lot_id}]}}, status=422)
    # self.assertEqual(response.status, '422 Unprocessable Entity')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['status'], 'error')
    # self.assertEqual(response.json['errors'], [
    #     {u'description': [{u'value': [u'value of bid should be greater than minValue of lot']}], u'location': u'body', u'name': u'lotValues'}
    # ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': self.lot_id}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'All features parameters is required.'], u'location': u'body', u'name': u'parameters'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': self.lot_id}], 'parameters': [{"code": "code_item", "value": 0.01}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'All features parameters is required.'], u'location': u'body', u'name': u'parameters'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': self.lot_id}], 'parameters': [{"code": "code_invalid", "value": 0.01}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'code': [u'code should be one of feature code.']}], u'location': u'body', u'name': u'parameters'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': self.lot_id}], 'parameters': [
        {"code": "code_item", "value": 0.01},
        {"code": "code_tenderer", "value": 0},
        {"code": "code_lot", "value": 0.01},
    ]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'value': [u'value should be one of feature value.']}], u'location': u'body', u'name': u'parameters'}
    ])


def create_tender_feature_bid(self):
    request_path = '/tenders/{}/bids'.format(self.tender_id)
    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': self.test_bids_data[0]["tenderers"], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': self.lot_id}], 'parameters': [
        {"code": "code_item", "value": 0.01},
        {"code": "code_tenderer", "value": 0.01},
        {"code": "code_lot", "value": 0.01},
    ]}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bid = response.json['data']
    self.assertEqual(bid['tenderers'][0]['name'], self.initial_data["procuringEntity"]['name'])
    self.assertIn('id', bid)
    self.assertIn(bid['id'], response.headers['Location'])

    self.time_shift('active.pre-qualification')
    self.check_chronograph()

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': self.test_bids_data[0]["tenderers"], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': self.lot_id}], 'parameters': [
        {"code": "code_item", "value": 0.01},
        {"code": "code_tenderer", "value": 0.01},
        {"code": "code_lot", "value": 0.01},
    ]}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add bid in current (unsuccessful) tender status")


def tender_features_invalid(self):
    request_path = '/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token)
    data = self.initial_data.copy()
    item = data['items'][0].copy()
    item['id'] = "1"
    data['items'] = [item]
    data['features'] = [
        {
            "featureOf": "lot",
            "relatedItem": self.initial_lots[0]['id'],
            "title": u"Потужність всмоктування",
            "enum": [
                {
                    "value": self.invalid_feature_value,
                    "title": u"До 1000 Вт"
                },
                {
                    "value": 0.01,
                    "title": u"Більше 1000 Вт"
                }
            ]
        }
    ]
    response = self.app.patch_json(request_path, {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'enum': [{u'value': [u'Float value should be less than {}.'.format(self.max_feature_value)]}]}], u'location': u'body', u'name': u'features'}
    ])
    data['features'][0]["enum"][0]["value"] = 0.02
    data['features'].append(data['features'][0].copy())
    data['features'][1]["enum"][0]["value"] = self.sum_of_max_value_of_all_features
    response = self.app.patch_json(request_path, {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'Sum of max value of all features for lot should be less then or equal to {0:.0%}'.format(self.sum_of_max_value_of_all_features)], u'location': u'body', u'name': u'features'}
    ])
    data['features'][1]["enum"][0]["value"] = 0.02
    data['features'].append(data['features'][0].copy())
    data['features'][2]["relatedItem"] = self.initial_lots[1]['id']
    data['features'].append(data['features'][2].copy())
    response = self.app.patch_json(request_path, {'data': data})
    self.assertEqual(response.status, '200 OK')
