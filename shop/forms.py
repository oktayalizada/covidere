from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext, gettext_lazy

from product.models import Product
from shop.models import Shop


class ShopContactForm(forms.Form):
    email = forms.EmailField(label=gettext_lazy('email'), required=True)
    subject = forms.CharField(label=gettext_lazy('subject'), required=True)
    message = forms.CharField(label=gettext_lazy('message'), widget=forms.Textarea, required=True)


class ShopRegisterForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'email', 'phone']


class ShopProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'image', 'price', 'offer_price', 'color', 'size', 'active', 'delivery_days', 'start_datetime', 'end_datetime']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(ShopProductForm, self).__init__(*args, **kwargs)
    

    def clean(self):
        # Limitation - A customer can have 3 active products
        limit = 3
        if self.cleaned_data.get('active', False) and Product.objects.filter(active=True, shop=self.request.user.shop).count() >= limit:
            raise ValidationError(gettext("Maximum of %(limit)s products reached!") % {'limit': limit})