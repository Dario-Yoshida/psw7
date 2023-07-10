from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Conta, Categoria
from django.contrib import messages
from django.contrib.messages import constants
from .utils import calcula_total, calcula_equilibrio_financeiro
from datetime import datetime
from extrato.models import Valores

# Create your views here.
def home(request):
    valores = Valores.objects.filter(data__month=datetime.now().month)
    entrada = valores.filter(tipo='E')
    saida = valores.filter(tipo='S')
    
    total_entrada = calcula_total(entrada, 'valor')
    total_saida = calcula_total(saida, 'valor')
    saldo_mes = total_entrada - total_saida
    contas = Conta.objects.all()
    total_conta = calcula_total(contas, 'valor')

    vencidas = request.session.get('vencidas')
    proximas = request.session.get('proximas')

    percentual_gastos_essenciais, percentual_gastos_nao_essenciais = calcula_equilibrio_financeiro()
    
    return render(request, 'home.html', {'proximas':proximas, 'vencidas':vencidas, 'saldo_mes':saldo_mes, 'percentual_gastos_essenciais':int(percentual_gastos_essenciais), 'percentual_gastos_nao_essenciais':int(percentual_gastos_nao_essenciais), 'total_entrada':total_entrada, 'total_saida':total_saida, 'contas':contas, 'total_conta':total_conta})

def gerenciar(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    total_conta = calcula_total(contas, 'valor')
    
    return render(request, "gerenciar.html", {'contas':contas, 'total_conta':total_conta, 'categorias':categorias})

def cadastrar_banco(request):
    apelido = request.POST.get('apelido')
    banco = request.POST.get('banco')
    tipo = request.POST.get('tipo')
    valor = request.POST.get('valor')
    icone = request.FILES.get('icone')

    if len(apelido.strip()) == 0 or len(valor.strip()) == 0 or len(banco.strip()) == 0 or len(tipo.strip()) == 0:
        # mensagem erro
        messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
        return redirect('/perfil/gerenciar/')
    #aumentar validações

    conta = Conta(
        apelido=apelido,
        banco=banco,
        tipo=tipo,
        valor=valor,
        icone=icone
    )

    conta.save()
    messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com Sucesso!')
    return redirect('/perfil/gerenciar/')

def deletar_banco(request, id):
    conta = Conta.objects.get(id=id)
    conta.delete()

    messages.add_message(request, constants.SUCCESS, 'Banco deletado com sucesso!')
    return redirect('/perfil/gerenciar/')

def cadastrar_categoria(request):
    nome = request.POST.get('categoria')
    essencial = bool(request.POST.get('essencial'))
    print(essencial)
    #validar nome e essencial
    if len(nome.strip()) == 0 or not isinstance(essencial, bool):
        # mensagem erro
        messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
        return redirect('/perfil/gerenciar/')

    categoria = Categoria(
        categoria=nome,
        essencial=essencial
    )

    categoria.save()

    messages.add_message(request, constants.SUCCESS, 'Categoria cadastrada com sucesso')
    return redirect('/perfil/gerenciar/')


def update_categoria(request, id):
    categoria = Categoria.objects.get(id=id)
    categoria.essencial = not categoria.essencial
    categoria.save()

    return redirect('/perfil/gerenciar/')


def dashboard(request):
    dados = {}

    categorias = Categoria.objects.all()

    for categoria in categorias:
        total = 0
        valores = Valores.objects.filter(categoria=categoria)
        for v in valores:
            total += v.valor
        dados[categoria.categoria] = total

    return render(request, 'dashboard.html', {'labels': list(dados.keys()), 'values': list(dados.values())})