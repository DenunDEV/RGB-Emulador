RGB DYNAMIC ANALYZER (Emulador RGB) 

- Contexto & Arquitetura
  
Objetivo do Módulo 

  O dinamismo desse emulador é essencial, assim deixando mais amplo e vasto a quantidade de opções e trabalhos que darão para calibragem e projeto relacionados a RGB. Podendo extrair dinamicamente a paleta cromática real de qualquer imagem raster (PNG, JPG, WEBP, etc.), agrupando variações de cor por tolerância matemática, calculando proporções de presença e exportando:

- JSON estruturado com dados RGB/HEX, IDs e porcentagens.
- PNG visual com swatches e rótulos para validação humana.

Este módulo é agnóstico e independente. Não assume paletas fixas, não depende de UI e não está acoplado a lógica de QR/Logo. Serve como camada pura de extração cromática.
️ Arquitetura & Responsabilidades

- main.py
  Orquestrador de Entrada/Saída
Resolve caminhos absolutos, detecta imagem em /input, valida extensões, instancia o analyzer e trata exceções.

 - chromatic_analyzer.py
   Motor de Processamento
Classe ChromaticAnalyzer: Carrega imagem → Reduz ruído → Agrupa por tolerância → Estrutura dados → Gera JSON + PNG.

Lógica Central & Decisões Técnicas

   Clusterização por Tolerância (Não K-Means) 
Usa distância euclidiana no espaço RGB: √((R1-R2)² + (G1-G2)² + (B1-B2)²)Por quê? K-Means exige número fixo de clusters e distorce cores dominantes.

  A tolerância adaptativa preserva a intenção visual do designer.Refinamento: Média móvel ponderada atualiza a cor do cluster a cada novo pixel, evitando viés do "primeiro pixel encontrado".
 Amostragem Inteligente
 Redimensiona para 150x150 com INTER_AREA antes da análise.

  Benefícios:
- Reduz carga computacional em ~95% para imagens 4K.
- Suaviza artefatos de compressão JPEG e anti-aliasing.
- Mantém a proporção cromática original da imagem.
