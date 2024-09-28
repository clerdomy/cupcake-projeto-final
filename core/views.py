# Bibliotecas padrão
import json
import logging
import os
import re
from datetime import datetime
from urllib.parse import quote

# Bibliotecas do Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


from libs import utils
from core.models import (
    Review,
    Testimonial,
    NewsletterSubscriber,
    Cart,
    CartItem,
    Categoria,
    Order,
    Address,
    Cupcake,
    CupcakeImage,
    CupcakesSistem,
)


from core.forms import(
    NewsletterForm, 
    AddressForm,
    ContactForm,
    AccountDetailsForm,
    ProfileForm,
    CustomPasswordChangeForm
)

logger = logging.getLogger('django')


@login_required
def register_rating(request):
    """
    Manipula o registro de uma avaliação de cupcake por um usuário autenticado.

    Esta view trata requisições POST para enviar uma avaliação e um comentário para 
    um cupcake específico. O ID do cupcake, a avaliação e o comentário são fornecidos 
    através dos dados da requisição POST. Se o usuário já tiver enviado uma avaliação 
    para o cupcake selecionado, uma mensagem de erro será retornada. Caso contrário, 
    a avaliação é salva, e uma mensagem de sucesso é enviada na resposta.

    A resposta é retornada como um objeto JSON indicando se a avaliação foi salva 
    com sucesso ou se ocorreu um erro.

    Parâmetros:
    request (HttpRequest): O objeto de requisição HTTP contendo o ID do cupcake, 
                           a avaliação e o comentário nos dados POST.

    Retorna:
    HttpResponse: Uma resposta JSON contendo a mensagem (sucesso ou descrição do erro) 
                  e o resultado ("success" ou "error").

    Estrutura da Resposta JSON:
    {
        "msg": str,  # Mensagem indicando o resultado (sucesso ou descrição do erro)
        "result": str  # Status do resultado: "success" se a avaliação foi salva, "error" caso contrário
    }

    Exceções:
    - Cupcake.DoesNotExist: Lançada se o cupcake com o ID fornecido não for encontrado.
    - Qualquer outra exceção será capturada e registrada para fins de depuração.

    Observações:
    - A função requer que o usuário esteja autenticado (decorador `@login_required`).
    - Se o método da requisição não for POST, nenhuma avaliação será enviada.
    """

    context = {"msg": "", "result": "error"}

    if request.method == "POST":
        cupcake_id = int(request.POST.get("cupcake_id"))
        avaliacao = int(request.POST.get("rating"))
        comentario = request.POST.get("comentario")

        try:
            cupcake = Cupcake.objects.get(id=cupcake_id)

            # Verifica se o usuário já fez uma avaliação para este cupcake
            if Review.objects.filter(cupcake=cupcake, usuario=request.user).exists():
                context["msg"] = "Você já avaliou este cupcake."
            else:
                review = Review.objects.create(
                    cupcake=cupcake,
                    usuario=request.user,
                    avaliacao=avaliacao,
                    comentario=comentario,
                )
                context["msg"] = "Avaliação registrada com sucesso!"
                context["result"] = "success"
                logger.info("Avaliação registrada com sucesso!", review.cupcake.titulo, review.usuario.username, avaliacao)

        except Cupcake.DoesNotExist:
            context["msg"] = "O cupcake selecionado não foi encontrado."
            logger.warning(f"Erro: Cupcake com ID {cupcake_id} não encontrado.")
        except ValueError:
            context["msg"] = "Valores inválidos fornecidos."
            logger.error("Erro de conversão de tipos nos dados POST.")
        except Exception as e:
            context["msg"] = "Ocorreu um erro ao registrar a avaliação."
            logger.exception(f"Erro inesperado ao registrar avaliação: {e}")
    response = f"{json.dumps(context)}"
    return HttpResponse(response, content_type="application/javascript")

