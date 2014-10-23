from decimal import Decimal

from django.test import TestCase

from peacecorps.models import Fund
from peacecorps.forms import DonationAmountForm, DonationPaymentForm


class DonationPaymentTests(TestCase):
    def form_data(self, clear=[], **kwargs):
        """Create a form_data object with reasonable defaults"""
        form_data = {
            'donor_type': 'Individual',
            'payer_name': 'William Williams',
            'billing_address': '1 Main Street',
            'billing_city': 'Anytown',
            'country': 'USA',
            'billing_state': 'MD',
            'billing_zip': '20852',
            'payment_type': 'CreditCard',
            'project_code': '15-4FF',
            'payment_amount': '3000',
            'information_consent': 'vol-consent-yes'
        }
        for key in clear:
            del form_data[key]
        for key, value in kwargs.items():
            form_data[key] = value
        return form_data

    def test_individual_donation_required(self):
        """ Check the minimum required data.  """
        form_data = self.form_data()
        form = DonationPaymentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_individual_ACH(self):
        """" Set the payment_type to ACH and check validation. """
        form_data = self.form_data()
        form_data['payment_type'] = 'CreditACH'
        form = DonationPaymentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_organization_donation_required(self):
        """ Check the minimum required data for the organization form. """
        form_data = self.form_data(
            clear=['payer_name'], donor_type='Organization',
            organization_name='Big Corporation',
            organization_contact='Mr A.  Suit')
        form = DonationPaymentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_individual_requirements(self):
        """Verify that "name" is required if donor_type is Individual.
        Further, verify that the organization fields get cleared"""
        form_data = self.form_data(
            clear=['payer_name'], organization_name='Big Corporation',
            organization_contact='Mr A. Suit')
        form = DonationPaymentForm(data=form_data)
        self.assertFalse(form.is_valid())

        form_data['payer_name'] = 'Bob'
        form = DonationPaymentForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertFalse('organization_name' in form.cleaned_data)
        self.assertFalse('organization_contact' in form.cleaned_data)

    def test_organization_requirements(self):
        """Verify that "organization_name" and "organization_contact" are
        required if donor_type is Organization. Also verify that the
        (Individual's) name field gets cleared"""
        form_data = self.form_data(donor_type='Organization')
        form = DonationPaymentForm(data=form_data)
        self.assertFalse(form.is_valid())

        form_data['organization_name'] = 'Org org'
        form = DonationPaymentForm(data=form_data)
        self.assertFalse(form.is_valid())
        form_data['organization_contact'] = 'Contact'
        form = DonationPaymentForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertFalse('payer_name' in form.cleaned_data)

    def test_zip_state_requirements(self):
        """Zip code and state are only required when the country is the US"""
        form_data = self.form_data(clear=['billing_state', 'billing_zip'])
        form = DonationPaymentForm(data=form_data)
        self.assertFalse(form.is_valid())

        form_data['country'] = 'CAN'
        form = DonationPaymentForm(data=form_data)
        self.assertTrue(form.is_valid())


class DonationAmountTests(TestCase):
    def test_preset_25(self):
        """Selecting a preset should set the correct value in
        payment_amount"""
        data = {'presets': 'preset-25'}
        form = DonationAmountForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['payment_amount'], Decimal(25))

    def test_preset_all(self):
        """Selecting 'preset-all' should be equivalent to a payment amount of
        the remaining balance"""
        fund = Fund(fundgoal=9876, fundcurrent=1234)
        data = {'presets': 'preset-all'}
        form = DonationAmountForm(data=data, fund=fund)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['payment_amount'], Decimal(86.42))

    def test_preset_all_bounds(self):
        """Selecting 'preset-all' won't work if the remaining balance is out
        of bounds"""
        fund = Fund(fundgoal=1000000, fundcurrent=0)
        data = {'presets': 'preset-all'}
        form = DonationAmountForm(data=data, fund=fund)
        self.assertFalse(form.is_valid())

        fund.fundcurrent = 999999
        form = DonationAmountForm(data=data, fund=fund)
        self.assertFalse(form.is_valid())

    def test_preset_custom(self):
        """Entering no value will result in an error. Entering a custom amount
        will resolve"""
        fund = Fund(fundgoal=1000000, fundcurrent=0)
        data = {'presets': 'custom'}
        form = DonationAmountForm(data=data, fund=fund)
        self.assertFalse(form.is_valid())

        data['payment_amount'] = 1250
        form = DonationAmountForm(data=data, fund=fund)
        self.assertTrue(form.is_valid())
