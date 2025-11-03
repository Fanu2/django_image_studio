from django import forms
from .models import ImageItem

# 🎨 Available image effects
EFFECT_CHOICES = [
    ('none', 'None'),
    ('grayscale', 'Grayscale'),
    ('sepia', 'Sepia Tone'),
    ('invert', 'Invert Colors'),
    ('sharpen', 'Sharpen'),
    ('emboss', 'Emboss'),
    ('edge', 'Edge Detect'),
    ('oilpaint', 'Oil Paint'),
    ('charcoal', 'Charcoal'),
    ('sketch', 'Sketch'),
    ('solarize', 'Solarize'),
    ('posterize', 'Posterize'),
    ('noise', 'Add Noise'),
    ('mirror', 'Mirror (Horizontal)'),
    ('flip', 'Flip (Vertical)'),
    ('rotate_left', 'Rotate Left 90°'),
    ('rotate_right', 'Rotate Right 90°'),
    ('frame', 'Add Frame'),
    ('border', 'Add Border'),
    ('shadow', 'Drop Shadow'),
    ('vignette', 'Vignette'),
    ('cartoon', 'Cartoon Effect'),
    ('glow', 'Soft Glow'),
]


class UploadForm(forms.ModelForm):
    """🖼️ Form for uploading a new image."""
    class Meta:
        model = ImageItem
        fields = ['title', 'original']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter image title'
            }),
            'original': forms.ClearableFileInput(attrs={
                'class': 'form-control-file'
            }),
        }


class ManipulateForm(forms.Form):
    """🎛️ Form for applying image effects, filters, and transformations."""
    # === Effect selection ===
    effect = forms.ChoiceField(
        choices=EFFECT_CHOICES,
        label="Choose Effect",
        initial='none',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # === Basic Adjustments ===
    brightness = forms.FloatField(
        label="Brightness (%)",
        min_value=0, max_value=200, initial=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1'})
    )
    contrast = forms.FloatField(
        label="Contrast (%)",
        min_value=0, max_value=200, initial=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1'})
    )
    saturate = forms.FloatField(
        label="Saturation (%)",
        min_value=0, max_value=200, initial=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1'})
    )
    blur = forms.FloatField(
        label="Blur Radius",
        min_value=0, max_value=20, initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'})
    )
    opacity = forms.FloatField(
        label="Opacity (%)",
        min_value=0, max_value=100, initial=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1'})
    )

    # === Geometric Transformations ===
    rotate = forms.FloatField(
        label="Rotate (°)",
        min_value=-360, max_value=360, initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1'})
    )
    resize_width = forms.IntegerField(
        label="Resize Width (px)",
        required=False, min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    resize_height = forms.IntegerField(
        label="Resize Height (px)",
        required=False, min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    crop_left = forms.IntegerField(
        label="Crop Left (px)", required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    crop_top = forms.IntegerField(
        label="Crop Top (px)", required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    crop_right = forms.IntegerField(
        label="Crop Right (px)", required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    crop_bottom = forms.IntegerField(
        label="Crop Bottom (px)", required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    # === Advanced Transformations ===
    deskew = forms.BooleanField(label="Deskew Image", required=False)
    trim = forms.BooleanField(label="Auto Trim", required=False)
    flip_horizontal = forms.BooleanField(label="Flip Horizontally", required=False)
    flip_vertical = forms.BooleanField(label="Flip Vertically", required=False)

    # === Notes for saving ===
    note = forms.CharField(
        label="Note",
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Describe this version (e.g., 'Sepia + Glow + Trim')"
        })
    )