@login_required
def home(request):
    """
    Renderiza a página inicial com cupcakes em destaque e depoimentos de clientes.

    Esta view recupera os cupcakes que estão marcados como destaque e seus 
    respectivos dados de avaliação e imagens associadas, além de exibir os depoimentos 
    dos clientes. Os cupcakes em destaque são agrupados em pares para exibição no frontend. 
    A view é acessível apenas para usuários autenticados.

    Parâmetros:
    request (HttpRequest): O objeto de requisição HTTP.

    Retorna:
    HttpResponse: Renderiza a página inicial ('index.html') com os seguintes dados no contexto:
                  - "home_featured_products": Lista de cupcakes em destaque com suas imagens e avaliações médias.
                  - "countdown_date": Data atual no formato "YYYY/MM/DD" usada para algum contador na página.
                  - "testimonials": Lista de depoimentos de clientes.
                  - "home_featured_products_grouped": Cupcakes em destaque agrupados em pares para exibição.

    Comportamento:
    - Recupera todos os cupcakes que estão em destaque.
    - Para cada cupcake, busca as imagens associadas e calcula a avaliação média.
    - Adiciona os cupcakes e suas imagens ao contexto da página.
    - Agrupa os cupcakes em pares para exibição organizada no frontend.
    - Recupera e exibe todos os depoimentos de clientes.
    
    Observações:
    - A função requer que o usuário esteja autenticado (decorador `@login_required`).
    - O agrupamento de cupcakes facilita a exibição em seções de 2 itens no frontend.
    """

    try:
        # Obtendo depoimentos
        testimonials = Testimonial.objects.all()
        logger.info(f"Carregados {testimonials.count()} depoimentos.")

        context = {
            "home_featured_products": [],
            "countdown_date": datetime.today().strftime("%Y/%m/%d"),
            "testimonials": testimonials,
        }

        # Filtrando cupcakes em destaque
        cupcake_em_destaque = Cupcake.objects.filter(esta_em_destaque=True)
        logger.info(f"Encontrados {cupcake_em_destaque.count()} cupcakes em destaque.")

        for cupcake in cupcake_em_destaque:
            # Obtendo imagens do cupcake
            imagens = CupcakeImage.objects.filter(cupcake=cupcake)
            imagem_urls = [imagem.normal.url for imagem in imagens]
            
            # Calculando a média de avaliações
            cupcake.media_rating = utils.cupcake_rating_median(cupcake)
            logger.debug(f"Cupcake {cupcake.titulo} tem média de avaliação {cupcake.media_rating}.")

            # Adicionando cupcake ao contexto
            context["home_featured_products"].append(
                {"cupcake": cupcake, "imagens": imagem_urls}
            )

        # Agrupando produtos em pares
        context["home_featured_products_grouped"] = [
            context["home_featured_products"][i : i + 2]
            for i in range(0, len(context["home_featured_products"]), 2)
        ]

        logger.info(f"Home page carregada com {len(context['home_featured_products'])} cupcakes em destaque.")
        
    except Exception as e:
        # Registrando qualquer erro que ocorrer
        logger.exception(f"Erro ao carregar a página home: {e}")

    return render(request, "cupcakes/index.html", context)

@login_required
def shop(request):
    # Obtém todos os cupcakes e suas imagens associadas
    data_GET = request.GET
    data_POST = request.POST

    cupcakes = Cupcake.objects.all().prefetch_related("imagens")
    categorias = Categoria.objects.all().prefetch_related("categoria_cupcakes")

     # Verifica se há um termo de pesquisa enviado via get
    search_query = data_GET.get('search_query', '').strip()
    
    if search_query:
        # Filtra os cupcakes pelo título que contenha o termo de pesquisa
        cupcakes = cupcakes.filter(titulo__icontains=search_query)

    for cupcake in cupcakes:
        cupcake.media_rating = utils.cupcake_rating_median(cupcake)

    # Define o critério de ordenação baseado nos valores do formulário
    sort_by = data_GET.get('sort_by', '1')  # O valor padrão é '1' (Alfabeticamente, A-Z)
    
    if sort_by == '1':
        cupcakes = cupcakes.order_by('titulo')  # Alfabeticamente, A-Z
    elif sort_by == '2':
        cupcakes = cupcakes.order_by('-esta_em_destaque')  # Ordenar por popularidade
    elif sort_by == '3':
        cupcakes = cupcakes.order_by('-data_lancamento')  # Ordenar por novidades
    elif sort_by == '4':
        cupcakes = cupcakes.order_by('preco_sale')  # Ordenar por preço: baixo para alto
    elif sort_by == '5':
        cupcakes = cupcakes.order_by('-preco')  # Ordenar por preço: alto para baixo
    elif sort_by == '6':
        cupcakes = cupcakes.order_by('-titulo')  # Nome do Produto: Z-A
    

    # Filtragem por categoria
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        cupcakes = cupcakes.filter(categoria__id=categoria_id)

    # Filtragem por cupcake específico (opcional)
    cupcake_titulo = request.GET.get('cupcake')
    if cupcake_titulo:
        cupcakes = cupcakes.filter(titulo=cupcake_titulo)
    # Paginação
    page_number = request.GET.get('page', 1)  # Pega o número da página atual (1 é o padrão)
    paginator = Paginator(cupcakes, 6)  # Pagina com 6 cupcakes por página

    # Obtém a página atual
    page_obj = paginator.get_page(page_number)

    # Renderiza o template com os dados paginados
    return render(
        request,
        "cupcakes/shop.html",
        {
            "cupcakes": page_obj.object_list,  # Cupcakes da página atual
            "categorias": categorias,
            "search_query": search_query,
            "page_obj": page_obj,  # Página para controle de navegação
        },
    )

