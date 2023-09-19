import datetime
from time import timezone
from typing import Any, Dict, Mapping, Optional, Type, Union
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList

from .models import Budget, Income, Expense, RecurrencyType


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email address'}),
        help_text='<span class="form-text text-muted"><small>Required. Inform a valid email address.</small></span>')
    first_name = forms.CharField(max_length=254, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'First name'}),
        help_text='<span class="form-text text-muted"><small>Required. Inform a valid first name.</small></span>')
    last_name = forms.CharField(max_length=254, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Last name'}),
        help_text='<span class="form-text text-muted"><small>Required. Inform a valid last name.</small></span>')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'password1', 'password2',)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<span class="form-text text-muted"><small>Your password can’t be too similar to your other personal information. It must contain at least 8 characters, nor be a commonly used password. and it can’t be entirely numeric.</small></span>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


class BudgetForm(forms.ModelForm):

    class Meta:
        model = Budget
        fields = ('purpose', 'goal', 'from_date', 'to_date')

    def __init__(self, *args, **kwargs):
        super(BudgetForm, self).__init__(*args, **kwargs)
        self.fields['purpose'].widget.attrs['class'] = 'form-control'
        self.fields['purpose'].widget.attrs['placeholder'] = 'Purpose'
        self.fields['purpose'].label = ''
        self.fields['purpose'].help_text = '<span class="form-text text-muted"><small>Required. Inform a valid purpose.</small></span>'
        self.fields['goal'].widget.attrs['class'] = 'form-control'
        self.fields['goal'].widget.attrs['placeholder'] = 'Goal'
        self.fields['goal'].label = ''
        self.fields['goal'].help_text = '<span class="form-text text-muted"><small>Required. Inform a valid goal.</small></span>'
        self.fields['from_date'] = forms.DateField(widget=forms.SelectDateWidget(
            attrs={'class': 'form-control'}))
        self.fields['from_date'].help_text = '<span class="form-text text-muted"><small>Required. Inform a valid from date.</small></span>'
        self.fields['to_date'] = forms.DateField(widget=forms.SelectDateWidget(
            attrs={'class': 'form-control'}))
        self.fields['to_date'].help_text = '<span class="form-text text-muted"><small>Required. Inform a valid to date. It should be greater than the budget start date.</small></span>'


class BudgetEntryForm(forms.ModelForm):
    class Meta:
        model = None
        fields = ('source', 'amount', 'date',
                  'recurrency', 'frequency')

    def __init__(self, *args, **kwargs):
        super(BudgetEntryForm, self).__init__(*args, **kwargs)
        self.fields['source'].widget.attrs['class'] = 'form-control'
        self.fields['source'].widget.attrs['placeholder'] = 'Source'
        self.fields['source'].label = ''
        self.fields['source'].help_text = '<span class="form-text text-muted"><small>Required. Inform a valid source.</small></span>'

        self.fields['amount'].widget.attrs['class'] = 'form-control'
        self.fields['amount'].widget.attrs['placeholder'] = 'Amount'
        self.fields['amount'].label = ''
        self.fields['amount'].help_text = '<span class="form-text text-muted"><small>Required. Inform a valid amount.</small></span>'

        self.fields['date'] = forms.DateField(widget=forms.SelectDateWidget(
            attrs={'class': 'form-control'}))
        self.fields['date'].help_text = '<span class="form-text text-muted"><small>Required. Inform a valid date.</small></span>'
        self.fields['date'].label = 'Date'

        self.fields['recurrency'] = forms.ChoiceField(choices=RecurrencyType.choices, widget=forms.Select(
            attrs={'class': 'form-control'}))
        self.fields['recurrency'].help_text = '<span class="form-text text-muted"><small>Required. Inform a valid recurrency type.</small></span>'
        self.fields['recurrency'].label = 'Recurrency'

        self.fields['frequency'] = forms.IntegerField(widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Frequency'}))
        self.fields['frequency'].help_text = '<span class="form-text text-muted"><small>Required. Inform a valid frequency.</small></span>'
        self.fields['frequency'].label = 'Frequency'


class IncomeForm(BudgetEntryForm):

    class Meta:
        model = Income
        fields = ('source', 'amount', 'date',
                  'recurrency', 'frequency')


class ExpenseForm(BudgetEntryForm):

    class Meta:
        model = Expense
        fields = ('source', 'amount', 'date',
                  'recurrency', 'frequency')
