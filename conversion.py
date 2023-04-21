import segmentador
import os
import time

def segmentadorDir (dir_pdf, dir_json):

    if not os.path.exists(dir_pdf):
        print(f"Caminho não existe: '{dir_pdf}'.")
        print(f"Por favor, informar o caminho completo com a entrada dos dados: {sys.argv[0]} --dir <caminho>")
        exit(2)

    arquivos = os.listdir(dir_pdf)
    for arquivo in arquivos:
        if arquivo.endswith('.pdf'):
            chama_segmentador(dir_pdf + arquivo, dir_json)

def chama_segmentador(arquivo_pdf, dir_json):
    file_name = arquivo_pdf.split('/')[-1][:-4]
    dir_html = f'./data/HTML_files/{file_name}.html'

    start_time = time.time()
    print("Convertendo arquivo '" + arquivo_pdf + "' para html")
    os.system(f'pdf2htmlEX {arquivo_pdf} {dir_html}')
    print("Covertido - %.2f segundos" % (time.time() - start_time))

    start_time = time.time()
    print("Processando '" + dir_html + "'")
    os.system(f'node ./Javascript/index.js {dir_html}')
    print("Processado - %.2f segundos" % (time.time() - start_time))
    
    arquivo_json = f'./data/json_files/{file_name}.json'

    seg = segmentador.Segmentador(arquivo_pdf, arquivo_json, dir_json)
    seg.segmentar()

    # os.remove(dir_html)