@login_required
def product_details(request, id):
    """
    Exibe os detalhes de um produto específico (cupcake) para o usuário autenticado.

    Esta view trata uma requisição GET para carregar os detalhes de um cupcake com base em seu ID. 
    Ela também verifica se o usuário atual já enviou uma avaliação para o cupcake. Além disso, 
    exibe uma lista de cupcakes em destaque na página.

    Parâmetros:
    request (HttpRequest): O objeto de requisição HTTP.
    id (int): O ID do cupcake a ser exibido.

    Retorna:
    HttpResponse: A página de detalhes do produto com informações sobre o cupcake e avaliações.
    
    Exceções:
    - Cupcake.DoesNotExist: Lançada se o cupcake com o ID fornecido não for encontrado.
    - Qualquer outra exceção será capturada e registrada para fins de depuração.
    
    Observações:
    - A função requer que o usuário esteja autenticado (decorador `@login_required`).
    """
    
    context = {"product": [], "home_featured_products": [], "user_has_rating": False}
    
    try:
        # Obtendo as avaliações e verificando se o usuário já fez uma
        reviews = utils.cupcake_rating(id)
        logger.info(f"Avaliações carregadas para o cupcake {id}.")
        
        if reviews["reviews"]:
            user_has_rating = bool(
                [
                    r
                    for r in reviews["reviews"]
                    if r.usuario.username == request.user.username
                ]
            )
            context["user_has_rating"] = user_has_rating

        context.update(reviews)

        # Obtendo o cupcake pelo ID
        cupcake = get_object_or_404(Cupcake, id=id)
        logger.info(f"Cupcake {cupcake.titulo} (ID: {id}) carregado.")

        # Obtendo imagens do cupcake
        imagens = CupcakeImage.objects.filter(cupcake=cupcake)
        normal = [imagem.normal.url for imagem in imagens]
        large_size = [imagem.large_size.url for imagem in imagens]
        small_size = [imagem.small_size.url for imagem in imagens]

        # Calculando a média de avaliações
        cupcake.media_rating = utils.cupcake_rating_median(cupcake)
        logger.debug(f"Cupcake {cupcake.titulo} tem média de avaliação {cupcake.media_rating}.")

        # Adicionando detalhes ao contexto
        context["product"].append(
            {
                "cupcake": cupcake,
                "normal": normal,
                "large_size": large_size,
                "small_size": small_size,
            }
        )

        # Cupcakes em destaque
        cupcake_em_destaque = Cupcake.objects.filter(esta_em_destaque=True)
        logger.info(f"Carregados {cupcake_em_destaque.count()} cupcakes em destaque.")

        for cupcake in cupcake_em_destaque:
            imagens = CupcakeImage.objects.filter(cupcake=cupcake)
            imagem_urls = [imagem.normal.url for imagem in imagens]
            cupcake.media_rating = utils.cupcake_rating_median(cupcake)

            context["home_featured_products"].append(
                {"cupcake": cupcake, "imagens": imagem_urls}
            )

    except Cupcake.DoesNotExist:
        logger.error(f"Cupcake com ID {id} não encontrado.")
        context["error"] = "O cupcake selecionado não foi encontrado."
    except Exception as e:
        logger.exception(f"Erro ao carregar os detalhes do produto {id}: {e}")
        context["error"] = "Ocorreu um erro ao carregar os detalhes do produto."

    return render(
        request,
        "cupcakes/product-details.html",
        context=context,
    )

# Cart

@login_required
def cart_view(request):
    try:
        carrinho = Cart.objects.get(usuario=request.user)
        carrinho.total =  carrinho.get_total()
        carrinho.shipping = settings.DEFAULT_SHIPPING(carrinho.total)
        carrinho.discount = settings.DEFAULT_DISCOUNT(carrinho.total)
        carrinho.total +=  carrinho.shipping
        carrinho.total -= carrinho.discount
    except Cart.DoesNotExist:
        carrinho = None

    return render(request, "cupcakes/cart.html", {"carrinho": carrinho})

@login_required
def adicionar_ao_carrinho(request, cupcake_id):
    """
    Adiciona um cupcake ao carrinho de compras do usuário autenticado.

    Esta view permite que o usuário adicione um cupcake específico ao seu carrinho de compras. 
    Se o cupcake já estiver no carrinho, sua quantidade será atualizada com o valor especificado. 
    Caso contrário, um novo item será criado e adicionado ao carrinho. 

    Parâmetros:
    request (HttpRequest): O objeto de requisição HTTP contendo os dados do cupcake a ser adicionado e a quantidade.
    cupcake_id (int): O ID do cupcake que será adicionado ao carrinho.

    Retorna:
    HttpResponse: Redireciona o usuário para a página do carrinho ('cart-page') após adicionar o cupcake.

    Comportamento:
    - Recupera o cupcake a ser adicionado usando o ID fornecido. Se o cupcake não for encontrado, uma página 404 é exibida.
    - Recupera ou cria um carrinho para o usuário autenticado.
    - Verifica se o cupcake já está presente no carrinho:
        - Se o cupcake já estiver no carrinho, a quantidade é atualizada com o valor especificado.
        - Se o cupcake não estiver no carrinho, um novo item é criado e adicionado ao carrinho.
    - Redireciona o usuário para a página do carrinho após a atualização ou criação do item.

    Observações:
    - Apenas usuários autenticados podem acessar esta view, garantindo que cada usuário possa gerenciar seu próprio carrinho.
    - Se o `cupcake_id` fornecido não corresponder a um cupcake existente, a função retorna uma página 404.
    """

    cupcake = get_object_or_404(Cupcake, id=cupcake_id)
    usuario = request.user
    quantities = int(request.POST.get("quantities"))

    # Recupera ou cria um carrinho para o usuário
    carrinho, created = Cart.objects.get_or_create(usuario=usuario)

    # Verifica se o item já está no carrinho
    item_existente = carrinho.itens.filter(cupcake=cupcake).first()

    if item_existente:
        # Se já existe, aumenta a quantidade
        item_existente.quantidade = quantities
        item_existente.save()
    else:
        # Se não existe, cria um novo item no carrinho
        novo_item = CartItem.objects.create(cupcake=cupcake, quantidade=quantities)
        carrinho.itens.add(novo_item)

    return redirect("cart-page")  # Redireciona para a página do carrinho

