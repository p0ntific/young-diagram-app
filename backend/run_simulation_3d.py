#!/usr/bin/env python3
"""
Скрипт для запуска 3D симуляций диаграмм Юнга.
"""
import os
import argparse
from diagrams3d import DiagramSimulator3D


def main():
    """
    Основная функция для запуска 3D симуляций диаграмм Юнга.
    """
    parser = argparse.ArgumentParser(description='Запуск 3D симуляций диаграмм Юнга')
    parser.add_argument('--alpha', type=float, default=1.0,
                      help='Степенной параметр для управления поведением роста (по умолчанию: 1.0)')
    parser.add_argument('--steps', type=int, default=1000,
                      help='Количество шагов для каждой симуляции (по умолчанию: 1000)')
    parser.add_argument('--runs', type=int, default=10,
                      help='Количество запусков симуляции (по умолчанию: 10)')
    parser.add_argument('--output-dir', type=str, default='results_3d',
                      help='Директория для сохранения выходных файлов (по умолчанию: results_3d)')
    parser.add_argument('--visualization', type=str, choices=['voxel', 'point', 'slice', 'all'], 
                      default='all', help='Тип визуализации для генерации (по умолчанию: all)')
    
    args = parser.parse_args()
    
    # Создаем выходную директорию, если она не существует
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Запуск 3D симуляций диаграмм Юнга с alpha={args.alpha}")
    print(f"Шагов на симуляцию: {args.steps}")
    print(f"Количество запусков: {args.runs}")
    
    # Создаем и запускаем симулятор
    simulator = DiagramSimulator3D()
    simulator.simulate(n_steps=args.steps, alpha=args.alpha, runs=args.runs)
    
    # Базовое имя файла для выходных данных
    base_filename = f"{args.output_dir}/young_diagram_3d_alpha_{args.alpha}"
    
    # Сохраняем результаты
    print(f"Сохранение результатов в {args.output_dir}/...")
    
    # Сохраняем количество ячеек в файл
    simulator.save_cells(f"{base_filename}_cells.txt")
    
    # Генерируем визуализации
    print("Генерация визуализаций...")
    
    # Определяем, какие визуализации генерировать
    visualizations = []
    if args.visualization == 'all':
        visualizations = ['voxel', 'point', 'slice']
    else:
        visualizations = [args.visualization]
    
    # Генерируем выбранные визуализации
    for viz_type in visualizations:
        if viz_type == 'voxel':
            print("  Генерация воксельной визуализации...")
            simulator.visualize(filename=f"{base_filename}_voxel.png")
        
        if viz_type == 'point':
            print("  Генерация визуализации облака точек...")
            simulator.visualize_point_cloud(filename=f"{base_filename}_point_cloud.png")
        
        if viz_type == 'slice':
            print("  Генерация визуализации срезов...")
            simulator.visualize_slices(filename=f"{base_filename}_slices.png")
    
    # Пытаемся сгенерировать визуализацию предельной формы (требуется scikit-image)
    try:
        from skimage import measure
        print("  Генерация визуализации предельной формы...")
        simulator.visualize_limit_shape(filename=f"{base_filename}_limit_shape.png")
    except ImportError:
        print("  Пропуск визуализации предельной формы (scikit-image не установлен)")
    
    print("Готово!")
    

if __name__ == "__main__":
    main() 