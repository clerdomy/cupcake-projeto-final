from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import PAIS

# Create your models here.

class CupcakesSistem(models.Model):
    system_name = models.CharField(max_length=100, verbose_name="Nome do Sistema")
    version = models.CharField(max_length=10, verbose_name="Versão")
    sobre = models.TextField(verbose_name="Sobre Nós", blank=True, null=True)
    description = models.TextField(verbose_name="Descrição", blank=True, null=True)
    launch_date = models.DateField(verbose_name="Data de Lançamento")
    developer = models.CharField(max_length=100, verbose_name="Desenvolvedor")
    support_email = models.EmailField(verbose_name="Email de Suporte", blank=True, null=True)
    active = models.BooleanField(default=True, verbose_name="Ativo")
    last_update = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    logo = models.ImageField(upload_to='logos/', verbose_name="Logo", blank=True, null=True)
    facebook_link = models.URLField(verbose_name="Facebook", blank=True, null=True)
    instagram_link = models.URLField(verbose_name="Instagram", blank=True, null=True)
    twitter_link = models.URLField(verbose_name="Twitter", blank=True, null=True)
    phone_number = models.CharField(max_length=15, verbose_name="Telefone", blank=True, null=True)
    address = models.CharField(max_length=255, verbose_name="Endereço", blank=True, null=True)

    def clean(self, *args, **kwargs):
        if not self.pk and CupcakesSistem.objects.exists():
            raise ValidationError("Só pode haver uma instância de CupcakesSistem.")

    def __str__(self):
        return self.system_name

    class Meta:
        verbose_name = "Sistema de Cupcakes"
        verbose_name_plural = "Sistemas de Cupcakes"



class Contact(models.Model):
    """
    Modelo que representa uma solicitação de contato feita por um usuário no sistema.
    
    Atributos:
        first_name (CharField): O primeiro nome do usuário que entrou em contato.
        email (EmailField): O email de contato fornecido pelo usuário.
        subject (CharField): O assunto do contato.
        message (TextField): A mensagem enviada pelo usuário.
        status (CharField): O status atual da solicitação de contato (pendente, em análise, resolvido).
        is_resolved (BooleanField): Indica se o contato foi resolvido.
        resolved_by (ForeignKey): O usuário que resolveu o contato.
        response (TextField): A resposta dada à solicitação de contato.
        contact_date (DateField): A data em que a solicitação de contato foi enviada.
        resolved_at (DateField): A data em que a solicitação foi resolvida.
    """
    
    first_name = models.CharField(max_length=255, verbose_name="First Name")
    email = models.EmailField(max_length=255, verbose_name="Email Address")
    subject = models.CharField(max_length=255, verbose_name="Subject")
    message = models.TextField(verbose_name="Message")
    
    # Status de contato
    status = models.CharField(max_length=50, default="Pending", choices=[
        ("Pending", "Pending"),
        ("Under Review", "Under Review"),
        ("Resolved", "Resolved")
    ], verbose_name="Contact Status")
    is_resolved = models.BooleanField(default=False, verbose_name="Is Resolved")
    
    # Informações sobre a resolução
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Resolved By")
    response = models.TextField(blank=True, null=True, verbose_name="Response Message")
    
    # Datas
    contact_date = models.DateField(auto_now_add=True, verbose_name="Contact Date")
    resolved_at = models.DateField(blank=True, null=True, verbose_name="Resolution Date")
    
    def __str__(self):
        """
        Retorna uma representação legível do contato, mostrando o nome completo e o assunto.
        """
        return f'{self.first_name}  - {self.subject}'

    def clean(self):
        """
        Validações personalizadas para o modelo Contact.
        
        - Verifica se a data de resolução não é anterior à data de contato.
        - Se o contato for resolvido, verifica se o resolved_by está preenchido.
        """
        # Verifica se a data de resolução é anterior à data de contato
        if self.resolved_at and self.resolved_at < self.contact_date:
            raise ValidationError(
                {'resolved_at': _('The resolution date cannot be before the contact date.')}
            )
        
        # Verifica se o contato está resolvido, mas o resolved_by não foi preenchido
        if self.is_resolved and not self.resolved_by:
            raise ValidationError(
                {'resolved_by': _('A resolver must be assigned when the contact is marked as resolved.')}
            )
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    avatar = models.ImageField(default="profile_images/default.jpeg", upload_to="profile_images")
    bio = models.TextField()

    def __str__(self):
        return self.user.username

# Modelo de Categorias
class Categoria(models.Model):
    nome_categoria = models.CharField(
        max_length=255,
        help_text="Nome da categoria, por exemplo, 'Chocolate', 'Baunilha'.",
    )

    def __str__(self):
        return self.nome_categoria
    
    