@require_POST
def atualizar_carrinho(request):
    """
    Atualiza o carrinho de compras do usuário.

    Esta view é responsável por processar a atualização do carrinho de compras. Atualmente, 
    ela simplesmente redireciona o usuário para a página do carrinho sem realizar nenhuma 
    operação adicional. A função está configurada para aceitar apenas requisições POST.

    Parâmetros:
    request (HttpRequest): O objeto de requisição HTTP. Para esta view, espera-se que a requisição seja do tipo POST.

    Retorna:
    HttpResponse: Redireciona o usuário para a página do carrinho ('cart-page').

    Comportamento:
    - A função não realiza nenhuma atualização efetiva no carrinho. Apenas redireciona o usuário para a página do carrinho.

    Observações:
    - O decorador `@require_POST` garante que a função só seja acessível via requisições POST.
    """

    return redirect("cart-page")

@csrf_exempt
@login_required
def atualizar_quantidade_carrinho(request):
    """
    Atualiza a quantidade de um item específico no carrinho de compras do usuário.

    Esta view processa a atualização da quantidade de um item no carrinho com base nos dados 
    recebidos via requisição POST em formato JSON. A função é protegida contra CSRF e requer 
    que o usuário esteja autenticado. Se a atualização for bem-sucedida, o subtotal do item é 
    retornado como resposta JSON. Se o item não for encontrado ou ocorrer um erro, uma mensagem 
    de erro é retornada.

    Parâmetros:
    request (HttpRequest): O objeto de requisição HTTP contendo os dados do item a ser atualizado em formato JSON.

    Retorna:
    JsonResponse: 
    - Se a atualização for bem-sucedida, retorna um JSON com "success": True e o "subtotal" atualizado do item.
    - Se o item não for encontrado, retorna um JSON com "success": False e uma mensagem de erro "Item não encontrado".
    - Se mais de um item for encontrado com o mesmo ID, retorna um JSON com "success": False e uma mensagem de erro "Mais de um item encontrado com o mesmo ID."
    - Se o método da requisição não for POST, retorna um JSON com "success": False e uma mensagem de erro "Método não permitido".

    Comportamento:
    - Carrega os dados da requisição POST em formato JSON.
    - Recupera o item do carrinho pelo ID fornecido e atualiza sua quantidade.
    - Calcula o subtotal do item e retorna a resposta JSON com o resultado.
    - Trata exceções para item não encontrado e múltiplos itens encontrados com o mesmo ID.
    - Responde com erro se o método não for POST.

    Observações:
    - O decorador `@csrf_exempt` desativa a proteção CSRF para esta view, permitindo requisições sem token CSRF.
    - O decorador `@login_required` garante que apenas usuários autenticados possam acessar esta view.
    """

    if request.method == "POST":
        data = json.loads(request.body)
        item_id = int(data.get("item_id"))
        quantidade = int(data.get("quantity"))

        try:
            # Assumindo que o 'item_id' é o ID do item no carrinho
            item = CartItem.objects.get(id=item_id)
            item.quantidade = quantidade
            item.save()
            total_price = item.get_total_price()
            return JsonResponse({"success": True, "subtotal": total_price})
        except CartItem.DoesNotExist:
            return JsonResponse({"success": False, "error": "Item não encontrado"})
        except CartItem.MultipleObjectsReturned:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Mais de um item encontrado com o mesmo ID.",
                }
            )
    return JsonResponse({"success": False, "error": "Método não permitido"})

@login_required
def remover_item_do_carrinho(request, item_id):
    """
    Remove um item do carrinho de compras do usuário autenticado.

    Esta view lida com a remoção de um item específico do carrinho de compras do usuário. 
    Se o item existir no carrinho, ele será removido e excluído do banco de dados. 
    Após a remoção, o usuário é redirecionado para a página do carrinho.

    Parâmetros:
    request (HttpRequest): O objeto de requisição HTTP.
    item_id (int): O ID do item que será removido do carrinho.

    Retorna:
    HttpResponse: Redireciona o usuário para a página do carrinho ('cart-page') após a remoção do item.

    Comportamento:
    - Tenta recuperar o carrinho do usuário autenticado.
    - Se o carrinho e o item forem encontrados, o item é removido do carrinho e excluído do banco de dados.
    - Caso o carrinho ou o item não sejam encontrados, a exceção é tratada silenciosamente (nenhuma ação adicional é tomada).
    - Redireciona o usuário de volta para a página do carrinho após o processamento.

    Observações:
    - Apenas usuários autenticados podem acessar esta view, garantindo que cada usuário só possa manipular seu próprio carrinho.
    - Se o item ou o carrinho não existirem, a função não gera erros visíveis ao usuário (o erro é tratado com `pass`).
    """

    try:
        carrinho = Cart.objects.get(usuario=request.user)
        item = carrinho.itens.get(id=item_id)
        carrinho.itens.remove(item)
        item.delete()
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        pass

    return redirect("cart-page")

@login_required
def aplicar_cupom(request):
    coupon_code = request.POST.get("coupon_code")
    # Aqui você deve implementar a lógica para validar e aplicar o cupom.
    # Isso pode incluir a verificação de validade do cupom, aplicação de desconto, etc.
    # Por simplicidade, vamos apenas redirecionar para o carrinho.
    return redirect("cart-page")

@login_required
def process_checkout(request, id=None):

    context = {"form": AddressForm(), "saved_address": ""}

    # procurar address
    user_address = Address.objects.filter(usuario=request.user).first()
    context["saved_address"] = user_address

    if not user_address:
        if request.method == "POST":
            form = AddressForm(request.POST)
            if form.is_valid():
                address = form.save(commit=False)
                address.usuario = (
                    request.user
                )  # Associe o endereço ao usuário autenticado
                address.save()
                # Redirecionar para uma página de sucesso ou confirmação
                del address
                return redirect("process_checkout")
    else:
        try:
            # Obtém o carrinho do usuário
            cart = Cart.objects.get(usuario=request.user)
        except Exception as ex:
            print(ex)
            cart = None
            # return redirect('cart-page')

        # Obtém o endereço do usuário
        if not user_address:
            return redirect("process_checkout")

        order = None

        if cart:
            if cart.itens.count() > 0:
                # Cria a ordem/pedido
                order = Order.create_order(user=request.user, address=user_address)
            else:
                return redirect("cart-page")

        if not order:
            try:
                if id:
                    order = Order.objects.get(id=id)
                else:
                    order = Order.objects.filter(status="Pendente").last()
            except Exception as ex:
                print(ex)

        if not order:
            return redirect("cart-page")

        produtos = [
            {
                "titulo": produto.cupcake.titulo,
                "quantidade": produto.quantidade,
                "total_preco": produto.get_total_price(),
            }
            for produto in order.cart.itens.all()
        ]
        order.produtos = produtos
        order.shipping = settings.DEFAULT_SHIPPING(order.cart.get_total())
        order.discount = settings.DEFAULT_DISCOUNT(order.cart.get_total()) 
        # Após criar a ordem, o carrinho pode ser limpo ou marcado como finalizado
        # Pode-se optar por deletar os itens do carrinho, ou marcar o carrinho como finalizado

        context["order"] = order

    # Redireciona o usuário para uma página de confirmação do pedido
    return render(request, "cupcakes/checkout.html", context=context)

@login_required
def registe_address(request):
    """
    Exibe e processa o formulário de registro de endereço para o usuário autenticado.

    Esta view permite que um usuário autenticado registre ou visualize seu endereço 
    no sistema. Se o usuário já tiver um endereço cadastrado, ele será exibido na página. 
    Caso contrário, um formulário será exibido para que o usuário possa registrar 
    um novo endereço. O formulário é processado apenas quando a requisição for POST, 
    e o endereço é associado ao usuário autenticado.

    Parâmetros:
    request (HttpRequest): O objeto de requisição HTTP.

    Retorna:
    HttpResponse: Renderiza a página de checkout ('checkout.html') com os seguintes dados no contexto:
                  - "form": O formulário de registro de endereço, seja em branco ou preenchido.
                  - "address": O endereço já existente do usuário, se houver.

    Comportamento:
    - Se o usuário já possui um endereço cadastrado, ele é exibido na página.
    - Se o usuário não tiver endereço e o método da requisição for POST, o formulário 
      de registro de endereço é processado.
    - O formulário é validado e, se for válido, o novo endereço é salvo e associado 
      ao usuário autenticado.
    
    Observações:
    - A função utiliza o decorador `@login_required`, o que significa que apenas 
      usuários autenticados podem acessar a página.
    - Se o formulário for submetido e for válido, o endereço é salvo, mas não há um 
      redirecionamento explícito para uma página de sucesso ou confirmação após o salvamento.
    """

    context = {"form": AddressForm(), "address": ""}

    # procurar address
    user_address = Address.objects.filter(usuario=request.user).first()
    context["address"] = user_address
    if not user_address:
        if request.method == "POST":
            form = AddressForm(request.POST)
            if form.is_valid():
                address = form.save(commit=False)
                address.usuario = (
                    request.user
                )  # Associe o endereço ao usuário autenticado
                address.save()
                context["form"] = form

                # Redirecionar para uma página de sucesso ou confirmação

    return render(request, "cupcakes/checkout.html", context=context)

@login_required
def edit_address(request, token, id):
    user = request.user
    expected_token = utils.generate_user_token(user.username)

    if token != expected_token:
        return redirect(
            "error404-page"
        )  # Se o token não corresponder ao usuário, redirecione para erro.

    order = Order.objects.filter(status="Pendente").first()

    if not order:
        return redirect("cart-page")

    produtos = [
        {
            "titulo": produto.cupcake.titulo,
            "quantidade": produto.quantidade,
            "total_preco": produto.get_total_price(),
        }
        for produto in order.cart.itens.all()
    ]
    order.produtos = produtos
    order.shipping = settings.DEFAULT_SHIPPING(order.cart.get_total())
    order.discount = settings.DEFAULT_DISCOUNT(order.cart.get_total()) 

    # Após criar a ordem, o carrinho pode ser limpo ou marcado como finalizado
    # Pode-se optar por deletar os itens do carrinho, ou marcar o carrinho como finalizado

    context = {"order": order}

    address = get_object_or_404(Address, id=id)
    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect("process_checkout")
    else:
        form = AddressForm(instance=address)

    context.update({"form": form})
    return render(request, "cupcakes/edit_address.html", context=context)

@login_required
def delete_address(request, id):
    """
    Exclui o endereço do usuário autenticado.

    Esta view lida com a exclusão de um endereço associado ao usuário autenticado. 
    Se o método da requisição for POST, o endereço especificado será excluído do banco de dados. 
    Caso contrário, uma página de confirmação será exibida.

    Parâmetros:
    request (HttpRequest): O objeto de requisição HTTP.
    id (int): O ID do endereço que será excluído.

    Retorna:
    HttpResponse: 
    - Se o método for POST, redireciona o usuário para a página de checkout após a exclusão do endereço.
    - Se o método for GET, renderiza a página de confirmação de exclusão ('delete_address.html') com os seguintes dados no contexto:
        - "address": O endereço a ser excluído, recuperado pelo ID.

    Comportamento:
    - Busca o endereço pelo ID. Se o endereço não for encontrado, uma página 404 será exibida.
    - Se o método for POST, o endereço é excluído do banco de dados e o usuário é redirecionado para a página de checkout.
    - Se o método for GET, uma página de confirmação é exibida com os detalhes do endereço a ser excluído.

    Observações:
    - Apenas usuários autenticados podem acessar esta view, graças ao decorador `@login_required`.
    - A exclusão do endereço só ocorre após a confirmação via requisição POST.
    """

    address = get_object_or_404(Address, id=id)
    if request.method == "POST":
        address.delete()
        return redirect("process_checkout")
    return render(request, "cupcakes/delete_address.html", {"address": address})

def contact_us(request):
    form = ContactForm()
    context = {"form": form, "alert": {"msg": "", "alert": "error"}}
    context["sistem"] = CupcakesSistem.objects.filter().last()

    if request.method == "POST":
        try:
            form = ContactForm(request.POST)
            if form.is_valid():
                form.save()
                # Redirecionar para uma página de sucesso ou a mesma página sem duplicar o formulário
                return redirect(
                    "contact-us-success"
                )  # Crie uma URL para uma página de sucesso
        except Exception as ex:
            print(ex)
            return redirect("redirect-to-contact-page")

        context["alert"]["msg"] = "Please correct the errors in the form."
        context["alert"]["alert"] = "error"

    return render(request, "cupcakes/contact-us.html", context=context)

def contact_us_success(request):
    return render(request, "cupcakes/contact-us-success.html")

def contact_redirect(request):
    return render(request, "cupcakes/contact-redirect.html")

@login_required
def about_us(request):
    """
    Exibe a página "Sobre Nós" do site.

    Esta view renderiza a página "Sobre Nós" do site, fornecendo informações sobre a empresa ou a equipe.

    Parâmetros:
    request (HttpRequest): O objeto de requisição HTTP que contém os dados da requisição.

    Retorna:
    HttpResponse: Renderiza e retorna a resposta com o template "cupcakes/about-us.html".

    Comportamento:
    - A função renderiza a página "Sobre Nós" com o template especificado.

    Observações:
    - O decorador `@login_required` garante que apenas usuários autenticados possam acessar esta página.
    """

    return render(request, "cupcakes/about-us.html")

# @login_required
def error404(request):
    """
    Exibe a página de erro 404.

    Esta view renderiza uma página de erro 404, que é exibida quando a página solicitada não é encontrada.

    Parâmetros:
    request (HttpRequest): O objeto de requisição HTTP que contém os dados da requisição.

    Retorna:
    HttpResponse: Renderiza e retorna a resposta com o template "404.html".

    Comportamento:
    - A função renderiza a página de erro 404 com o template especificado.

    Observações:
    - O decorador `@login_required` está comentado, o que significa que a página de erro 404 pode ser acessada por todos os usuários, não apenas pelos autenticados.
    """

    return render(request, "404.html")

