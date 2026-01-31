import utils_render
import config
import os
import shutil

def main():
    print("🚀 Iniciando construção do site para GitHub Pages...")
    
    output_dir = "docs"
    
    # Limpa diretório anterior
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📂 Diretório de saída: {output_dir}")
    
    # Gera o HTML usando as configuarações padrões
    try:
        _, _, debug = utils_render.render_quarto(
            titulo=config.TITULO_PADRAO,
            subtitulo=config.SUBTITULO_PADRAO,
            instituto=config.INSTITUTO_PADRAO,
            conteudo=config.CONTEUDO_PADRAO,
            uploaded_files=None, # Para o build automático, assumimos sem upload dinâmico por enquanto
            output_dir=output_dir
        )
        
        # Verifica se deu erro
        if debug.get('exit_code') != 0:
            print("❌ Erro ao renderizar:")
            print(debug.get('stderr'))
            return

        # Quarto gera 'apresentacao.html' ou 'index.html' dependendo da config.
        # O script utils_render copia como index.html para output_dir.
        
        # Precisamos garantir que arquivos estáticos também vão
        # O Quarto com --embed-resources coloca tudo num arquivo só, o que é ótimo para Pages simples.
        
        print("✅ Site gerado com sucesso!")
        print(f"👉 Abra {output_dir}/index.html para testar.")
        print("🔧 Para publicar: git push e ative o GitHub Pages na pasta /docs")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
