#!/usr/bin/env python3
"""
📄 Gerador Automático de subjects.json + Renomeador de PDFs
Coloque este script DENTRO da pasta 'pdf/' e execute:
    python gerar_subjects.py
"""

import os
import re
import json
import unicodedata
from pathlib import Path

def normalize_pdf_name(filename: str) -> str | None:
    """
    Padroniza o nome do arquivo:
    - Minúsculas
    - Remove acentos
    - Substitui espaços/caracteres especiais por '_'
    - Remove underscores duplicados e do início/fim
    """
    name, ext = os.path.splitext(filename)
    if ext.lower() != '.pdf':
        return None  # Ignora arquivos que não são PDF

    # 1. Minúsculas
    name = name.lower()
    # 2. Remove acentos (ex: á -> a, ç -> c)
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    # 3. Substitui tudo que não é letra/número por '_'
    name = re.sub(r'[^a-z0-9]', '_', name)
    # 4. Limpa underscores repetidos e das bordas
    name = re.sub(r'_+', '_', name).strip('_')
    
    return f"{name}.pdf"


def main():
    pdf_dir = Path(__file__).parent.resolve()
    print(f"🔍 Escaneando pasta: {pdf_dir}\n")

    subjects = {}
    total_pdfs = 0
    total_renamed = 0
    subjects_found = 0

    # Percorre apenas subpastas
    for item in sorted(pdf_dir.iterdir()):
        if not item.is_dir():
            continue

        subject_name = item.name
        pdf_list = []
        used_names = set()  # Evita colisões ao renomear

        for file_path in sorted(item.iterdir()):
            if not file_path.is_file() or file_path.suffix.lower() != '.pdf':
                continue

            total_pdfs += 1
            original_name = file_path.name
            new_name = normalize_pdf_name(original_name)

            if new_name is None:
                continue

            # 🔁 Lógica anti-colisão
            if new_name in used_names:
                base = os.path.splitext(new_name)[0]
                counter = 1
                while f"{base}_{counter}.pdf" in used_names:
                    counter += 1
                new_name = f"{base}_{counter}.pdf"

            used_names.add(new_name)

            # 📝 Renomeia fisicamente se necessário
            if original_name != new_name:
                new_path = item / new_name
                try:
                    file_path.rename(new_path)
                    print(f"  🔄 {original_name:40} → {new_name}")
                    total_renamed += 1
                except Exception as e:
                    print(f"  ❌ Falha ao renomear {original_name}: {e}")
                    continue
            else:
                print(f"  ✅ {original_name}")

            pdf_list.append(new_name)

        if pdf_list:
            subjects[subject_name] = pdf_list
            subjects_found += 1
            print()  # Espaço visual entre assuntos
        else:
            print(f"  ⚠️  Pasta '{subject_name}' vazia ou sem PDFs. Ignorada.\n")

    # 💾 Gera o subjects.json
    json_path = pdf_dir / 'subjects.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(subjects, f, indent=2, ensure_ascii=False)

    print("━" * 50)
    print(f"✅ Processo concluído!")
    print(f"📊 Total de PDFs processados: {total_pdfs}")
    print(f"🔄 Arquivos renomeados:      {total_renamed}")
    print(f"📚 Assuntos mapeados:        {subjects_found}")
    print(f"💾 JSON salvo em:            {json_path}")
    print("━" * 50)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Operação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")