def get_image(request, page, _type, name):
    """
    Retorna uma imagem do sistema de arquivos com base nos parâmetros fornecidos.

    Esta view serve imagens armazenadas no servidor, determinando o caminho da imagem com base 
    nos parâmetros fornecidos (`page`, `_type`, e `name`). Se a imagem existir, ela é retornada 
    como uma resposta HTTP com o tipo de conteúdo adequado. Caso contrário, um erro 404 é gerado.

    Parâmetros:
    request (HttpRequest): O objeto de requisição HTTP que contém os dados da requisição.
    page (str): O subdiretório da pasta onde a imagem está armazenada. Se for "null", a imagem é buscada na pasta principal.
    _type (str): O tipo de imagem ou subdiretório dentro da pasta `page`.
    name (str): O nome do arquivo da imagem.

    Retorna:
    HttpResponse: 
    - Se a imagem existir, retorna uma resposta HTTP contendo a imagem com o tipo de conteúdo "image/jpeg" e o nome do arquivo como disposição de conteúdo.
    - Se a imagem não for encontrada, gera uma exceção `Http404` com a mensagem "Image not found".

    Comportamento:
    - Constrói o caminho do arquivo da imagem com base nos parâmetros fornecidos e no diretório de mídia configurado.
    - Verifica se o caminho da imagem existe.
    - Se a imagem for encontrada, lê o arquivo e o retorna como uma resposta HTTP com o tipo de conteúdo apropriado.
    - Se a imagem não for encontrada, lança um erro 404.

    Observações:
    - O tipo de conteúdo é fixado como "image/jpeg". Se outros tipos de imagem forem suportados, o tipo de conteúdo deve ser ajustado dinamicamente.
    """

    if page != "null":
        image_path = os.path.join(settings.MEDIA_ROOT, page, _type, name)
    else:
        image_path = os.path.join(settings.MEDIA_ROOT, _type, name)

    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            response = HttpResponse(image_file.read(), content_type="image/jpeg")
            response["Content-Disposition"] = f"inline; filename={quote(name)}"
            return response
    else:
        raise Http404("Image not found")


# Newsletter


def subscribe_newsletter(request):
    context = {
        "result": "error",
        "msg": "Houve um erro ao tentar inscrevê-lo. Por favor, tente novamente.",
    }
    try:
        email = request.GET.get("EMAIL")
        email_is_valid = utils.validar_email(email)
        if email_is_valid:
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email
            )
            if not created and subscriber.is_active:
                context["result"] = "success"
                context["msg"] = "Você já está inscrito na nossa newsletter."
            else:
                subscriber.is_active = True
                subscriber.save()
                context["msg"] = "Você foi inscrito com sucesso na nossa newsletter!"
                context["result"] = "success"
        else:
            context["msg"] = f"'{email}' não é um e-mail válido."

    except Exception as ex:
        print(ex)
    callback = request.GET.get("callback")
    if callback:
        response = f"{callback}({json.dumps(context)})"
        return HttpResponse(response, content_type="application/javascript")
    return JsonResponse(context)

def unsubscribe_newsletter(request, email):
    try:
        subscriber = NewsletterSubscriber.objects.get(email=email)
        subscriber.is_active = False
        subscriber.save()
        messages.success(request, "Você cancelou sua inscrição com sucesso.")
    except NewsletterSubscriber.DoesNotExist:
        messages.error(request, "Este email não está inscrito na nossa newsletter.")

    return redirect("home-page")

