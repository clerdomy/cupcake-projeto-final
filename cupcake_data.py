from datetime import date
from core.models import Cupcake, Categoria
from django.contrib.auth.models import User

# Suponha que o usuário que está cadastrando seja o primeiro usuário na base de dados
usuario = User.objects.first()

# Suponha que você já tenha algumas categorias cadastradas
categoria1 = Categoria.objects.get_or_create(nome_categoria='Doces')[0]  
categoria2 = Categoria.objects.get_or_create(nome_categoria='Salgados')[0]

# Dados para o cadastro dos cupcakes
cupcakes_data = [
    {
        'titulo': 'Cupcake de Chocolate',
        'descricao': 'Delicioso cupcake de chocolate com cobertura de ganache e granulado.',
        'preco': 15.00,
        'sale': True,
        'preco_sale': 12.00,
        'quantidade_disponivel': 20,
        'sku': '784571',
        'data_lancamento': date(2024, 8, 10),
        'quem_cadastrou': usuario,
        'esta_em_destaque': True,
        'categoria': categoria1,
        'ingrediente': 'Açúcar, Farinha de Trigo, Cacau, Manteiga, Ovos',
        'etiqueta': 'Sem Glúten',
        'cobertura': 'Ganache de Chocolate'
    },
    {
        'titulo': 'Cupcake de Baunilha',
        'descricao': 'Cupcake de baunilha com cobertura de frutas vermelhas e granulado.',
        'preco': 14.00,
        'sale': True,
        'preco_sale': 2.00,
        'quantidade_disponivel': 15,
        'sku': 'VAAN7845',
        'data_lancamento': date(2024, 8, 11),
        'quem_cadastrou': usuario,
        'esta_em_destaque': True,
        'categoria': categoria2,
        'ingrediente': 'Açúcar, Farinha de Trigo, Baunilha, Manteiga, Ovos',
        'etiqueta': 'Vegano',
        'cobertura': 'Frutas Vermelhas'
    },
    {
        'titulo': 'Cupcake chocolate cara e caramelo',
        'descricao': 'Cupcake de chocolate com recheio de caramelo salgado.',
        'preco': 16.00,
        'sale': False,
        'preco_sale': None,
        'quantidade_disponivel': 10,
        'sku': 'CHOC7845',
        'data_lancamento': date(2024, 8, 12),
        'quem_cadastrou': usuario,
        'esta_em_destaque': False,
        'categoria': categoria1,
        'ingrediente': 'Açúcar, Farinha de Trigo, Cacau, Manteiga, Ovos, Caramelo',
        'etiqueta': 'Sem Lactose',
        'cobertura': 'Caramelo Salgado'
    },
    # Mais cupcakes adicionados aqui
    {
        'titulo': 'Cupcake de Chocolate Morango',
        'descricao': 'Delicioso cupcake de chocolate com cobertura de ganache e granulado.',
        'preco': 15.00,
        'sale': True,
        'preco_sale': 12.00,
        'quantidade_disponivel': 20,
        'sku': '784574',
        'data_lancamento': date(2024, 8, 10),
        'quem_cadastrou': usuario,
        'esta_em_destaque': True,
        'categoria': categoria1,
        'ingrediente': 'Açúcar, Farinha de Trigo, Cacau, Manteiga, Ovos',
        'etiqueta': 'Sem Glúten',
        'cobertura': 'Ganache de Chocolate'
    },
    {
        'titulo': 'Cupcake de Baunilha com granulado',
        'descricao': 'Cupcake de baunilha com cobertura de frutas vermelhas e granulado.',
        'preco': 14.00,
        'sale': True,
        'preco_sale': 2.00,
        'quantidade_disponivel': 15,
        'sku': 'VAAN7846',
        'data_lancamento': date(2024, 8, 11),
        'quem_cadastrou': usuario,
        'esta_em_destaque': True,
        'categoria': categoria2,
        'ingrediente': 'Açúcar, Farinha de Trigo, Baunilha, Manteiga, Ovos',
        'etiqueta': 'Vegano',
        'cobertura': 'Frutas Vermelhas'
    },
    {
        'titulo': 'Cupcake de Limão',
        'descricao': 'Cupcake de limão com cobertura de chantilly.',
        'preco': 13.00,
        'sale': True,
        'preco_sale': 10.00,
        'quantidade_disponivel': 18,
        'sku': 'LIMON784',
        'data_lancamento': date(2024, 8, 12),
        'quem_cadastrou': usuario,
        'esta_em_destaque': True,
        'categoria': categoria1,
        'ingrediente': 'Açúcar, Farinha de Trigo, Limão, Manteiga, Ovos',
        'etiqueta': 'Sem Lactose',
        'cobertura': 'Chantilly de Limão'
    },
    {
        'titulo': 'Cupcake de Morango',
        'descricao': 'Cupcake de morango com cobertura de merengue.',
        'preco': 17.00,
        'sale': False,
        'preco_sale': None,
        'quantidade_disponivel': 12,
        'sku': 'STRAW7845',
        'data_lancamento': date(2024, 8, 13),
        'quem_cadastrou': usuario,
        'esta_em_destaque': True,
        'categoria': categoria1,
        'ingrediente': 'Açúcar, Farinha de Trigo, Morango, Manteiga, Ovos',
        'etiqueta': 'Orgânico',
        'cobertura': 'Merengue de Morango'
    },
    {
        'titulo': 'Cupcake de Café',
        'descricao': 'Cupcake de café com cobertura de creme de mascarpone.',
        'preco': 18.00,
        'sale': True,
        'preco_sale': 15.00,
        'quantidade_disponivel': 10,
        'sku': 'COFF7845',
        'data_lancamento': date(2024, 8, 14),
        'quem_cadastrou': usuario,
        'esta_em_destaque': False,
        'categoria': categoria1,
        'ingrediente': 'Açúcar, Farinha de Trigo, Café, Manteiga, Ovos, Mascarpone',
        'etiqueta': 'Vegetariano',
        'cobertura': 'Creme de Mascarpone'
    },
    {
        'titulo': 'Cupcake de Cenoura',
        'descricao': 'Cupcake de cenoura com cobertura de chocolate.',
        'preco': 15.00,
        'sale': True,
        'preco_sale': 12.00,
        'quantidade_disponivel': 20,
        'sku': 'CAROT784',
        'data_lancamento': date(2024, 8, 15),
        'quem_cadastrou': usuario,
        'esta_em_destaque': True,
        'categoria': categoria1,
        'ingrediente': 'Açúcar, Farinha de Trigo, Cenoura, Manteiga, Ovos, Chocolate',
        'etiqueta': 'Sem Glúten',
        'cobertura': 'Chocolate'
    },
    {
        'titulo': 'Cupcake de Abóbora',
        'descricao': 'Cupcake de abóbora com cobertura de cream cheese.',
        'preco': 19.00,
        'sale': False,
        'preco_sale': None,
        'quantidade_disponivel': 14,
        'sku': 'PUMK7845',
        'data_lancamento': date(2024, 8, 16),
        'quem_cadastrou': usuario,
        'esta_em_destaque': False,
        'categoria': categoria2,
        'ingrediente': 'Açúcar, Farinha de Trigo, Abóbora, Manteiga, Ovos, Cream Cheese',
        'etiqueta': 'Vegetariano',
        'cobertura': 'Cream Cheese'
    },
    {
        'titulo': 'Cupcake de Coco',
        'descricao': 'Cupcake de coco com cobertura de marshmallow.',
        'preco': 16.00,
        'sale': True,
        'preco_sale': 14.00,
        'quantidade_disponivel': 17,
        'sku': 'COCO7845',
        'data_lancamento': date(2024, 8, 17),
        'quem_cadastrou': usuario,
        'esta_em_destaque': True,
        'categoria': categoria1,
        'ingrediente': 'Açúcar, Farinha de Trigo, Coco, Manteiga, Ovos, Marshmallow',
        'etiqueta': 'Sem Lactose',
        'cobertura': 'Marshmallow'
    },
    {
        'titulo': 'Cupcake de chantilly e raspas de limão.',
        'descricao': 'Cupcake de limão com cobertura de chantilly e raspas de limão.',
        'preco': 14.00,
        'sale': True,
        'preco_sale': 11.00,
        'quantidade_disponivel': 18,
        'sku': 'LIMON7846',
        'data_lancamento': date(2024, 8, 18),
        'quem_cadastrou': usuario,
        'esta_em_destaque': False,
        'categoria': categoria1,
        'ingrediente': 'Açúcar, Farinha de Trigo, Limão, Manteiga, Ovos',
        'etiqueta': 'Orgânico',
        'cobertura': 'Chantilly e Raspas de Limão'
    }
]

# Cadastro dos cupcakes no banco de dados
for cupcake_data in cupcakes_data:
    cupcake = Cupcake(**cupcake_data)
    cupcake.save()
