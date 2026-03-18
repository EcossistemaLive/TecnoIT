import re

def normalize_phone(raw: str) -> list[str]:
    """
    Normaliza números de WhatsApp brasileiros.
    Retorna as variantes possíveis (com e sem o 9º dígito) para busca no DB.
    """
    digits = re.sub(r'\D', '', str(raw))
    
    digits = digits.replace('s.whatsapp.net', '')

    if not digits.startswith('55') and len(digits) >= 10:
        digits = '55' + digits
        
    if len(digits) < 12: # Incompleto
        return [digits]
        
    ddd = digits[2:4]
    number = digits[4:]
    
    candidates = []
    
    if len(number) == 9:
        candidates.append('55' + ddd + number)          # com 9
        candidates.append('55' + ddd + number[1:])      # sem 9
    elif len(number) == 8:
        candidates.append('55' + ddd + number)          # sem 9
        candidates.append('55' + ddd + '9' + number)    # com 9
    else:
        candidates.append(digits)
        
    return list(set(candidates))
