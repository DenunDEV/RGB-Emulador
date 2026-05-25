
# main.py - Ponto de Entrada para o RGB Dynamic Analyzer Emulator
# 1. Detectar e validar a imagem de entrada (via argumento ou pasta input/)
# 2. Configurar o ambiente de saída (pasta output/)
# 3. Invocar o ChromaticAnalyzer para processar a imagem e gerar os resultados

import sys
from pathlib import Path
from chromatic_analyzer import ChromaticAnalyzer

def main():
    print("=" * 50)
    print("RGB DYNAMIC ANALYZER - PROJETO INDEPENDENTE")
    print("=" * 50)

    # 1. Resolve o diretório ABSOLUTO do script (evita erros de CWD) e define pastas de input/output
    SCRIPT_DIR = Path(__file__).parent.resolve()
    INPUT_DIR = SCRIPT_DIR / "input"
    OUTPUT_DIR = SCRIPT_DIR / "output"

    # Estrutura de pastas
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Lógica de seleção de imagem
    if len(sys.argv) > 1:
        # Usuário passou caminho via terminal
        image_path = Path(sys.argv[1])
        if not image_path.is_absolute():
            image_path = Path.cwd() / image_path
    else:
        # Detecção automática na pasta input/
        valid_ext = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}
        found_files = [
            f for f in INPUT_DIR.iterdir() 
            if f.is_file() and f.suffix.lower() in valid_ext
        ]
        
        if not found_files:
            print("️ Nenhuma imagem válida encontrada em 'input/'.")
            print("📁 Formatos aceitos: PNG, JPG, JPEG, WEBP, BMP")
            print("💡 Verifique se a extensão não está duplicada (ex: 'logo.png.jpg')")
            print("   Ou rode: python main.py input/nome_da_sua_imagem.png")
            return
            
        # Ordena alfabeticamente para consistência
        image_path = sorted(found_files)[0]
        print(f"📷 Imagem detectada automaticamente: {image_path.name}")

    # 3. Validação final
    if not image_path.exists():
        print(f"❌ Arquivo não encontrado: {image_path}")
        return

    print(f"🔍 Processando: {image_path}")
    analyzer = ChromaticAnalyzer(tolerance=30.0, max_colors=15)

    try:
        # Passa caminhos absolutos para o analyzer
        analyzer.analyze(str(image_path), output_folder=str(OUTPUT_DIR))
        print("\n Análise concluída com sucesso!")
        print(f"📂 Resultados salvos em: {OUTPUT_DIR}")
    except Exception as e:
        print(f"\n❌ Erro durante a análise: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()