# Modelo principal dos Cupcakes
class Cupcake(models.Model):
    titulo = models.CharField(
        max_length=255,
        help_text="Insira o título do cupcake, por exemplo, 'Cupcake de Chocolate'.",
    )
    descricao = models.TextField(
        help_text="Insira uma descrição detalhada do cupcake, incluindo sabor, textura, etc."
    )
    preco = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Preço original do cupcake (use ponto para separar decimais).",
    )
    sale = models.BooleanField(
        default=False,
        help_text="Marque se o cupcake está em promoção.",
    )
    preco_sale = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Preço promocional do cupcake (use ponto para separar decimais). Preenchido apenas se o produto estiver em promoção.",
    )
    quantidade_disponivel = models.IntegerField(
        help_text="Número de unidades disponíveis em estoque."
    )
    sku = models.CharField(
        max_length=100,
        unique=True,
        help_text="Código SKU único para o cupcake.",
    )
    data_lancamento = models.DateField(help_text="Data de lançamento do cupcake.")
    quem_cadastrou = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Usuário que cadastrou o cupcake.",
    )
    esta_em_destaque = models.BooleanField(
        default=False,
        help_text="Marque se o cupcake deve ser destacado na página inicial.",
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name="categoria_cupcakes",
        help_text="A categoria associada a este cupcake.",
    )

    ingrediente = models.TextField(
        help_text="Nome dos ingredientes, por exemplo, 'Açúcar', 'Farinha de Trigo'."
    )

    etiqueta = models.CharField(
        max_length=255,
        help_text="Nome da etiqueta, por exemplo, 'Vegano', 'Sem Glúten'.",
    )

    cobertura = models.CharField(
        max_length=255,
        help_text="Nome da cobertura, por exemplo, 'Chocolate', 'Baunilha', 'Morango'.",
    )

    def __str__(self):
        return self.titulo

    def clean(self):

        if not self.preco_sale:
            self.preco_sale = 0

        if self.sale and not self.preco_sale:
            raise ValidationError(
                "Um preço de promoção deve ser fornecido quando o produto está em promoção."
            )

        if self.preco < self.preco_sale and self.sale:
            raise ValidationError(
                "Um preço de promoção deve ser menor quando o produto está em promoção."
            )

        if self.preco_sale and self.preco_sale < self.preco:
            self.sale = True


class CupcakeImage(models.Model):
    cupcake = models.ForeignKey(
        Cupcake,
        on_delete=models.CASCADE,
        related_name="imagens",
        help_text="O cupcake ao qual esta imagem está associada.",
    )
    normal = models.ImageField(
        upload_to="cupcakes-fotos/",
        help_text="Imagem normal 400 x 400.",
    )
    large_size = models.ImageField(
        upload_to="cupcakes-fotos/large-size",
        help_text="Imagem large 600 x 600.",
        blank=True,
        null=True,
        editable=False,
    )
    small_size = models.ImageField(
        upload_to="cupcakes-fotos/small-size",
        help_text="Imagem small 140 x 140.",
        blank=True,
        null=True,
        editable=False,
    )
    descricao = models.TextField(
        help_text="Descrição ou legenda da imagem.",
        null=True,
        blank=True,
    )

    _processed = models.BooleanField(default=False, editable=False)  # Flag interna

    def clean(self):
        if not self.descricao:
            self.descricao = self.cupcake.descricao

    def __str__(self) -> str:
        return f"{self.pk} Imagem {self.cupcake.titulo} - {self.cupcake.pk}"


# Modelo de Reviews dos Cupcakes
class Review(models.Model):
    cupcake = models.ForeignKey(
        Cupcake,
        on_delete=models.CASCADE,
        related_name="reviews",
        help_text="O cupcake que está sendo avaliado.",
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Usuário que fez a avaliação.",
    )
    avaliacao = models.IntegerField(
        help_text="Avaliação dada ao cupcake (de 1 a 5 estrelas)."
    )
    comentario = models.TextField(help_text="Comentário sobre o cupcake.")
    data = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e hora em que a avaliação foi feita.",
    )

    class Meta:
        unique_together = (('usuario', 'cupcake'), )
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return f"Review {self.avaliacao} estrelas por {self.usuario.username}"


class Endereco(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enderecos', null=True, blank=True)
    pais = models.CharField(max_length=100)
    primeiro_nome = models.CharField(max_length=100)
    ultimo_nome = models.CharField(max_length=100)
    nome_empresa = models.CharField(max_length=100, blank=True, null=True)
    endereco = models.CharField(max_length=255)
    apartamento_sala_unidade = models.CharField(max_length=255, blank=True, null=True)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    cep = models.CharField(max_length=20)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    criar_conta = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.primeiro_nome} {self.ultimo_nome}, {self.cidade}, {self.estado}"


# Modelo de Políticas de Envio
class PoliticaEnvio(models.Model):
    cupcake = models.ForeignKey(
        Cupcake,
        on_delete=models.CASCADE,
        related_name="politicas_envio",
        help_text="O cupcake associado a esta política de envio.",
    )
    politica = models.TextField(
        help_text="Descrição da política de envio para este cupcake."
    )

    def __str__(self):
        return f"Política de envio para {self.cupcake.titulo}"


# Modelo de Item no Carrinho de Compras
class CartItem(models.Model):
    cupcake = models.ForeignKey(
        Cupcake,
        on_delete=models.CASCADE,
        help_text="O cupcake adicionado ao carrinho.",
    )
    quantidade = models.PositiveIntegerField(
        default=1,
        help_text="Quantidade do produto no carrinho.",
    )

    def __str__(self):
        return f"{self.quantidade} x {self.cupcake.titulo}"

    def get_total_price(self):
        if self.cupcake.preco_sale:
            return self.quantidade * self.cupcake.preco_sale
        return self.quantidade * self.cupcake.preco


# Modelo de Carrinho de Compras
class Cart(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Usuário ao qual o carrinho pertence.",
    )
    itens = models.ManyToManyField(CartItem, related_name="carrinho")
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        help_text="Data em que o carrinho foi criado.",
    )

    def __str__(self):
        return f"Carrinho de {self.usuario.username}"

    def get_total(self):
        return sum(item.get_total_price() for item in self.itens.all())



class Address(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Endereço do Usuário",
        null=True,
        blank=True
    )
    country = models.CharField(max_length=100, choices=PAIS.PAIS, default="Brazil")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    street_address = models.CharField(max_length=255)
    apartment_suite = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    order_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.street_address}"



# Modelo de Pedido
class Order(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Usuário que fez o pedido.",
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        help_text="Usuário que fez o pedido.",
    )
    cart = models.OneToOneField(
        Cart,
        on_delete=models.CASCADE,
        help_text="Carrinho associado a este pedido.",
    )
    data_pedido = models.DateTimeField(
        auto_now_add=True,
        help_text="Data em que o pedido foi realizado.",
    )
    
    status = models.CharField(
        max_length=50,
        choices=[
            ('Pendente', 'Pendente'),
            ('Processando', 'Processando'),
            ('Enviado', 'Enviado'),
            ('Entregue', 'Entregue'),
            ('Cancelado', 'Cancelado')
        ],
        default='Pendente',
        help_text="Status do pedido."
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Valor total do pedido."
    )

    # Lógica para criar um pedido
    def create_order( user, address, ):
        # Obtém o carrinho atual do usuário
        cart = Cart.objects.filter(usuario=user).last()
        total = cart.get_total()
        shipping = settings.DEFAULT_SHIPPING(total)
        discount = settings.DEFAULT_DISCOUNT(total)

        total -= discount
        total += shipping


        if cart:
            # Cria o pedido associado ao carrinho
            order = Order.objects.create(usuario=user, cart=cart, total=total, address=address)

            # Desassocia o carrinho do usuário para que ele tenha que criar um novo carrinho
            cart.usuario = User.objects.filter(username="admin").first()
            cart.save()

            return order

        else:
            raise ValueError("No cart available to create an order.")

    def __str__(self):
        return f"Pedido {self.pk} - {self.usuario.username}"
    
    def get_total(self):
        return self.cart.get_total()
    
class Checkout(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="checkout",
        help_text="Pedido associado a este checkout.",
    )
    payment_status = models.CharField(
        max_length=50,
        choices=[
            ('Aguardando pagamento', 'Aguardando pagamento'),
            ('Pago', 'Pago'),
            ('Falha no pagamento', 'Falha no pagamento'),
        ],
        default='Aguardando pagamento',
        help_text="Status do pagamento.",
    )
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('Cartão de Crédito', 'Cartão de Crédito'),
            ('Boleto', 'Boleto'),
            ('Pix', 'Pix'),
            ('Transferência Bancária', 'Transferência Bancária'),
        ],
        help_text="Método de pagamento utilizado.",
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Valor total do pedido.",
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
        help_text="Data em que o checkout foi realizado.",
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="ID da transação de pagamento.",
    )

    def __str__(self):
        return f"Checkout do Pedido #{self.order.id}"

    def process_payment(self, payment_data):
        # Implementar lógica para processar o pagamento
        pass

    def is_payment_successful(self):
        return self.payment_status == 'Pago'




# NewsletterSubscriber

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Campo para indicar se o usuário ainda deseja receber emails
    
    def __str__(self):
        return self.email
    

class Newsletter(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
    
# Testimonial

class Testimonial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Testimonial by {self.user.username}'
    

    def get_profile_picture(self):
        profile = Profile.objects.filter(user=self.user).first()
        if profile and profile.avatar:
            return profile.avatar.url
        return 'assets/images/testimonial/default.jpg'