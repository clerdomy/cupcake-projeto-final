# Registra todos os modelos no admin
from django.apps import apps
from django.contrib import admin
from django.core.mail import send_mail
from django.urls import reverse

from core.models import (
    Cart,
    CartItem,
    Categoria,
    Cupcake,
    CupcakeImage,
    CupcakesSistem,
    PoliticaEnvio,
    Profile,
    Review,
    Testimonial,
    NewsletterSubscriber,
    Address,
    Order,
    Contact
)


class DynamicModelAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        """
        Retorna todos os campos do modelo para a exibição da lista.
        """
        return [field.name for field in self.model._meta.get_fields()]

    def get_search_fields(self, request):
        """
        Retorna todos os campos de texto para a pesquisa.
        """
        return [field.name for field in self.model._meta.get_fields() if field.get_internal_type() in ['CharField', 'TextField']]

    def get_list_filter(self, request):
        """
        Retorna todos os campos que são filtros.
        """
        return [field.name for field in self.model._meta.get_fields() if field.get_internal_type() in ['CharField', 'TextField', 'BooleanField', 'DateField', 'DateTimeField']]




admin.site.register(Cart, DynamicModelAdmin)
admin.site.register(CartItem, DynamicModelAdmin)
admin.site.register(CupcakeImage, DynamicModelAdmin)
admin.site.register(CupcakesSistem, DynamicModelAdmin)
admin.site.register(PoliticaEnvio, DynamicModelAdmin)
admin.site.register(Profile, DynamicModelAdmin)
admin.site.register(Review, DynamicModelAdmin)
admin.site.register(Contact, DynamicModelAdmin)
admin.site.register(Order, DynamicModelAdmin)






@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    pass

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at', 'is_active')
    search_fields = ('email',)
    actions = ['send_newsletter']

    def send_newsletter(self, request, queryset):
        for subscriber in queryset.filter(is_active=True):
            unsubscribe_link = request.build_absolute_uri(
                reverse('unsubscribe_newsletter', args=[subscriber.email])
            )
            full_message = f"Este é o conteúdo da newsletter.\n\nPara cancelar a inscrição, clique aqui: {unsubscribe_link}"
            send_mail("Sua Newsletter", full_message, 'clerdomyz@gmail.com', [subscriber.email])
        self.message_user(request, "Newsletters enviadas com sucesso.")
    send_newsletter.short_description = "Enviar newsletter para inscritos selecionados"

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'created_at')
    search_fields = ('user__username', 'content')
    list_filter = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_categoria')



@admin.register(Cupcake)
class CupcakeAdmin(admin.ModelAdmin):
    list_display = ['id', 'titulo', 'preco', 'sale', 'preco_sale', 'quantidade_disponivel']
