import codecs
import pdfplumber
import re
import json
import os
import time
import sys

# def segmentadorDir (dir_pdf, dir_json):

#     if not os.path.exists(dir_pdf):
#         print(f"Caminho não existe: '{dir_pdf}'.")
#         print(f"Por favor, informar o caminho completo com a entrada dos dados: {sys.argv[0]} --dir <caminho>")
#         exit(2)

#     arquivos = os.listdir(dir_pdf)
#     for arquivo in arquivos:
#         if arquivo.endswith('.pdf'):
#             segmentador(dir_pdf + arquivo, dir_json)

class Segmento:
    def __init__(self, titulo, conteudo, numero_da_pagina = "", publicador = ""):
        self.titulo = titulo
        self.conteudo = conteudo
        self.numero_da_pagina = numero_da_pagina
        self.publicador = publicador

class Segmentador:
    def __init__(self, arquivo_pdf, arquivo_json, dir_json):
        self.arquivo_pdf = arquivo_pdf
        self.arquivo_json = arquivo_json
        self.dir_json = dir_json

        if not os.path.exists(dir_json):
            os.makedirs(dir_json)

        start_time = time.time()
        print("Pré-processando arquivo '" + self.arquivo_json + "'")
        try:
            self.sections = json.load(open(arquivo_json))
        except:
            self.sections = []
        self.sections_dict = {}
        self.pdf = pdfplumber.open(arquivo_pdf)
        linhas_em_negrito = dict()
        lista_linhas_em_negrito = json.load(open('lista_linhas_em_negrito.json'))

        for page in self.pdf.pages:
            clean_text = page.filter(lambda obj: obj['object_type'] == 'char' and 'Bold' in obj['fontname'])
            lista_linhas_em_negrito += clean_text.extract_text().split('\n')

        caixa_alta = set()
        caixa_baixa = set()

        for linha in lista_linhas_em_negrito:
            if ''.join(linha.split('º')).isupper():
                caixa_alta.add(linha)
            else:
                caixa_baixa.add(linha)

        caixa_alta.add('これはファイルの終わりです')

        self.caixa_alta = caixa_alta
        self.caixa_baixa = caixa_baixa

        self.document_dict = {
            "origem" : self.arquivo_pdf,
            "diario": "Diário Oficial de Belo Horizonte",
            "numero" : "",
            "data" : "",
            "segmentos" : ""
        }

        print("Pré-processado - %.2f segundos" % (time.time() - start_time))

    def segmentar_secao(self, secao):
        linhas = secao['text']
        linhas.append('これはファイルの終わりです')

        caixa_alta = self.caixa_alta
        caixa_baixa = self.caixa_baixa

        segmentos = []

        regex_formula = re.compile(r'.*Diário Oficial do Município[\s]?[\d]+[Poder Executivo]{0,15}')

        PDF_number_formula = re.compile(r'.*N. [\d]\.[\d]{3}.*')

        page_number_formula = re.compile(r'Page number: [\d]*')
        
        date_formula = re.compile(r'.*\d{1,2}\/\d{1,2}\/\d{4}.*')

        primeira_linha, segunda_linha = linhas[:2]
        linhas = linhas[2:]

        numeros = re.findall(r'[0-9]+', segunda_linha)

        meses = {
            '1' : 'Janeiro',
            '2' : 'Fevereiro',
            '3' : 'Março',
            '4' : 'Abril',
            '5' : 'Maio',
            '6' : 'Junho',
            '7' : 'Julho',
            '8' : 'Agosto',
            '9' : 'Setembro',
            '10' : 'Outubro',
            '11' : 'Novembro',
            '12' : 'Dezembro'
        }

        try:
            numero_lista = numeros[:-3]
            dia, mes, ano = numeros[-3:]
            data_string = f'{dia} de {meses[mes]} de {ano}'
            numero = ''.join(numero_lista)
        except:
            numero = 'ERROR'
            data_string = 'ERROR'

        data_flag = False
        number_flag = False
        titulo = ''
        conteudo = ''
        page_number = '1'
        publicador = ''
        linha_anterior = ''

        if data_flag == False:
            for linha in linhas:

                if date_formula.match(linha) != None:
                    #print("Linha da data: " + linha)
                    data = linha.split('/')
                    dia = data[0]
                    mes = data[1]
                    ano = data[2]
                    dia = dia.strip()
                    data_flag = True
                    try:
                        data_string = f'{dia} de {meses[mes]} de {ano}'
                    except:
                        data_string = "ERROR"
                    break

        for linha in linhas:

            if page_number_formula.match(linha) != None:
                print("Linha do número: " + linha)
                page_number = linha[len(linha) - 2 :]
                if int(page_number) < 10:
                    page_number = page_number[1]

            if linha in caixa_alta:

                if titulo and conteudo:
                    segmentos.append(Segmento(titulo, conteudo, page_number, publicador))
                    titulo = ''
                    conteudo = ''
                    publicador = ''

                titulo += linha + '\n'
            
            elif linha in caixa_baixa:

                publicador += linha_anterior + '\n'

            else:
                if number_flag == False:
                    if PDF_number_formula.match(linha) != None:
                        #print("Linha do numero do arquivo: " + linha)
                        #PDF_number_extractor = linha.split()
                        try:
                            index = linha.index("N.")
                            numero = linha[index + 3: index + 8]
                        except:
                            numero = linha
                        #numero = PDF_number_extractor[PDF_number_extractor.index("N.") + 1].translate(str.maketrans('', '','.'))
                        number_flag = True
                        break
                if linha[:55] == "Documento assinado digitalmente em consonância com a MP" or linha[:18] == "Poder Executivo" or regex_formula.match(linha) != None or page_number_formula.match(linha) != None:
                    if regex_formula.match(linha) != None and data_flag == False:
                        date = linha.split()
                        data_string = ""
                        date[3] = date[3].title()
                        for i in range (1, 6):
                            data_string += date[i]
                            if i < 5:
                                data_string += " "
                        data_flag = True
                    if not conteudo:    
                        ultimo_segmento = segmentos.pop()
                        titulo, conteudo, page_number, publicador = ultimo_segmento.titulo, ultimo_segmento.conteudo, ultimo_segmento.numero_da_pagina, ultimo_segmento.publicador
                else:
                    if linha[:19] == "Hash da assinatura:":
                        continue
                    else:
                        conteudo += linha + '\n'

            linha_anterior = linha

        if not self.document_dict["numero"] or self.document_dict["numero"] == "ERROR":
            self.document_dict["numero"] = numero

        if not self.document_dict["data"] or self.document_dict["data"] == "ERROR":
            self.document_dict["data"] = data_string


        segmentos_dicts = []
    
        for segmento in segmentos:
            seg_dict = {
                "materia" : segmento.titulo + segmento.conteudo,
                "page" : segmento.numero_da_pagina,
                "publicador" : segmento.publicador,
                "id" : "" 
            }
            segmentos_dicts.append(seg_dict)
        
        return(segmentos_dicts)

    def segmentar(self):
        start_time = time.time()
        print("Processando arquivo '" + self.arquivo_json + "'")

        for section in self.sections:
            self.sections_dict[section["title"]] = self.segmentar_secao(section)

        self.document_dict["segmentos"] = self.sections_dict
        try:
            os.remove(self.arquivo_json)
        except:
            no_file = True    
        json_file_name = self.dir_json + self.arquivo_pdf.split('/')[-1][:-4] + '.json'
        with codecs.open(json_file_name, "w", "utf-8") as outfile: 
            json.dump(self.document_dict, outfile, indent = 4, ensure_ascii=False)
        print("Processado - %.2f segundos" % (time.time() - start_time))