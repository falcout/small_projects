def main():
    if to_fill(*get_input()):
        print("\nDeclarar IRPF")
    else:
        print("\nNao precisa declarar IRPF")


def get_input():
    while True:
        try:
            cat1 = float(input("-----------------------\nDetalhe seu faturamento\n-----------------------\n\nComercio, Industria e Transporte de Carga: "))
            cat2 = float(input("Transporte de Passageiro: "))
            cat3 = float(input("Servicos em geral: "))
            expenses = float(input("Despesas: "))
        except ValueError:
            print("Apenas numeros sao permitidos")
        else:
            break

    return cat1, cat2, cat3, expenses
    

def to_fill(market, transport, services, discount):
    revenue = market + transport + services
    exempt = market * 0.08 + transport * 0.16 + services * 0.32

    if revenue > 81_000:
        print("\nCUIDADO! Faturamento acima do limite MEI", end='')
        return True
    elif revenue - discount - exempt > 35_584:
        return True
    
    return False



if __name__ == "__main__":
    main()