import re

def is_valid_cpf(cpf: str) -> bool:
    """Valida um CPF verificando os dígitos e formato."""
    cpf = re.sub(r'\D', '', str(cpf))
    
    if len(cpf) != 11:
        return False
        
    if cpf == cpf[0] * 11:
        return False

    # Primeiro dígito
    sum_val = sum(int(cpf[i]) * (10 - i) for i in range(9))
    rem = sum_val % 11
    digit1 = 0 if rem < 2 else 11 - rem
    
    if digit1 != int(cpf[9]):
        return False

    # Segundo dígito
    sum_val = sum(int(cpf[i]) * (11 - i) for i in range(10))
    rem = sum_val % 11
    digit2 = 0 if rem < 2 else 11 - rem
    
    if digit2 != int(cpf[10]):
        return False

    return True

def format_cpf(cpf: str) -> str:
    """Retorna CPF pontuado."""
    cpf = re.sub(r'\D', '', str(cpf))
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf
