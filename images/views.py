import os
import subprocess
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from .models import ImageItem, ProcessedVersion
from .forms import UploadForm, ManipulateForm


# === Gallery View ===
def gallery(request):
    """Display all uploaded images."""
    images = ImageItem.objects.all().order_by('-created_at')
    return render(request, 'images/image_list.html', {'images': images})


# === Upload Image ===
def upload_image(request):
    """Upload a new image and redirect to manipulation studio."""
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save()
            return redirect('images:manipulate_image', pk=image_instance.pk)
    else:
        form = UploadForm()
    return render(request, 'images/upload.html', {'form': form})


# === Manipulate Image ===
def manipulate_image(request, pk):
    """
    Apply ImageMagick-based effects and transformations to the selected image.
    Includes color correction, cropping, resizing, flipping, rotating, deskewing, and trimming.
    """
    image_instance = get_object_or_404(ImageItem, pk=pk)
    original_path = image_instance.original.path
    processed_dir = os.path.join(settings.MEDIA_ROOT, 'processed')
    os.makedirs(processed_dir, exist_ok=True)

    modified_filename = f"processed_{image_instance.pk}.png"
    modified_path = os.path.join(processed_dir, modified_filename)
    preview_url = None

    if request.method == 'POST':
        form = ManipulateForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            effect = cd.get('effect', 'none')
            brightness = float(cd.get('brightness', 100))
            contrast = float(cd.get('contrast', 100))
            saturation = float(cd.get('saturate', 100))
            rotate = float(cd.get('rotate', 0))
            blur = float(cd.get('blur', 0))
            opacity = float(cd.get('opacity', 100))
            resize_width = cd.get('resize_width')
            resize_height = cd.get('resize_height')
            crop_left = cd.get('crop_left') or 0
            crop_top = cd.get('crop_top') or 0
            crop_right = cd.get('crop_right') or 0
            crop_bottom = cd.get('crop_bottom') or 0
            deskew = cd.get('deskew')
            trim = cd.get('trim')
            flip_h = cd.get('flip_horizontal')
            flip_v = cd.get('flip_vertical')
            note = cd.get('note') or f"Effect: {effect}"

            # === Start ImageMagick Command ===
            cmd = ['magick', original_path, '-auto-orient']

            # Adjust brightness, contrast, saturation
            cmd += ['-modulate', f'{brightness},{saturation},{contrast}']

            # Rotate
            if rotate:
                cmd += ['-rotate', str(rotate)]

            # Resize
            if resize_width or resize_height:
                resize_geometry = f"{resize_width or ''}x{resize_height or ''}"
                cmd += ['-resize', resize_geometry]

            # Crop
            if any([crop_left, crop_top, crop_right, crop_bottom]):
                width = crop_right - crop_left if crop_right else ''
                height = crop_bottom - crop_top if crop_bottom else ''
                crop_geometry = f"{width}x{height}+{crop_left}+{crop_top}"
                cmd += ['-crop', crop_geometry, '+repage']

            # Deskew
            if deskew:
                cmd += ['-deskew', '40%']

            # Trim
            if trim:
                cmd += ['-trim', '+repage']

            # Flips
            if flip_h:
                cmd += ['-flop']
            if flip_v:
                cmd += ['-flip']

            # Blur
            if blur:
                cmd += ['-blur', f'0x{blur}']

            # Opacity
            if opacity < 100:
                cmd += ['-alpha', 'set', '-channel', 'A', '-evaluate', 'set', f'{opacity}%']

            # === Image Effects Map ===
            effects_map = {
                'grayscale': ['-colorspace', 'Gray'],
                'sepia': ['-sepia-tone', '80%'],
                'invert': ['-negate'],
                'sharpen': ['-sharpen', '0x2'],
                'emboss': ['-emboss', '0x1'],
                'edge': ['-edge', '1'],
                'oilpaint': ['-paint', '4'],
                'charcoal': ['-charcoal', '1'],
                'sketch': ['-sketch', '0x20+120'],
                'solarize': ['-solarize', '50%'],
                'posterize': ['-posterize', '4'],
                'noise': ['-noise', '3'],
                'mirror': ['-flop'],
                'flip': ['-flip'],
                'rotate_left': ['-rotate', '90'],
                'rotate_right': ['-rotate', '-90'],
                'frame': ['-frame', '10x10+3+3'],
                'border': ['-bordercolor', 'black', '-border', '10x10'],
                'vignette': ['-vignette', '0x50'],
                'cartoon': ['-morphology', 'EdgeOut', 'DoG:0,1,0'],
            }

            # Add complex effects
            if effect in effects_map:
                cmd += effects_map[effect]
            elif effect == 'shadow':
                cmd += [
                    '(',
                    '+clone', '-background', 'black',
                    '-shadow', '80x3+5+5',
                    ')',
                    '+swap', '-background', 'none',
                    '-layers', 'merge', '+repage'
                ]
            elif effect == 'glow':
                cmd += [
                    '(',
                    '+clone', '-blur', '0x8',
                    ')',
                    '-compose', 'screen', '-composite'
                ]

            # Output
            cmd.append(modified_path)

            # Run ImageMagick
            MAGICK_PATH = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

            try:
                subprocess.run([MAGICK_PATH] + cmd[1:], check=True)
            except FileNotFoundError:
                return HttpResponse(
                    f"<h3>❌ ImageMagick not found at:</h3><pre>{MAGICK_PATH}</pre>",
                    status=500
                )
            except subprocess.CalledProcessError as e:
                return HttpResponse(f"<h3>⚠️ Processing error:</h3><pre>{e}</pre>", status=500)

            # Save processed version to DB
            rel_path = os.path.join('processed', modified_filename)
            ProcessedVersion.objects.create(item=image_instance, image=rel_path, note=note)
            preview_url = os.path.join(settings.MEDIA_URL, rel_path)
    else:
        form = ManipulateForm()

    processed_versions = ProcessedVersion.objects.filter(item=image_instance).order_by('-created_at')

    return render(request, 'images/manipulate.html', {
        'image': image_instance,
        'form': form,
        'preview_url': preview_url,
        'processed_versions': processed_versions,
    })


# === Delete Image ===
def delete_image(request, pk):
    """Delete an image and its associated processed versions."""
    image_instance = get_object_or_404(ImageItem, pk=pk)

    if request.method == 'POST':
        if image_instance.original and os.path.exists(image_instance.original.path):
            os.remove(image_instance.original.path)

        for version in image_instance.versions.all():
            if version.image and os.path.exists(version.image.path):
                os.remove(version.image.path)

        image_instance.delete()
        return redirect('images:gallery')

    return render(request, 'images/confirm_delete.html', {'image': image_instance})
