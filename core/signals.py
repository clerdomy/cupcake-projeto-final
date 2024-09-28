import hashlib
import os
import string
from random import choices, randint

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from rembg import remove

from core.models import Cupcake, CupcakeImage, Profile, Order
from libs.utils import generate_number


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except:
        Profile.objects.create(user=instance)
    


@receiver(post_save, sender=Cupcake)
def add_default_cupcake_image(sender, instance, created, **kwargs):
    if created:
        # Adiciona uma imagem padrão ao cupcake recém-criado
        CupcakeImage.objects.create(
            cupcake=instance,
            normal="cupcakes-fotos/default_cupcakes.jpeg",  # Caminho para a imagem padrão
            descricao="Imagem padrão",
        )


@receiver(post_save, sender=CupcakeImage)
def resize_and_rename_images(sender, instance, **kwargs):
    # Evita processar novamente se já foi feito uma vez
    if instance._processed:
        return

    if instance.normal:
        image_path = instance.normal.path
        img = Image.open(image_path)

        # Verifica se a imagem normal não está no tamanho 400x400 e redimensiona se necessário
        if img.size != (400, 400):
            img = img.resize((400, 400), Image.Resampling.LANCZOS)

        # Converte para RGB se a imagem for RGBA
        if img.mode == "RGBA":
            img = img.convert("RGB")

        # Renomeia a imagem com a PK do modelo
        code = generate_number()
        normal_img_name = f"cupcake_{instance.pk}_{code}normal.png"
        normal_img_path = os.path.join(os.path.dirname(image_path), normal_img_name)

        # Cria o diretório se não existir
        normal_dir = os.path.dirname(normal_img_path)
        if not os.path.exists(normal_dir):
            os.makedirs(normal_dir)

        # img.save(normal_img_path, format='JPEG')

        # Remover o fundo
        output_image = remove(img)

        # Salvar a imagem sem fundo
        output_image.save(normal_img_path, format="PNG")

        # Atualiza o campo `normal` com o novo caminho
        instance.normal.name = os.path.join("cupcakes-fotos/", normal_img_name)

        # Cria e renomeia a imagem large_size
        large_img = img.resize((600, 600), Image.Resampling.LANCZOS)
        code = generate_number()
        large_img_name = f"cupcake_{instance.pk}_{code}_large.png"
        large_img_path = os.path.join(
            os.path.dirname(image_path),
            "large-size",
            large_img_name,
        )

        # Cria o diretório se não existir
        large_dir = os.path.dirname(large_img_path)
        if not os.path.exists(large_dir):
            os.makedirs(large_dir)

        # large_img.save(large_img_path, format='JPEG')

        # Remover o fundo
        output_image = remove(large_img)

        # Salvar a imagem sem fundo
        output_image.save(large_img_path, format="PNG")

        # Atualiza o campo `large_size` com o novo caminho
        instance.large_size.name = os.path.join(
            "cupcakes-fotos/large-size", large_img_name
        )

        # Cria e renomeia a imagem small_size
        small_img = img.resize((140, 140), Image.Resampling.LANCZOS)
        code = generate_number()
        small_img_name = f"cupcake_{instance.pk}_{code}_small.png"
        small_img_path = os.path.join(
            os.path.dirname(image_path),
            "small-size",
            small_img_name,
        )

        # Cria o diretório se não existir
        small_dir = os.path.dirname(small_img_path)
        if not os.path.exists(small_dir):
            os.makedirs(small_dir)

        # small_img.save(small_img_path, format='JPEG')

        # Remover o fundo
        output_image = remove(small_img)

        # Salvar a imagem sem fundo
        output_image.save(small_img_path, format="PNG")

        # Atualiza o campo `small_size` com o novo caminho
        instance.small_size.name = os.path.join(
            "cupcakes-fotos/small-size", small_img_name
        )

        # Remove a imagem original
        if os.path.exists(image_path):
            if image_path.split("\\cupcakes-fotos\\")[-1] != "default_cupcakes.jpeg":
                os.remove(image_path)

        # Sinaliza que o processamento foi feito
        instance._processed = True
        instance.save()
