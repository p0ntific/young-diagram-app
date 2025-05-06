#!/usr/bin/env python3
"""
Скрипт для запуска 2D симуляций диаграмм Юнга.
"""
import os
import argparse
import logging
from diagrams2d import DiagramSimulator2D

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """
    Основная функция для запуска 2D симуляций диаграмм Юнга.
    """
    parser = argparse.ArgumentParser(description='Запуск 2D симуляций диаграмм Юнга')
    parser.add_argument('--alpha', type=float, default=1.0,
                      help='Степенной параметр для управления поведением роста (по умолчанию: 1.0)')
    parser.add_argument('--steps', type=int, default=1000,
                      help='Количество шагов для каждой симуляции (по умолчанию: 1000)')
    parser.add_argument('--runs', type=int, default=10,
                      help='Количество запусков симуляции (по умолчанию: 10)')
    parser.add_argument('--output-dir', type=str, default='results_2d',
                      help='Директория для сохранения выходных файлов (по умолчанию: results_2d)')
    parser.add_argument('--save-state', action='store_true',
                      help='Сохранить состояние симуляции для возможности продолжения')
    
    args = parser.parse_args()
    
    # Проверка валидности аргументов
    if args.alpha <= 0:
        logger.error("Параметр alpha должен быть положительным числом")
        return
    if args.steps <= 0:
        logger.error("Количество шагов должно быть положительным числом")
        return
    if args.runs <= 0:
        logger.error("Количество запусков должно быть положительным числом")
        return
    
    try:
        # Создаем выходную директорию, если она не существует
        os.makedirs(args.output_dir, exist_ok=True)
        
        logger.info(f"Запуск 2D симуляций диаграмм Юнга с alpha={args.alpha}")
        logger.info(f"Шагов на симуляцию: {args.steps}")
        logger.info(f"Количество запусков: {args.runs}")
        
        # Создаем и запускаем симулятор
        simulator = DiagramSimulator2D()
        simulator.simulate(n_steps=args.steps, alpha=args.alpha, runs=args.runs)
        
        # Базовое имя файла для выходных данных
        base_filename = f"{args.output_dir}/young_diagram_2d_alpha_{args.alpha}"
        
        # Сохраняем результаты
        logger.info(f"Сохранение результатов в {args.output_dir}/...")
        
        # Сохраняем количество ячеек в файл
        simulator.save_cells(f"{base_filename}_cells.txt")
        
        # Сохраняем состояние симуляции, если запрошено
        if args.save_state:
            simulator.save_state(f"{base_filename}_state.pkl")
            logger.info(f"Состояние симуляции сохранено в {base_filename}_state.pkl")
        
        # Генерируем визуализации
        logger.info("Генерация визуализаций...")
        
        # Накопленная диаграмма
        simulator.visualize(filename=f"{base_filename}_heatmap.png")
        
        # Предельная форма
        simulator.limit_shape_visualize(filename=f"{base_filename}_limit_shape.png")
        
        logger.info("Готово!")
    
    except Exception as e:
        logger.error(f"Произошла ошибка при выполнении симуляции: {str(e)}")
        

if __name__ == "__main__":
    main()
