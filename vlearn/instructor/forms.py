from django import forms
from .models import Course, Category, Video
from django.forms import modelformset_factory

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'image','duration','price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        # Add "others" option as a choice for categories (which will trigger new category input)
        self.fields['category'].choices = list(self.fields['category'].choices) + [('others', 'Others')]

    # Validate category to check if it's "others" and requires a new category name
    def clean_category(self):
        category = self.cleaned_data.get('category')
        if category == 'others':
            new_category = self.data.get('new_category')
            if not new_category:
                raise forms.ValidationError('Please provide a new category name.')
            category = new_category  # Override with the new category
        return category

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title_1', 'video_file']  # Use 'title_1' instead of 'title'

VideoFormSet = modelformset_factory(Video, form=VideoForm, extra=1)  # extra=1 allows for 1 extra blank form

class CourseUpdateForm(forms.ModelForm):
    # Field for 'category' includes an option for 'others'
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,  # Not required initially
        empty_label="Select Category"
    )
    new_category = forms.CharField(
        required=False,
        label='New Category',
        widget=forms.TextInput(attrs={'placeholder': 'Enter new category if others selected'})
    )

    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'price', 'duration', 'image']

    def clean(self):
        cleaned_data = super().clean()
        
        # If "others" category is selected, ensure the new_category field is filled
        category = cleaned_data.get('category')
        new_category = cleaned_data.get('new_category')

        if category is None and new_category == '':
            raise forms.ValidationError('Please provide a new category name if you select "others".')

        return cleaned_data