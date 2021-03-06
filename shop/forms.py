from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext, gettext_lazy
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget

from base.widgets import BootstrapDateTimePickerInput
from order.models import Order
from postcode.models import Postcode
from product.models import Product
from shop.models import Shop


class ShopContactForm(forms.Form):
    email = forms.EmailField(label=gettext_lazy('email'), required=True)
    subject = forms.CharField(label=gettext_lazy('subject'), required=True, max_length=199)
    message = forms.CharField(label=gettext_lazy('message'), widget=forms.Textarea, required=True, max_length=9999)


class ShopRegisterForm(forms.ModelForm):
    postcode_special = forms.IntegerField(label=gettext_lazy("Postcode"))
    city_special = forms.CharField(label=gettext_lazy("City"))

    class Meta:
        model = Shop
        fields = ['cvr_number', 'name', 'address', 'postcode_special', 'city_special', 'email', 'phone']
        widgets = {
            'phone': PhoneNumberInternationalFallbackWidget(
                attrs={'class': 'form-control'}
            )
        }

    def clean_postcode_special(self):
        data = self.cleaned_data['postcode_special']
        try:
            Postcode.objects.get(postcode=data)
        except Postcode.DoesNotExist:
            raise forms.ValidationError(gettext("Invalid postcode"))
        return data

    def __init__(self, *args, **kwargs):
        super(ShopRegisterForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if not isinstance(self.fields[f].widget, forms.CheckboxInput):
                self.fields[f].widget.attrs['placeholder'] = self.fields[f].label
                self.fields[f].label = ''


class ShopProductForm(forms.ModelForm):
    start_datetime = forms.DateTimeField(
        label=gettext('Start datetime'),
        input_formats=['%Y-%m-%d %H:%M'],
        widget=BootstrapDateTimePickerInput(),
        required=False,
    )
    end_datetime = forms.DateTimeField(
        label=gettext('End datetime'),
        input_formats=['%Y-%m-%d %H:%M'],
        widget=BootstrapDateTimePickerInput(),
        required=False,
    )

    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'image',
            'price',
            'offer_price',
            'active',
            'start_datetime',
            'end_datetime'
        ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(ShopProductForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if not isinstance(self.fields[f].widget, forms.CheckboxInput):
                self.fields[f].widget.attrs['placeholder'] = self.fields[f].label
                self.fields[f].label = ''

    def clean(self):
        cleaned_data = super().clean()
        # Limitation - A customer can have 3 active products
        limit = 3
        if self.instance:
            active_products = Product.objects.filter(
                active=True,
                shop=self.request.user.shop
            ).exclude(pk=self.instance.pk).count()
        else:
            active_products = Product.objects.filter(
                active=True,
                shop=self.request.user.shop
            ).count()
        if cleaned_data.get('active', False) and active_products >= limit:
            raise ValidationError(
                gettext(
                    "Maximum of %(limit)s products reached!"
                ) % {'limit': limit}
            )

        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')
        if start_datetime and end_datetime and end_datetime < start_datetime:
            raise ValidationError(
                gettext(
                    "A start datetime can't start "
                    "after end datetime and vice versa"
                )
            )


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']


class ShopCVRForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['cvr_number']
