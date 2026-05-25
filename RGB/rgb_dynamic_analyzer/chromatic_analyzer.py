# Chromatic_analyzer.py - Motor de Análise Cromática Dinâmica para Imagens RGB

import cv2
import numpy as np
import json
import os
from typing import List, Dict, Tuple
from datetime import datetime

class ChromaticAnalyzer:
    """
    Motor de Emulador e Análise Cromática Dinâmica para Imagens RGB.
    
    Responsável único por:
    1. Ler imagems RGB e processar seus pixels
    2. Extrair cores dominantes baseadas em tolerância RGB 
    3. Gerar JSON de dados cromáticos (RGB, HEX, % de presença)
    4. Gerar PNG de paleta visual com as cores detectadas

    """

    def __init__(self, tolerance: float = 30.0, max_colors: int = 20):
        """
        :param tolerance: Distância RGB máxima para considerar duas cores como "iguais".
        :param max_colors: Limite máximo de cores para extrair (evita poluição visual).
        """
        self.tolerance = tolerance
        self.max_colors = max_colors

    def _calculate_distance(self, c1: np.ndarray, c2: np.ndarray) -> float:
        """Distância Euclidiana simples no espaço RGB"""
        return float(np.linalg.norm(c1 - c2))

    def analyze(self, image_path: str, output_folder: str = "output"):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Imagem não encontrada em: {image_path}")

        print(f" Iniciando análise em: {image_path}")

        # 1. Carregar Imagem
        img = cv2.imread(image_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        height, width, _ = img_rgb.shape
        total_pixels = height * width

        # 2. Pré-processamento (Resize para agilizar e suavizar ruído)
        # Reduzimos a imagem para um tamanho manejável para extrair a "essência" das cores
        # Reduzindo para 150x150, o que dá 22.500 pixels, um número razoável para análise sem perder a diversidade de cores.
        sample_size = (150, 150) 
        img_small = cv2.resize(img_rgb, sample_size, interpolation=cv2.INTER_AREA)
        pixels = img_small.reshape(-1, 3) # Transforma em lista de pixels [R, G, B]

        # 3. Extração e Agrupamento de Cores
        print("🎨 Processando agrupamento de cores...")
        unique_colors = self._cluster_colors(pixels)

        # 4. Preparar Dados para JSON
        colors_data = []
        for idx, color_info in enumerate(unique_colors):
            rgb = color_info['color'].astype(int)
            hex_code = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
            percentage = (color_info['count'] / len(pixels)) * 100

            colors_data.append({
                "id": f"COLOR_{idx:02d}",
                "rgb": rgb.tolist(),
                "hex": hex_code,
                "percentage": round(percentage, 2),
                "approx_pixels_original": int((percentage / 100) * total_pixels)
            })

        # 5. Gerar JSON
        report = {
            "project": "RGB Dynamic Analyzer",
            "source_image": os.path.basename(image_path),
            "timestamp": datetime.now().isoformat(),
            "config": {
                "tolerance": self.tolerance,
                "max_colors": self.max_colors
            },
            "detected_colors": colors_data,
            "total_detected": len(colors_data)
        }

        os.makedirs(output_folder, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        json_path = os.path.join(output_folder, f"{base_name}_analysis.json")
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        print(f"✅ JSON salvo em: {json_path}")

        # 6. Gerar Imagem da Paleta
        png_path = os.path.join(output_folder, f"{base_name}_palette.png")
        self._generate_palette_image(colors_data, png_path)
        print(f"✅ Paleta visual salva em: {png_path}")

        return report

    def _cluster_colors(self, pixels: np.ndarray) -> List[Dict]:
        """
        Algoritmo de clusterização simples baseado em tolerância.
        Se um pixel está perto de uma cor existente, incrementa essa cor.
        Se não, cria uma nova cor.
        """
        clusters = [] # Lista de dicionários: {'color': [R,G,B], 'count': int}

        for pixel in pixels:
            pixel = pixel.astype(float)
            found_cluster = False

            for cluster in clusters:
                if self._calculate_distance(pixel, cluster['color']) < self.tolerance:
                    # Atualiza a média da cor para refinar a precisão
                    old_count = cluster['count']
                    new_count = old_count + 1
                    
                    # Fórmula de média móvel para evitar guardar todos os pixels
                    cluster['color'] = ((cluster['color'] * old_count) + pixel) / new_count
                    cluster['count'] = new_count
                    found_cluster = True
                    break
            
            if not found_cluster:
                clusters.append({'color': pixel.copy(), 'count': 1})
            
            # Limite de segurança para não travar o loop em imagens muito complexas
            if len(clusters) > self.max_colors * 2:
                # Se passou muito do limite, paramos de buscar novos e focamos nos existentes
                break

        # Ordenar por quantidade de pixels (do mais usado para o menos usado)
        clusters.sort(key=lambda x: x['count'], reverse=True)
        
        return clusters[:self.max_colors]

    def _generate_palette_image(self, colors_data: List[Dict], output_path: str):
        """Cria uma imagem horizontal mostrando as cores detectadas."""
        if not colors_data:
            return

        swatch_width = 100
        swatch_height = 100
        gap = 10
        text_height = 40
        
        total_width = (len(colors_data) * (swatch_width + gap)) - gap
        total_height = swatch_height + text_height

        # Fundo branco
        canvas = np.ones((total_height, total_width, 3), dtype=np.uint8) * 255

        for i, color_info in enumerate(colors_data):
            rgb = color_info['rgb']
            x_start = i * (swatch_width + gap)
            
            # Desenhar o retângulo da cor
            # OpenCV usa BGR, então invertemos RGB -> BGR
            cv2.rectangle(canvas, 
                          (x_start, 0), 
                          (x_start + swatch_width, swatch_height), 
                          (rgb[2], rgb[1], rgb[0]), 
                          -1)
            
            # Borda fina preta
            cv2.rectangle(canvas, 
                          (x_start, 0), 
                          (x_start + swatch_width, swatch_height), 
                          (0, 0, 0), 
                          1)
            
            # Texto com o código HEX
            cv2.putText(canvas, 
                        color_info['hex'].upper(), 
                        (x_start + 10, swatch_height + 25), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.5, 
                        (0, 0, 0), 
                        1)

        cv2.imwrite(output_path, canvas)