def send_newsletter_view(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save()
            subscribers = NewsletterSubscriber.objects.filter(is_active=True)
            sistem = CupcakesSistem.objects.first()

            for subscriber in subscribers:
                unsubscribe_link = request.build_absolute_uri(
                    reverse("unsubscribe_newsletter", args=[subscriber.email])
                )
                full_message = f"{newsletter.message}\n\nPara cancelar sua inscrição, clique aqui: {unsubscribe_link}"
                send_mail(
                    newsletter.subject,
                    full_message,
                    sistem.support_email,
                    [subscriber.email],
                )

            messages.success(request, "Newsletter enviada com sucesso!")
            return redirect("send_newsletter")
    else:
        form = NewsletterForm()

    return redirect("home-page")


# User accounts

@login_required
def my_account(request):
    context = {}
    orders = Order.objects.filter(usuario=request.user)

    context.update({"form": AddressForm(), "address": ""})

    # Formulário de detalhes da conta
    if request.method == "POST" and 'old_password' in request.POST:
        user_form = AccountDetailsForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        if user_form.is_valid():
            user_form.save()
        if profile_form.is_valid():
            profile_form.save()
        if password_form.is_valid():
            password_form.save()

        update_session_auth_hash(request, request.user)  # Mantém o usuário logado após mudar a senha
        return redirect('user_account-page')
    else:
        user_form = AccountDetailsForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        password_form = CustomPasswordChangeForm(user=request.user)

    context.update({
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form
    })

    # procurar address
    user_address = Address.objects.filter(usuario=request.user).first()
    context["address"] = user_address
    if not user_address:
        if request.method == "POST":
            form = AddressForm(request.POST)
            if form.is_valid():
                address = form.save(commit=False)
                address.usuario = (request.user)  # Associe o endereço ao usuário autenticado
                address.save()
                context["form"] = form

    context["orders"] = [
        {
            "id": order.pk,
            "total": order.total,
            "data_pedido": order.data_pedido,
            "status": order.status,
        }
        for order in orders
    ]
    return render(request, "cupcakes/my-account.html", context=context)

def register_view(request):
    """
    Manipula o registro de novos usuários e faz login automaticamente após o registro.

    Esta view trata requisições POST para registrar um novo usuário com as informações 
    fornecidas (nome, sobrenome, nome de usuário, email, senha). Se o nome de usuário 
    já estiver em uso, uma mensagem de erro será exibida. Caso contrário, o usuário 
    é criado, autenticado, e logado automaticamente. Uma mensagem de sucesso é exibida 
    e o usuário é redirecionado para a página inicial ou outra página designada.

    Parâmetros:
    request (HttpRequest): O objeto de requisição HTTP contendo os dados do usuário
                           (nome, sobrenome, nome de usuário, email, senha, e 
                           a opção de inscrição).

    Retorna:
    HttpResponse: Renderiza a página de registro caso o método seja GET ou POST com erro.
                  Caso o registro seja bem-sucedido, redireciona o usuário para 
                  a página inicial com uma mensagem de sucesso.

    Comportamento:
    - Se o método for POST, os dados do formulário são processados:
        - O nome de usuário é verificado para garantir que não está em uso.
        - Se disponível, o usuário é criado, salvo e autenticado.
        - O usuário é logado automaticamente e redirecionado com uma mensagem de sucesso.
    - Se o método for GET, a página de registro é exibida.

    Observações:
    - O campo "subscribe" é opcional e verifica se o usuário optou por se inscrever em algo 
      (por exemplo, uma newsletter), mas não é utilizado diretamente nesta função.
    - As mensagens de erro ou sucesso são exibidas ao usuário através do sistema 
      de mensagens do Django.

    Exceções:
    - Não há tratamento específico para exceções, então erros como falha no banco de dados 
      ou problemas de autenticação podem resultar em erros não capturados.
    """

    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        subscribe = request.POST.get("subscribe", False)

        # Verifica se o username já existe
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
        else:
            # Cria o novo usuário
            user = User.objects.create_user(
                username=username, password=password, email=email
            )
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # Autentica e faz login do usuário automaticamente após o registro
            login(request, user)

            # Exibe uma mensagem de sucesso e redireciona para a página inicial ou outra página
            messages.success(request, "Registration successful.")
            return redirect("home-page")

    return render(request, "cupcakes/register.html")

def login_view(request):
    """
    Manipula o login de usuários no sistema.

    Esta view trata requisições GET e POST para realizar o login de usuários. 
    Se o usuário já estiver autenticado, ele é redirecionado para a URL especificada 
    no parâmetro 'next' ou, se não especificado, para a página principal ("/"). 
    Se o usuário não estiver autenticado, o formulário de login é exibido e processado 
    quando enviado. Se as credenciais de login forem válidas, o usuário é autenticado 
    e redirecionado para a URL indicada no parâmetro 'next'. Caso contrário, uma mensagem 
    de erro é exibida.

    Parâmetros:
    request (HttpRequest): O objeto de requisição HTTP contendo dados de login 
                           (nome de usuário e senha) no caso de uma requisição POST 
                           ou a URL de redirecionamento no caso de uma requisição GET.

    Retorna:
    HttpResponse: Se o método for GET ou a autenticação falhar, a página de login 
                  é renderizada. Se o login for bem-sucedido, o usuário é redirecionado 
                  para a URL especificada ou para a página principal ("/").

    Comportamento:
    - Se o método for GET:
        - Se o usuário já estiver autenticado, ele é redirecionado para a página indicada
          no parâmetro 'next' (ou a página principal).
        - Caso contrário, a página de login é exibida.
    - Se o método for POST:
        - O nome de usuário e a senha são capturados e o Django tenta autenticar o usuário.
        - Se as credenciais forem válidas, o login é realizado e o usuário é redirecionado
          para a URL especificada em 'next' (ou a página principal).
        - Se as credenciais forem inválidas, uma mensagem de erro é exibida na página.

    Observações:
    - O parâmetro 'next' é utilizado para redirecionar o usuário para a página que ele 
      tentou acessar antes de ser redirecionado para o login.
    - As mensagens de erro são exibidas ao usuário através do sistema de mensagens do Django.
    """

    # Captura o valor do parâmetro 'next'
    next_url = request.GET.get("next", "/")
    if request.user.is_authenticated:
        return redirect(next_url)

    if request.method == "POST":
        next_url = request.GET.get("next", "/")
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redireciona para a página principal após o login
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "cupcakes/login.html")

@login_required
def logout_view(request):
    """
    Realiza o logout do usuário autenticado e redireciona para a página inicial.

    Esta view trata a requisição de logout do usuário atual. Ao ser chamada, 
    o usuário é desautenticado da sessão ativa e redirecionado para a página inicial.

    Parâmetros:
    request (HttpRequest): O objeto de requisição HTTP que contém as informações 
                           da sessão do usuário que será desconectado.

    Retorna:
    HttpResponse: Redireciona o usuário para a página inicial (home-page) após 
                  o logout ser realizado com sucesso.

    Comportamento:
    - A função `logout()` do Django é chamada para desautenticar o usuário.
    - Após o logout, o usuário é redirecionado para a página inicial.
    
    Observações:
    - Não há verificação de autenticação prévia, a função tentará deslogar o usuário 
      independentemente de seu estado atual (logado ou não).
    """

    logout(request)
    return redirect("home-page")

