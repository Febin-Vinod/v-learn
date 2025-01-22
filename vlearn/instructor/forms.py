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
